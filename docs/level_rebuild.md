# Reconstruction d'urgence du niveau Aincrad

## Pourquoi ce script existe

Le niveau de travail du projet Aincrad (`/Temp/Untitled_1` dans l'editeur, ou
tout niveau qui l'aurait remplace depuis) contient tout le placement du
monde : terrain PCG, ville de depart, tour du labyrinthe, silhouette
d'Aincrad, ennemis, boss, porte de progression, PlayerStart et GameMode.

Ce niveau **n'a jamais ete sauvegarde sur disque**. Il n'existe a ce jour
aucun outil MCP (plugin officiel Epic pilote depuis Claude Code) permettant
de faire l'equivalent d'un "Save Level As" : le placement d'acteurs ne vit
qu'en memoire dans l'editeur. Un crash de l'editeur a deja fait perdre une
fois l'integralite de ce placement en cours de session — il a fallu tout
reconstruire a la main en rejouant deux scripts Python ecrits dans un dossier
temporaire, donc non versionnes et non recuperables si la machine change.

`ue_tools/rebuild_level.py` consolide ces deux scripts de secours en un seul
script propre, versionne dans le depot, pour ne plus jamais dependre d'un
dossier temporaire en cas de nouveau crash.

## Comment l'utiliser

Ce script n'est pas un executable Python autonome : il appelle une fonction
`execute_tool(tool_name, json_args)` qui n'existe que dans le contexte du
pont MCP Unreal. Pour l'utiliser :

1. Ouvrir une session Claude Code dans ce depot, avec le plugin MCP Unreal
   actif (l'editeur Unreal doit etre ouvert, avec le serveur MCP demarre —
   voir la section MCP de `CLAUDE.md` a la racine pour le detail de la
   configuration, meme si ce fichier decrit un autre projet).
2. Faire evaluer le contenu de `ue_tools/rebuild_level.py` par l'outil MCP
   d'execution Python cote editeur (celui qui fournit `execute_tool` dans
   son contexte d'execution).
3. Appeler `run()`. Le script reconstruit l'integralite du placement du
   Floor 01 : ville, tour du labyrinthe, silhouette d'Aincrad, spawn +
   execution du graphe PCG du terrain, 6 ennemis, le boss, la porte de
   progression liee au boss, le repositionnement du PlayerStart et
   l'assignation du GameMode par defaut dans les WorldSettings.

Le script suppose un niveau vide (ou en tout cas ne contenant pas deja ces
acteurs) : le relancer sur un niveau qui les contient deja creera des
doublons. Les chemins d'objet fixes vers `PlayerStart` et `WorldSettings`
(`PLAYER_START_PATH`, `WORLD_SETTINGS_PATH` en tete de fichier) correspondent
au niveau `/Temp/Untitled_1` d'origine ; s'ils ont change (par exemple apres
un "Save Level As" vers un niveau nomme), il faut les adapter avant
d'appeler `run()`.

## Bug decouvert cette session : collision des entites PCG

Les entites spawnees par le graphe PCG (`TerrainMeshSpawner`, meshes
instancies de terrain) ont **par defaut** `bodyInstance.collisionEnabled =
NoCollision`.

Piege constate : modifier le descriptor du graphe PCG (par exemple pour
activer la collision sur les meshes generes) puis relancer
`PCGToolset.PCGToolset.ExecuteGraphInstance` **ne met pas a jour** la
collision des composants ISM (Instanced Static Mesh) deja presents dans le
niveau. Le graphe se re-execute, mais les instances existantes gardent leurs
anciennes proprietes de collision — le changement de descriptor n'est pris
en compte que pour un composant recree de zero, ce qui n'est pas garanti
par une simple re-execution du graphe.

**Solution qui fonctionne** : patcher directement les proprietes du
composant vivant, apres coup, via :

```python
execute("editor_toolset.toolsets.object.ObjectTools.set_properties", {
    "instance": component,  # ref vers le composant ISM du niveau
    "values": json.dumps({
        "collisionEnabled": "QueryAndPhysics",
        "collisionProfileName": "BlockAll",
    }),
})
```

A retenir : pour la collision des entites PCG, ne pas compter sur une
re-execution du graphe apres modification du descriptor — patcher le
composant deja instancie dans le niveau.

## Rappel important

Ce script est un **filet de securite**, pas un remplacement d'une vraie
sauvegarde. Des qu'un "Save Level As" manuel devient possible dans
l'editeur (action humaine, aucun outil MCP ne le fait aujourd'hui), il faut
le faire pour fixer le niveau sur disque une bonne fois pour toutes. Ce
script ne doit servir qu'en cas de perte du placement (crash, niveau non
sauvegarde) et tant qu'aucun outil MCP de sauvegarde de niveau n'existe.

## Note de consolidation

Les deux scripts source (`rebuild_world.py` et `rebuild_world_part2.py`,
ecrits dans un dossier temporaire pendant la session de reconstruction)
n'etaient pas strictement equivalents :

- `rebuild_world.py` reconstruisait le niveau complet depuis zero, y compris
  le spawn du graphe PCG via `SpawnGraphInstance`.
- `rebuild_world_part2.py` etait une reprise partielle ecrite en cours de
  session : elle ne refaisait que la fin de la sequence (ennemis, boss,
  porte, PlayerStart, GameMode) et re-attachait le graphe PCG a un acteur
  **deja present** dans le niveau, via un chemin d'objet code en dur obtenu
  en inspectant le niveau apres le crash — un chemin qui n'existe que dans
  le contexte exact de cette session-la.

`ue_tools/rebuild_level.py` reprend la version complete et autonome
(`rebuild_world.py`), reorganisee en fonctions, sans aucune valeur numerique
modifiee. La variante de reprise partielle de `rebuild_world_part2.py` n'a
pas ete reportee telle quelle car son chemin code en dur vers un acteur PCG
preexistant ne serait pas fiable pour une reconstruction depuis un niveau
vide — l'objectif de ce script.
