# CLAUDE.md — Outil de génération de personnages 3D par IA (style Genshin Impact)

> Ce fichier décrit l'intégralité du projet pour toute session Claude Code qui travaille
> dessus. Objectif : reconstruire en **local et gratuitement** l'équivalent de Meshy
> (image/texte → mesh 3D texturé → riggé → exportable jeu), avec une spécialisation
> rendu **cel-shading style Genshin Impact**.

---

## 1. Objectif du projet

Développer un outil de bureau (local, hors-ligne, sans coût par génération) qui prend en
entrée une description ou une image de personnage et produit en sortie un **personnage 3D
game-ready** : mesh propre + textures + squelette + (option) shader toon façon Genshin.

Le pipeline cible reproduit ce que fait Meshy, étape par étape :

```
[texte] --(SD/Flux + LoRA Genshin)--> [concept image vues multiples]
        --(Hunyuan3D 2.1)----------> [mesh + texture PBR]
        --(UniRig)------------------> [squelette + skinning]
        --(Blender headless)--------> [cleanup topologie + cel-shader + export GLB/FBX]
```

Livrable final : un personnage exporté en `.glb` (et `.fbx`), importable dans Unity /
Unreal / Godot, avec un look toon optionnel.

---

## 2. Contraintes matérielles (CRITIQUE — ne pas ignorer)

- **GPU : NVIDIA RTX 2070** — **8 Go VRAM**, architecture **Turing (compute capability 7.5)**.
- **OS : Windows 11**, shell **PowerShell**.
- Conséquences directes sur l'architecture du code :
  - **8 Go = budget VRAM serré.** Les modèles doivent être chargés **un à la fois** puis
    **déchargés** (`del model; torch.cuda.empty_cache()`) entre chaque étape du pipeline.
    Jamais deux gros modèles en VRAM simultanément.
  - **Turing ne supporte pas `bf16` nativement** → utiliser **`fp16`** partout. Éviter les
    chemins de code qui forcent `bfloat16`.
  - **Flash-Attention 2** ne fonctionne pas (ou mal) sur Turing → désactiver / utiliser
    l'attention standard ou `xformers` (qui supporte Turing).
  - **TRELLIS.2-4B (24 Go) est HORS budget.** Ne pas l'utiliser. Modèle 3D retenu :
    **Hunyuan3D 2.1** (génération de forme dès ~6 Go, texture en étape séparée).
  - Activer les modes économes : `enable_model_cpu_offload`, `enable_sequential_cpu_offload`,
    VAE tiling/slicing pour Stable Diffusion.
  - Prévoir un **fallback CPU** lent pour les étapes légères (cleanup Blender) mais jamais
    pour la génération 3D.

---

## 3. Stack technique (100 % open source / gratuit)

| Étape | Outil / modèle | Rôle | Notes 8 Go |
|---|---|---|---|
| 0. Orchestration | **ComfyUI** (phase test) puis **script Python** (outil final) | enchaîner les étapes | — |
| 1. Concept image | **Stable Diffusion 1.5 / SDXL / Flux** + **LoRA Genshin** (Civitai) | générer le concept multi-vues | SD1.5/SDXL OK ; Flux lourd, offload CPU |
| 2. Image → 3D | **Hunyuan3D 2.1** (Tencent) | mesh + texture PBR | fp16, offload, modèle de référence |
| 3. Auto-rigging | **UniRig** (VAST-AI / Tsinghua) | squelette + skinning weights | humanoïde |
| 4. Cleanup + export + shader | **Blender 4.x** (mode headless `--background --python`) | retopo légère, toon shader, export | CPU OK |
| (alt rig) | **Mixamo** (gratuit, en ligne) | fallback rig humanoïde | non-local |

Langage : **Python 3.10/3.11**. Frameworks : PyTorch (CUDA 12.x build), diffusers,
trimesh, gradio (UI).

---

## 4. Pourquoi le style Genshin demande une étape custom

