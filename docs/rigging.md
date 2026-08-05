# Étape 3 — Rigging (squelette + skinning)

## Situation sur RTX 2070 (Turing) — important

L'option « tout local IA » **UniRig** (VAST-AI/Tripo) est, en l'état, **bloquée sur
cette machine** :

1. **`flash_attn` requis** par UniRig → Flash-Attention exige **Ampere (sm_80+)**.
   La RTX 2070 est **Turing (sm_75)** : flash-attn ne compile pas / ne s'exécute pas.
2. **`transformers==4.51.3`** requis → entre en conflit avec le pin **4.49.0** de
   TripoSR (couches ViT renommées).
3. Dépendances lourdes Windows (`spconv`, `bpy==4.2`, `open3d`, `pyrender`).

→ UniRig nécessiterait : un **venv séparé**, un **patch attention** (remplacer
flash-attn par l'attention standard, à valider), et idéalement un GPU Ampere+.
C'est faisable mais coûteux ; ce n'est pas le chemin recommandé ici.

## Chemin recommandé : Mixamo (gratuit, en ligne, fiable)

Pour un personnage **humanoïde**, Mixamo donne un excellent rig en 2 minutes :

1. Aller sur https://www.mixamo.com (compte Adobe gratuit).
2. **Upload** `outputs/<perso>.fbx` (ou `.obj`).
3. Placer les marqueurs (menton, poignets, coudes, genoux, aine) → auto-rig + skinning.
4. Choisir une animation (idle, walk…) ou « T-Pose ».
5. **Download** en FBX (« With Skin ») → importable Unreal Engine 5.

Avantages : zéro install, skinning de qualité, animations incluses.
Limite : en ligne (pas 100 % local), humanoïde uniquement.

## Alternative locale desktop : AccuRIG (gratuit, Reallusion)

- App Windows gratuite : https://actorcore.reallusion.com/auto-rig
- Drag-drop du mesh → auto-rig humanoïde local, export FBX.
- GUI (non scriptable) mais 100 % local et gratuit.

## Si vraiment UniRig en local (avancé)

```powershell
python -m venv .venv-unirig
.\.venv-unirig\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
# Éditer requirements : retirer flash_attn, patcher le modèle vers l'attention standard
pip install -r third_party\UniRig\requirements.txt   # APRÈS avoir retiré flash_attn
```
→ tester `python -m unirig ...` ; surveiller les appels à flash-attn dans le code.

## Intégration pipeline

`src/step3_rig.py` insère l'étape entre le mesh (étape 2) et l'export (étape 4) :
- tente UniRig s'il est installé,
- sinon affiche les instructions Mixamo/AccuRIG et passe la main (le mesh non riggé
  reste exportable et riggable manuellement ensuite).
