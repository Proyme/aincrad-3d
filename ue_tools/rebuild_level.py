# -*- coding: utf-8 -*-
"""
rebuild_level.py — script de reprise apres sinistre pour le niveau Aincrad.

CONTEXTE
--------
Le niveau actuellement ouvert dans l'editeur Unreal (`/Temp/Untitled_1`, ou tout
niveau qui l'aurait remplace) n'est PAS sauvegarde sur disque : il n'existe a ce
jour aucun outil MCP permettant de faire l'equivalent d'un "Save Level As" depuis
Claude Code. Tout le placement d'acteurs (terrain PCG, ville, tour, ennemis,
boss, porte de progression) ne vit qu'en memoire dans l'editeur. Un crash de
l'editeur a deja fait perdre integralement ce placement une fois.

Ce script reconstruit ce placement a l'identique. Il consolide deux scripts
ecrits dans un dossier temporaire (`rebuild_world.py` et
`rebuild_world_part2.py`) qui ont servi a reconstruire le niveau a la main
apres le crash. Aucune valeur numerique (positions, dimensions, rayons,
tags, chemins d'assets) n'a ete modifiee par rapport aux scripts source.

UTILISATION
-----------
Ce fichier n'est PAS un script Python autonome : il s'execute a l'interieur
d'une session Claude Code qui a le pont MCP Unreal actif, c'est-a-dire un
contexte ou la fonction `execute_tool(tool_name, json_args)` est deja fournie
(ex: evalue ce fichier via l'outil MCP d'execution Python, puis appelle
`run()`). Sans ce pont, `execute_tool` n'existe pas et le script ne peut pas
fonctionner tel quel.

A n'utiliser que si le niveau a perdu son placement d'acteurs (apres un crash,
par exemple) et tant qu'aucun outil "Save Level" n'existe cote MCP. Ce script
est un FILET DE SECURITE, pas un remplacement d'une sauvegarde propre : des
qu'un "Save Level As" manuel devient possible dans l'editeur, il faut le faire.

NOTE SUR LA CONSOLIDATION
--------------------------
`rebuild_world.py` construisait le niveau complet depuis un niveau vide
(ville, tour du labyrinthe, silhouette d'Aincrad, spawn + execution du graphe
PCG, ennemis, boss, porte, PlayerStart, GameMode). `rebuild_world_part2.py`
etait une variante de reprise partielle ecrite en cours de session : elle
ne re-executait que la fin de la sequence (ennemis, boss, porte, PlayerStart,
GameMode) et re-attachait le graphe PCG a un acteur DEJA PRESENT dans le
niveau via un chemin d'objet code en dur (obtenu apres inspection du niveau
post-crash), au lieu de le spawner. Ce chemin en dur n'existe que si cet
acteur precis a deja ete cree pendant la meme session : il n'est pas
reutilisable pour une reconstruction depuis un niveau vide.

Ce script consolide la version COMPLETE (`rebuild_world.py`) : elle spawn le
graphe PCG via `SpawnGraphInstance` avant de l'executer, ce qui la rend
autonome et rejouable depuis un niveau totalement vide. La logique de reprise
partielle de `rebuild_world_part2.py` (re-attache a un acteur PCG existant
par chemin code en dur) n'a pas ete reportee ici car elle ne serait pas
fiable hors du contexte exact ou elle a ete ecrite.

BUG A NE PAS REPRODUIRE (decouvert cette session)
---------------------------------------------------
Les entites spawnees par le graphe PCG (`TerrainMeshSpawner`) ont par defaut
`bodyInstance.collisionEnabled = NoCollision`. Modifier le descriptor du
graphe PCG puis relancer `ExecuteGraphInstance` NE met PAS a jour la
collision des composants ISM deja presents dans le niveau : il faut patcher
directement les proprietes du composant vivant via
`editor_toolset.toolsets.object.ObjectTools.set_properties` avec
`{"collisionEnabled": "QueryAndPhysics", "collisionProfileName": "BlockAll"}`
sur l'instance du composant. Voir `docs/level_rebuild.md` pour le detail.
"""

import json
import math

# ---------------------------------------------------------------------------
# Constantes (identiques aux scripts source — ne pas modifier ces valeurs)
# ---------------------------------------------------------------------------