Aucun de ces modèles ne sort du cel-shading nativement (ils produisent du PBR « réaliste »).
Le look Genshin = pipeline NPR spécifique à ajouter nous-mêmes en étape 4 :

- Cel-shading à 2-3 tons (rampe de lumière custom).
- **Outlines** (contours) via inverted-hull mesh ou shader, pas via la géométrie.
- Textures plates, ombres partiellement peintes dans la texture.
- Séparation propre des matériaux : peau / cheveux / yeux / vêtements.

En pratique : viser des **concepts d'entrée déjà très « anime/plats »** (LoRA Genshin en
étape 1) donne de bien meilleurs meshes que de partir d'une image réaliste.

---

## 5. Structure du dépôt (à créer)

```
recherches 3d perso/
├── CLAUDE.md                  # ce fichier
├── README.md                  # quickstart utilisateur
├── requirements.txt           # dépendances pip (hors PyTorch, installé à part)
├── environment.md             # notes d'install env (CUDA, versions)
├── config.yaml                # chemins modèles, presets VRAM, options
├── models/                    # poids téléchargés (gitignore)
│   ├── sd/                    # checkpoints + LoRA Genshin
│   ├── hunyuan3d/
│   └── unirig/
├── src/
│   ├── pipeline.py            # orchestrateur principal (enchaîne les étapes)
│   ├── step1_concept.py       # texte -> image (diffusers)
│   ├── step2_image_to_3d.py   # image -> mesh+texture (Hunyuan3D)
│   ├── step3_rig.py           # mesh -> riggé (UniRig)
│   ├── step4_blender.py       # cleanup + cel-shader + export (lance Blender headless)
│   ├── vram.py                # helpers load/unload + empty_cache
│   └── ui.py                  # interface Gradio (bouton "générer")
├── blender/
│   ├── cleanup_export.py      # script exécuté DANS Blender (--background --python)
│   └── toon_material.py       # création du shader cel-shading + outlines
├── outputs/                   # personnages générés (gitignore)
└── tests/
    └── test_smoke.py          # vérifie que chaque étape charge sans OOM
```

---

## 6. Roadmap (phases de développement)

### Phase 0 — Environnement (prérequis)
- Installer **Python 3.11**, **Git**, **CUDA-compatible PyTorch** (build cu12x), **Blender 4.x**.
- Vérifier `torch.cuda.is_available()` → True, et `torch.cuda.get_device_name()` → RTX 2070.
- Créer le venv, `requirements.txt`.

### Phase 1 — Valider la qualité AVANT de coder (ne pas sauter)
- Installer **ComfyUI** + custom node **Hunyuan3D**.
- Générer manuellement 2-3 persos depuis une image pour juger la qualité sur 8 Go.
- **Décision GO/NO-GO** : si la qualité convient, continuer ; sinon ajuster (résolution, modèle).

### Phase 2 — Étape 2 isolée (cœur de l'outil)
- `step2_image_to_3d.py` : charger Hunyuan3D en fp16 + offload, image → `.obj/.glb` texturé.
- Gérer le déchargement VRAM. Tester l'absence d'OOM.

### Phase 3 — Étape 1 (concept)
- `step1_concept.py` : SD/SDXL + LoRA Genshin → image de référence (idéalement vues face/dos).

### Phase 4 — Étape 3 (rigging)
- Intégrer **UniRig** : mesh → squelette + skinning. Fallback documenté vers Mixamo.

### Phase 5 — Étape 4 (Blender headless)
- `blender/cleanup_export.py` : import, nettoyage, **toon_material.py** (cel-shader + outlines),
  export `.glb` + `.fbx`.

### Phase 6 — Orchestration + UI
- `pipeline.py` enchaîne 1→2→3→4 avec gestion VRAM séquentielle.
- `ui.py` : interface Gradio « un prompt / une image = un perso ».

### Phase 7 — Spécialisation Genshin + presets
- Affiner le shader, les presets de matériaux par zone, presets VRAM dans `config.yaml`.

---

## 7. Règles de développement (pour Claude Code)

