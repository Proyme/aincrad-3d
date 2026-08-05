# Générateur de personnages 3D par IA (style Genshin) — local & gratuit

Pipeline local reproduisant Meshy : image → mesh 3D texturé → (rig) → export jeu,
avec spécialisation cel-shading style Genshin Impact.

Voir `CLAUDE.md` pour la doc complète du projet.

## Machine cible
RTX 2070 (8 Go), Windows 11, Python 3.11, Blender 5.1.

## Installation

```powershell
# 1. venv (déjà créé : .venv)
.\.venv\Scripts\Activate.ps1

# 2. PyTorch CUDA (déjà installé)
#    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 3. Dépendances du pipeline
pip install -r requirements.txt

# 4. Modèle image->3D (TripoSR) cloné dans third_party/TripoSR
```

## Premier test (image → mesh 3D)

```powershell
.\.venv\Scripts\python.exe src\step2_image_to_3d.py `
  --input third_party\TripoSR\examples\tiger_girl.png `
  --out outputs\test1.obj

# Export + cel-shader Genshin via Blender
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background `
  --python blender\cleanup_export.py -- outputs\test1.obj outputs\test1 --toon
```

## Pipeline complet (texte → personnage 3D)

```powershell
# depuis un prompt (génère le concept SD puis le mesh puis l'export)
.\.venv\Scripts\python.exe src\pipeline.py --prompt "anime cat girl warrior" --name perso1

# depuis une image existante, backend qualité Hunyuan3D
.\.venv\Scripts\python.exe src\pipeline.py --image inputs\perso.png --name perso1 --backend hunyuan3d
```

## Étapes du pipeline (= ce que fait Meshy)
1. **Concept** — texte → image (`step1_concept.py`, Stable Diffusion). LoRA Genshin configurable. ✅
2. **Image → 3D** — `step2_image_to_3d.py`, backend `triposr` (rapide) ou `hunyuan3d` (qualité). ✅
3. **Rigging** (à venir) — UniRig
4. **Export** — Blender headless → GLB / FBX. ✅
5. **Cel-shader Genshin** — dans **Unreal Engine 5** : voir `docs/UE5_cel_shader_genshin.md`.

## Tests
```powershell
.\.venv\Scripts\python.exe tests\test_smoke.py
```