MAT = {
    "grass": {"refPath": "/Game/Aincrad/Materials/MI_Grass.MI_Grass"},
    "cliff": {"refPath": "/Game/Aincrad/Materials/MI_Cliff.MI_Cliff"},
    "wall": {"refPath": "/Game/Aincrad/Materials/MI_Wall.MI_Wall"},
    "roof": {"refPath": "/Game/Aincrad/Materials/MI_Roof.MI_Roof"},
    "tower": {"refPath": "/Game/Aincrad/Materials/MI_TowerStone.MI_TowerStone"},
    "path": {"refPath": "/Game/Aincrad/Materials/MI_Path.MI_Path"},
}
Z_BASE = 20000.0
R = 70000.0

ACTOR_CLASS = {"refPath": "/Script/Engine.Actor"}
ENEMY_CLASS = {"refPath": "/Game/Aincrad/Blueprints/BP_Enemy.BP_Enemy_C"}
GATE_CLASS = {"refPath": "/Game/Aincrad/Blueprints/BP_FloorGate.BP_FloorGate_C"}
GM_CLASS = {"refPath": "/Game/Aincrad/Blueprints/BP_AincradGameMode.BP_AincradGameMode_C"}

# Chemins d'objets fixes vers des acteurs qui existent deja nativement dans
# tout niveau Unreal (PlayerStart, WorldSettings) — presents sur le niveau
# `/Temp/Untitled_1` d'origine. Si le niveau courant est un autre niveau
# (ex: apres un "Save Level As" ulterieur), adapter ces deux chemins avant
# d'appeler run().
PLAYER_START_PATH = {
    "refPath": "/Temp/Untitled_1.Untitled_1:PersistentLevel.PlayerStart_UAID_F02F74551BF5599B01_1153002503"
}
WORLD_SETTINGS_PATH = {"refPath": "/Temp/Untitled_1.Untitled_1:PersistentLevel.WorldSettings"}

PCG_GRAPH = {"refPath": "/Game/Aincrad/PCG/PCG_Floor01_Terrain.PCG_Floor01_Terrain"}


# ---------------------------------------------------------------------------
# Helpers bas niveau (appels au pont MCP)
# ---------------------------------------------------------------------------

def execute(tool, args):
    """Appelle un outil MCP Unreal et renvoie sa reponse deserialisee."""
    return execute_tool(tool, json.dumps(args))


def hash01(i, salt=0.0):
    """Pseudo-alea deterministe [0, 1) — reproduit la variation organique
    des batiments de la ville sans dependre d'un generateur externe."""
    v = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return v - math.floor(v)


def spawn_actor(actor_type, name, x, y, z):
    """Spawn un acteur vide a une position monde donnee et renvoie sa ref."""
    return execute("editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_class", {
        "actor_type": actor_type, "name": name,
        "xform": {"location": {"x": x, "y": y, "z": z}},
    })["returnValue"]


def add_cube(actor, name, dx, dy, dz, lx, ly, lz):
    """Ajoute un composant cube primitif a un acteur (position locale)."""
    return execute("editor_toolset.toolsets.primitive.PrimitiveTools.add_cube", {
        "actor": actor, "name": name,
        "dimensions": {"x": dx, "y": dy, "z": dz},
        "local_transform": {"location": {"x": lx, "y": ly, "z": lz}},
    })["returnValue"]


def add_cylinder(actor, name, radius, height, lx, ly, lz):
    """Ajoute un composant cylindre primitif a un acteur (position locale)."""
    return execute("editor_toolset.toolsets.primitive.PrimitiveTools.add_cylinder", {
        "actor": actor, "name": name, "radius": radius, "height": height,
        "local_transform": {"location": {"x": lx, "y": ly, "z": lz}},
    })["returnValue"]


def add_cone(actor, name, radius, height, lx, ly, lz):
    """Ajoute un composant cone primitif a un acteur (position locale)."""
    return execute("editor_toolset.toolsets.primitive.PrimitiveTools.add_cone", {
        "actor": actor, "name": name, "radius": radius, "height": height,
        "local_transform": {"location": {"x": lx, "y": ly, "z": lz}},
    })["returnValue"]


def set_mat(component, mat_key):
    """Applique un materiau (par cle logique dans MAT) a un composant."""
    execute("editor_toolset.toolsets.object.ObjectTools.set_properties", {
        "instance": component,
        "values": json.dumps({"overrideMaterials": [MAT[mat_key]]}),
    })