- **VRAM d'abord** : toute nouvelle étape doit charger son modèle, faire le travail, puis
  libérer (`vram.py` centralise ce pattern). Jamais deux modèles lourds en même temps.
- **fp16 uniquement** (Turing), pas de `bf16`. Désactiver flash-attn ; préférer `xformers`.
- Tester chaque étape **isolément** (`tests/test_smoke.py`) avant de l'intégrer au pipeline.
- Les poids de modèles vont dans `models/` et sont **gitignorés** (lourds). Documenter les
  liens de téléchargement dans `environment.md`, pas committer les poids.
- Chemins et options dans `config.yaml`, pas en dur dans le code.
- Code commenté en français (cohérent avec ce projet) ; messages d'erreur explicites sur l'OOM.
- Commandes shell = **PowerShell** (Windows). Activer le venv via `.\.venv\Scripts\Activate.ps1`.

---

## 8. Commandes utiles (à compléter au fil du dev)

```powershell
# Créer / activer l'environnement
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# PyTorch CUDA (adapter la version cu12x au driver installé)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Dépendances projet
pip install -r requirements.txt

# Vérifier le GPU
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

# Lancer une étape isolée (exemple)
python src/step2_image_to_3d.py --input outputs/concept.png --out outputs/mesh.glb

# Blender headless (cleanup + export)
& "C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python blender/cleanup_export.py -- outputs/mesh.glb

# Lancer l'UI complète
python src/ui.py
```

---

## 9. Sources / références

- Hunyuan3D 2.1 (Tencent) — modèle image/texte → 3D, accessible en VRAM réduite.
- TRELLIS / TRELLIS.2 (Microsoft) — qualité supérieure mais 24 Go (hors budget RTX 2070).
- UniRig (VAST-AI / Tsinghua, SIGGRAPH 2025) — https://github.com/VAST-AI-Research/UniRig
- ComfyUI — orchestration node-based pour la phase de test.
- Civitai — LoRA / checkpoints style Genshin Impact pour l'étape concept.
- Blender 4.x — cleanup, toon shader, export (scriptable Python, headless).

---

## 10. État actuel du projet

- [x] Recherche & choix de la stack (RTX 2070 / 8 Go → Hunyuan3D, pas TRELLIS.2)
- [x] **Phase 0 — environnement** : Python 3.11.9, venv, PyTorch 2.5.1+cu121 (CUDA OK
      sur RTX 2070), Blender 5.1, deps installées. `transformers` épinglé à **4.49.0**
      (la 5.x renomme les couches ViT → checkpoint TripoSR incompatible).
- [x] **Étape 2 (image→3D) FONCTIONNELLE** via TripoSR : `tiger_girl.png` →
      mesh 22726 sommets / 45468 faces + couleurs de sommets, en **24 s**, **1,56 Go VRAM**.
      Marching cubes patché torchmcubes→**PyMCubes** (pas de compilation C++).
- [x] **Étape 4 (Blender)** : export GLB + FBX OK ; rendu de prévisualisation multi-angles.
- [ ] Bug mineur : auto-orientation du mesh (le perso sort couché ; rotation appliquée
      mais le repère face/dos est à fiabiliser — voir `blender/preview_render.py`).
- [x] **Étape 1 (concept SD) FONCTIONNELLE** : `step1_concept.py`, SD1.5 fp16 +
      attention/VAE slicing + CPU offload. Image anime générée en **~15 s**. Checkpoint
      et LoRA Genshin configurables dans `config.yaml` (defaut SD1.5 base).
- [x] **Backend Hunyuan3D — FORME FONCTIONNELLE** : `step2 --backend hunyuan3d`
      (`tencent/Hunyuan3D-2mini`, subfolder `hunyuan3d-dit-v2-mini`). Géométrie bien
      plus détaillée que TripoSR, **3,75 Go VRAM**, ~30 s de génération (FlashVDM).
      Texture UV (texgen) = nécessite compiler `custom_rasterizer` (VS Build Tools) →
      repli sur forme seule géré. Deps installées (ninja, pymeshlab, pygltflib…).
