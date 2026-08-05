# Cel-shader style Genshin dans Unreal Engine 5

> Le look Genshin se fait **dans le moteur**, pas dans le GLB. Le GLB/FBX exporté
> ne contient que le mesh + couleurs/texture. On applique le NPR ici.

## 1. Import du personnage

1. Glisser `outputs/<perso>.fbx` (ou `.glb`) dans le Content Browser.
2. Import options :
   - **Skeletal Mesh** : décocher si le perso n'est pas encore riggé (étape 3),
     sinon cocher pour importer le squelette.
   - **Import Normals** : *Import* (garder les normales du mesh).
   - **Combine Meshes** : selon le besoin.
3. Le perso sort debout mais peut nécessiter une rotation de 90°/180° (Yaw) dans
   le viewport — ajuster une fois.

## 2. Matériau cel-shading (2-3 tons)

Créer un Material, **Shading Model = Unlit** (on contrôle toute la lumière à la main,
le plus simple pour un look Genshin propre et stable).

Nodes (logique) :
```
BaseColor (texture/vertex color)
        │
        ▼
   [ N·L ]  ──►  marche (rampe)  ──►  multiply  ──►  Emissive Color
        ▲                              ▲
   Normal·LightDir              BaseColor
```

Détail des nœuds :
1. **Light direction** : pour de l'Unlit, exposer un paramètre vecteur `LightDir`
   (ou lire une lumière via un Blueprint). `NdotL = dot(normalize(Normal), -LightDir)`.
   - `VertexNormalWS` ou `PixelNormalWS` pour la normale monde.
2. **Rampe toon** : `NdotL` (range -1..1) → remap 0..1 → quantifier :
   - 2 tons : `step(0.5, ndotl01)` → 0 ou 1.
   - 3 tons : `floor(ndotl01 * 3) / 2`.
   - Adoucir le bord avec un petit `smoothstep` pour éviter l'aliasing.
3. **Couleurs ombre/lumière** : `lerp(ShadowColor, LightColor, toonStep)`.
   - ShadowColor = BaseColor × ~0.6 teinté légèrement vers le bleu/violet (ombre Genshin).
4. **Multiply** par la BaseColor (texture) → brancher sur **Emissive Color**.

### Rim light (liseré lumineux Genshin)
```
fresnel = pow(1 - saturate(dot(N, V)), RimPower)
emissive += fresnel * RimColor * RimIntensity
```
`V` = `CameraVector`. Donne le contour lumineux caractéristique sur les bords.

## 3. Outlines (contours noirs)

Méthode **inverted hull** (la plus fidèle Genshin) :
1. Dupliquer le mesh OU utiliser un second material slot.
2. Material outline : **Two Sided**, **Front Face Culling** (afficher l'arrière),
   couleur noire en Emissive (Unlit).
3. Dans le material, pousser les sommets le long de la normale :
   `WorldPositionOffset = VertexNormalWS * OutlineThickness`
   - `OutlineThickness` ~ 0.5–2 (échelle cm), idéalement × distance caméra pour
     une épaisseur constante à l'écran.

Alternative : **Post Process** (Sobel sur depth+normal) — plus global, moins
"par-perso", mais pas besoin de modifier le mesh.

## 4. Séparation des matériaux (peau / cheveux / yeux / vêtements)

Genshin sépare les zones. Tant que le mesh généré n'a pas de material IDs propres :
- soit peindre des masques (Vertex Paint) pour distinguer les zones,
- soit, à terme, exporter depuis Blender plusieurs material slots (étape 7 du projet).

Chaque zone = mêmes nœuds toon avec des paramètres différents (les cheveux ont
souvent une rampe plus contrastée + un reflet anisotrope "halo").

## 5. Réglages projet utiles
- Activer **Custom Depth/Stencil** si outline en post-process.
- Désactiver l'auto-exposure trop agressive (Post Process Volume) pour garder
  des couleurs plates.