def set_folder(actor, folder):
    """Range un acteur dans un dossier de l'Outliner (organisation)."""
    execute("editor_toolset.toolsets.scene.SceneTools.set_actor_folder", {
        "actor": actor, "folder_path": folder,
    })


def tag(actor, t):
    """Ajoute un gameplay tag a un acteur (utilise par les BP de gameplay)."""
    execute("editor_toolset.toolsets.actor.ActorTools.add_tag", {"actor": actor, "tag": t})


# ---------------------------------------------------------------------------
# Etapes de reconstruction (une fonction par "bloc" du niveau)
# ---------------------------------------------------------------------------

def build_town_of_beginnings(counts):
    """Reconstruit la ville de depart (Floor 01) : anneaux de batiments
    disperses autour du centre, avec murs + toits en cone."""
    town_actor = spawn_actor(ACTOR_CLASS, "Floor01_TownOfBeginnings", 0, 0, Z_BASE)
    set_folder(town_actor, "Aincrad/Floor01/Town")
    n_buildings = 24
    for i in range(n_buildings):
        ring = i % 3
        radius = 6000.0 + ring * 9000.0 + hash01(i, 2.1) * 4000.0
        angle = (i / n_buildings) * 2.0 * math.pi + hash01(i, 5.7) * 0.6
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        w = 2200.0 + hash01(i, 1.3) * 1400.0
        d = 2200.0 + hash01(i, 4.2) * 1400.0
        h = 2800.0 + hash01(i, 8.8) * 2200.0
        wall = add_cube(town_actor, f"Bldg_{i}_Wall", w, d, h, x, y, h / 2.0)
        set_mat(wall, "wall")
        roof = add_cone(town_actor, f"Bldg_{i}_Roof", max(w, d) * 0.75, h * 0.6, x, y, h + h * 0.3)
        set_mat(roof, "roof")
    counts["buildings"] = n_buildings
    return town_actor


def build_labyrinth_tower(plateau_r):
    """Reconstruit la tour du labyrinthe du Floor 01 (corps + chapeau)."""
    lab_actor = spawn_actor(ACTOR_CLASS, "Floor01_LabyrinthTower", 0, plateau_r * 0.92, Z_BASE)
    set_folder(lab_actor, "Aincrad/Floor01/Labyrinth")
    body = add_cylinder(lab_actor, "LabyrinthBody", 4500.0, 16000.0, 0, 0, 8000.0)
    set_mat(body, "tower")
    cap = add_cylinder(lab_actor, "LabyrinthCap", 3200.0, 3000.0, 0, 0, 17500.0)
    set_mat(cap, "tower")
    return lab_actor


def build_aincrad_silhouette():
    """Reconstruit la silhouette generale de la tour Aincrad : bandes de
    cylindres empiles qui retrecissent avec l'altitude."""
    tower_actor = spawn_actor(ACTOR_CLASS, "Aincrad_Silhouette", 0, 0, Z_BASE)
    set_folder(tower_actor, "Aincrad/Silhouette")
    n_bands = 16
    band_h = 8000.0
    gap = 4000.0
    for i in range(n_bands):
        t = i / float(n_bands - 1)
        band_r = R * (0.9 - 0.75 * t)
        z = gap + i * band_h + band_h / 2.0
        comp = add_cylinder(tower_actor, f"Band_{i}", band_r, band_h * 1.02, 0, 0, z)
        set_mat(comp, "tower")
    return tower_actor


def build_pcg_terrain():
    """Spawn l'instance de graphe PCG du terrain Floor 01 et l'execute.

    Autonome depuis un niveau vide (contrairement a la variante de reprise
    partielle qui re-attachait un acteur PCG deja existant par chemin code
    en dur — voir la note de consolidation en tete de fichier)."""
    pcg_actor = execute("PCGToolset.PCGToolset.SpawnGraphInstance", {
        "graph": PCG_GRAPH, "name": "Floor01_PCG_Terrain",
        "transform": {"location": {"x": 0, "y": 0, "z": Z_BASE},
                      "rotation": {"pitch": 0, "yaw": 0, "roll": 0},
                      "scale": {"x": 25, "y": 25, "z": 10}},
        "jsonParams": "{}",
    })["returnValue"]
    set_folder(pcg_actor, "Aincrad/Floor01/Terrain_PCG")
    tag(pcg_actor, "Floor01")
    exec_result = execute("PCGToolset.PCGToolset.ExecuteGraphInstance", {"pCGVolume": pcg_actor})
    return pcg_actor, exec_result


