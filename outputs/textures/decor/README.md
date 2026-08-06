# Textures de décor — Aincrad x Cube World

Swatchs de matériaux stylisés générés localement (SD1.5 fp16, `src/gen_textures.py`) pour
habiller les surfaces déjà construites dans Unreal : sol, murs, toits, chemins, coque de la
tour, eau du lac. Style visé : couleurs plates/saturées façon Cube World, **pas** de
photoréalisme, **pas** de bruit type Minecraft — un grain organique léger et propre.

16 images (512x512, 8 matériaux x 2 variantes) + `_generation_log.json` (prompt/négatif/seed
exacts de chaque image, régénéré à chaque run du script).

## Historique — deux passes de génération

**v1** (seed 1000+, prompts avec `"top-down view"` + `"Cube World voxel game art style"`) :
sur 16 images, seules 4 étaient réellement utilisables comme swatchs plats (`herbe_01`,
`bois_clair_01/02`, `toit_terracotta_01`). Les autres ont dérivé vers des **scènes**
isométriques complètes (paysages voxel avec buissons/eau/bâtiments) ou des motifs ornementaux
(mosaïques avec visages) au lieu d'un matériau uniforme — `"voxel"` + `"top-down view"`
poussait trop SD1.5 vers une composition de scène plutôt qu'un gros plan de texture.

**v2** (seed 2000+, prompts actuels) : reformulation du préfixe de style
(`"seamless tileable texture swatch, close-up macro material sample, ... no scene, no
landscape, no objects"`) + négatif renforcé contre les scènes/paysages/mosaïques
(`isometric scene, landscape, terrain, voxel blocks, buildings, trees, ornate carving,
mosaic, ...`). Résultat : **14/16 images utilisables**, nette amélioration de la cohérence
matériau. Ce sont les fichiers actuellement sur disque (v1 a été écrasé par v2, mêmes noms
de fichiers).

## Limitation connue — `eau_01` / `eau_02`

Les deux variantes d'eau ne ressemblent **pas** à de l'eau : SD1.5 les a transformées en
motif de rayures ondulées façon tissu/zébrure (bleu marine/blanc pour `eau_02`, bois strié
pour `eau_01`) plutôt qu'une surface d'eau stylisée. Le négatif qui exclut
`waves, foam, reflections` retire justement les indices visuels qui feraient reconnaître de
l'eau au modèle, sans qu'un mot-clé positif suffisant les remplace. **À refaire** avant usage
dans `MI_Water` — pistes : repartir d'un checkpoint anime/toon (plutôt que SD1.5 base),
autoriser `ripples, reflections` en positif, ou peindre le fallback à la main.

`pierre_noire` est gris foncé/anthracite plutôt que franchement noir (négatif
`beige/tan/ivory` a bien exclu les tons clairs, mais le résultat reste un gris-charbon, pas
un noir profond) — utilisable pour `MI_BlackIron` mais à assombrir en post (courbe/multiply
dans Unreal) si un noir plus marqué est voulu.

## Matériaux

| Fichier | Matériau visé (Unreal) | État |
|---|---|---|
| `herbe_01.png`, `herbe_02.png` | `MI_Grass` — sol de prairie, vert sauge désaturé | OK |
| `pierre_claire_01.png`, `pierre_claire_02.png` | `MI_Path` (rue de la ville) — dalles beige/crème | OK |
| `pierre_sombre_01.png`, `pierre_sombre_02.png` | `MI_TowerStone` (coque Aincrad / tour du Labyrinthe) — ardoise bleu-gris | OK |
| `bois_clair_01.png`, `bois_clair_02.png` | `MI_Wall` (charpente / moulins) — bois miel clair | OK |
| `toit_terracotta_01.png`, `toit_terracotta_02.png` | `MI_Roof` — tuiles terracotta | OK |
| `terre_01.png`, `terre_02.png` | `MI_Path` (chemin) — terre battue brune | OK |
| `pierre_noire_01.png`, `pierre_noire_02.png` | `MI_BlackIron` (nouveau — Black Iron Palace) — pierre sombre mate | OK (gris anthracite, pas noir pur — voir limitation) |
| `eau_01.png`, `eau_02.png` | `MI_Water` (nouveau — lac) — bleu-gris stylisé | **À refaire** (ne ressemble pas à de l'eau) |

## Régénérer

```powershell
.\.venv\Scripts\python.exe src\gen_textures.py --seed-base 3000
```

Options utiles : `--steps`, `--cfg`, `--size` (512 ou 768 max, VRAM limitée), `--variants`,
`--lora` (LoRA Genshin/anime si dispo). Le script charge SD1.5 une seule fois (fp16 +
attention/VAE slicing + `enable_model_cpu_offload`) et enchaîne toutes les générations avant
de libérer la VRAM (`vram.free()`), conformément aux règles VRAM du projet (voir
`CLAUDE.md` §7).