- [x] **Étape 3 rigging** : `step3_rig.py` + `docs/rigging.md`. **UniRig BLOQUÉ sur
      Turing** (flash_attn exige Ampere sm_80+ ; conflit transformers 4.51 vs 4.49).
      → Fallback recommandé **Mixamo** (en ligne, gratuit) / **AccuRIG** (local, gratuit).
- [x] **Pipeline complet** : `pipeline.py` enchaîne (prompt|image) → concept → 3D → export.
- [x] **Cel-shader Genshin pour Unreal Engine 5** documenté : `docs/UE5_cel_shader_genshin.md`
      (Unlit + rampe toon + rim + outline inverted-hull). Le moteur cible est **UE5**.
- [x] **Tests de fumée** : `tests/test_smoke.py` — tous OK.
- [x] **Texgen Hunyuan COMPILÉ** : `custom_rasterizer` (CUDA, sm_75) + `differentiable_renderer`
      built et installés. Pile : VS Build Tools 2022 + **CUDA Toolkit 12.6** (12.1 refusée par
      le STL de MSVC 14.44 → STL1002 ; 12.6 OK, majeure 12 = match torch cu121).
      Flags clés : `-allow-unsupported-compiler`, `TORCH_CUDA_ARCH_LIST=7.5`. Patch
      `trust_remote_code=True` dans `multiview_utils.py`. Voir `build_texgen.bat`.
- [x] **MAIS texture Hunyuan NON VIABLE sur 8 Go** : la génération de texture demande
      **16 Go+ VRAM** (doc officielle). Sur 8 Go → thrashing VRAM, le bake ne finit pas
      (testé 2048 puis 1024, >60 min sans résultat). Décision : **forme Hunyuan seule**,
      texture faite dans Unreal. Piste future : fork **Hunyuan3D-2GP** (mmgp, ~6 Go).
- [ ] Rigging automatique 100 % local sur Turing (UniRig patché sans flash-attn, ou autre).
- [ ] Améliorer le prompt concept (sujet unique centré) ou checkpoint anime + LoRA Genshin.
- [ ] Fiabiliser le face/dos de l'auto-orientation (le debout est OK).
- [ ] UI Gradio (conflit hub<->gradio : gradio 6.19 veut hub≥1.2, transformers 4.49 veut hub<1).
- [x] **Unreal Engine 5.8 installé + projet créé** : `ue_project/GenshinCharacterViewer/`
      (Blueprint-only, `EngineAssociation": "5.8"`). C'est la cible d'import des `.glb/.fbx`
      de `outputs/` pour appliquer le cel-shader Genshin (`docs/UE5_cel_shader_genshin.md`).
- [x] **Claude Code ↔ Unreal Editor via MCP (plugin officiel Epic)** :
      `unreal-engine-skills-for-claude-code@claude-plugins-official` installé
      (`claude plugin install ...`, scope user). Côté projet : plugins engine
      `ModelContextProtocol` + `AllToolsets` activés dans le `.uproject`, auto-start
      du serveur (port 8000, `/mcp`) via
      `ue_project/GenshinCharacterViewer/Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`
      (`bAutoStartServer=True` — fichier per-user, non versionné). `.mcp.json` à la
      racine du repo pointe vers `http://127.0.0.1:8000/mcp`. Testé : `LogHttpListener:
      Created new HttpListener on 127.0.0.1:8000` + réponse HTTP 200 sur `initialize`.
      **L'Éditeur doit rester ouvert** pour que les outils MCP (spawn actors, matériaux,
      import mesh, etc.) répondent depuis Claude Code — relancer une session Claude Code
      dans ce dossier après le premier lancement de l'éditeur pour que `.mcp.json` soit pris
      en compte. Nécessite Git Bash sur le PATH pour le hook de contexte du plugin (déjà OK).
      Note : premier lancement a affiché une boîte de dialogue Windows bloquante
      (redistribuable VC++ obsolète) → relancer avec `-unattended` évite le blocage.

> Mettre à jour cette checklist à chaque avancée.