def build_enemies(plateau_r):
    """Reconstruit les 6 ennemis standards du Floor 01, repartis en cercle."""
    enemies = []
    for i in range(6):
        angle = (i / 6.0) * 2.0 * math.pi
        x = math.cos(angle) * 25000.0
        y = math.sin(angle) * 25000.0
        e = spawn_actor(ENEMY_CLASS, f"Enemy_{i}", x, y, Z_BASE + 100.0)
        set_folder(e, "Aincrad/Floor01/Enemies")
        tag(e, "Floor01")
        comp = add_cube(e, "Body", 1200, 1200, 2000, 0, 0, 1000)
        set_mat(comp, "tower")
        enemies.append(e)
    return enemies


def build_boss(plateau_r):
    """Reconstruit le boss de fin de Floor 01 (gardien du labyrinthe)."""
    boss = spawn_actor(ENEMY_CLASS, "Boss_LabyrinthGuardian", 0, plateau_r * 0.92, Z_BASE + 100.0)
    set_folder(boss, "Aincrad/Floor01/Labyrinth")
    tag(boss, "Floor01")
    tag(boss, "Boss_Floor01")
    execute("editor_toolset.toolsets.object.ObjectTools.set_properties", {
        "instance": boss, "values": json.dumps({"bIsBoss": True, "Health": 500.0, "MaxHealth": 500.0}),
    })
    boss_comp = add_cube(boss, "Body", 3000, 3000, 5000, 0, 0, 2500)
    set_mat(boss_comp, "roof")
    return boss


def build_floor_gate(plateau_r, boss):
    """Reconstruit la porte de progression du Floor 01, liee au boss."""
    gate = spawn_actor(GATE_CLASS, "Floor01_LabyrinthGate", 0, plateau_r * 0.92 + 4500.0, Z_BASE + 100.0)
    set_folder(gate, "Aincrad/Floor01/Labyrinth")
    tag(gate, "Floor01")
    execute("editor_toolset.toolsets.object.ObjectTools.set_properties", {
        "instance": gate, "values": json.dumps({"BossRef": boss}),
    })
    barrier = add_cube(gate, "Barrier", 400, 4000, 3000, 0, 0, 1500)
    set_mat(barrier, "cliff")
    return gate


def configure_player_start_and_gamemode():
    """Repositionne le PlayerStart natif du niveau et assigne le GameMode
    par defaut dans les WorldSettings."""
    execute("editor_toolset.toolsets.actor.ActorTools.set_actor_transform", {
        "actor": PLAYER_START_PATH,
        "xform": {"location": {"x": 0, "y": -12000.0, "z": 20200.0}},
        "worldspace": True,
    })
    execute("editor_toolset.toolsets.object.ObjectTools.set_properties", {
        "instance": WORLD_SETTINGS_PATH, "values": json.dumps({"DefaultGameMode": GM_CLASS}),
    })


# ---------------------------------------------------------------------------
# Point d'entree unique
# ---------------------------------------------------------------------------

def run():
    """Reconstruit l'integralite du placement du Floor 01 d'Aincrad dans le
    niveau courant, a l'identique de la session perdue lors du crash.

    A appeler depuis une session Claude Code avec le pont MCP Unreal actif
    (voir docs/level_rebuild.md). Suppose un niveau vide ou ne contenant pas
    deja ces acteurs (sinon des doublons seront crees)."""
    counts = {}
    plateau_r = R * 0.72

    build_town_of_beginnings(counts)
    build_labyrinth_tower(plateau_r)
    build_aincrad_silhouette()

    pcg_actor, exec_result = build_pcg_terrain()

    build_enemies(plateau_r)
    boss = build_boss(plateau_r)
    gate = build_floor_gate(plateau_r, boss)

    configure_player_start_and_gamemode()

    return {"status": "ok", "counts": counts, "boss": boss, "gate": gate, "pcg_exec": exec_result}
