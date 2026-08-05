# Notes d'environnement

Machine : **RTX 2070 (8 Go, Turing)**, Windows 11, PowerShell.

## Versions installées (validées)
- Python **3.11.9** (`%LOCALAPPDATA%\Programs\Python\Python311`)
- PyTorch **2.5.1+cu121** / torchvision 0.20.1 (CUDA OK sur RTX 2070)
- **transformers == 4.49.0** ← ÉPINGLÉ. La 5.x renomme les couches ViT
  (`encoder.layer.*` → `layers.*.q_proj`), ce qui casse le checkpoint TripoSR.
- diffusers 0.38, trimesh 4.12, **PyMCubes 0.1.6** (marching cubes sans compilation)
- Blender **5.1** (`C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`)

## Installation (rappel)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
pip install "transformers==4.49.0"   # downgrade nécessaire pour TripoSR
git clone https://github.com/VAST-AI-Research/TripoSR.git third_party/TripoSR
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git third_party/Hunyuan3D-2
```

## Patch TripoSR (déjà appliqué)
`third_party/TripoSR/tsr/models/isosurface.py` : remplacement de `torchmcubes`
(compilation C++/CUDA) par **PyMCubes** (wheel précompilé). Évite d'installer
Visual Studio Build Tools.

## Modèles téléchargés (cache HF : `~/.cache/huggingface`)
- `stabilityai/TripoSR` (~1,6 Go) — étape 2 backend triposr.
- `sd-legacy/stable-diffusion-v1-5` (~4 Go) — étape 1 concept.
- `tencent/Hunyuan3D-2*` — à télécharger au 1er run du backend hunyuan3d.

## Conflits connus
- **gradio 6.19** veut `huggingface-hub>=1.2`, mais transformers 4.49 veut `hub<1`
  (on a hub 0.36). → l'UI Gradio devra utiliser une version de gradio compatible
  hub 0.x (ex. `gradio==4.44`) OU isoler l'UI dans un second venv. Sans impact sur
  le pipeline en ligne de commande.

## Backend Hunyuan3D — install (étape suivante, plus lourde)
Le code (`src/step2_image_to_3d.py --backend hunyuan3d`) est prêt. Reste à installer :
```powershell
pip install ninja pybind11 pymeshlab pygltflib opencv-python
```
- **Génération de forme** : fonctionne en Python pur (DiT flow-matching) — viser
  `tencent/Hunyuan3D-2mini` pour tenir dans 8 Go (`enable_flashvdm`).
- **Texture UV (texgen)** : nécessite de compiler `custom_rasterizer` et
  `differentiable_renderer` (dans `third_party/Hunyuan3D-2/hy3dgen/texgen/...`)
  → requiert **Visual Studio Build Tools (C++)** + **CUDA Toolkit**. Tant que ce
  n'est pas compilé, le wrapper exporte la forme **sans** texture (fallback géré).
- Risque : `requirements.txt` de Hunyuan3D laisse `transformers` libre → installer
  ses deps **sans** réinstaller transformers (`--no-deps` ciblé) pour préserver le
  pin 4.49 de TripoSR.

## Lancer
```powershell
.\.venv\Scripts\python.exe tests\test_smoke.py                       # vérifs env
.\.venv\Scripts\python.exe src\pipeline.py --prompt "..." --name p1  # texte -> 3D
.\.venv\Scripts\python.exe src\pipeline.py --image inputs\x.png --name p1 --backend hunyuan3d
```
