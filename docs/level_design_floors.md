# Level Design — Étages 2 à 10 d'Aincrad

> Document de production pour la construction des étages 2 à 10 dans Unreal Engine 5.8,
> style visuel Cube World (biomes procéduraux nets et saturés, architecture en blocs,
> terrain lissé/arrondi). Ancré dans le lore réel de Sword Art Online (wiki SAO/Fandom,
> Integral Factor, Progressive) ; les éléments non documentés dans les sources sont
> signalés **[concept cohérent]** plutôt que présentés comme canon.
>
> Référence d'échelle : Étage 1 (déjà construit) — biome plaines/Ville des Commencements,
> boss **Gardien du Labyrinthe**, 500 PV.

---

## Étage 2 — La Savane de Taurus

**Identité thématique.** Savane herbeuse ponctuée de rochers isolés et de collines
rases (lore : « floor de savane couvert de plaines et de rochers »). Faune dominante :
monstres-taureaux (type Taurus). Deux villages rivaux, **Marome** (faction rouge) et
**Taran** (faction bleue), sont en guerre permanente ; **Urbus**, ville principale,
est bâtie au sommet d'un cratère à parois plates.

**Boss.** **Asterius le Roi Taurus** (canon), soutenu par deux mini-boss de garde,
**Baran le Général Taurus** et **Nato le Colonel Taurus** — à traiter comme deux adds
à abattre avant/pendant le combat principal (mécanique de phase). PV cible boss : **650**
(voir table d'échelle). PV des deux gardes : ~110 chacun (type élite).

**Palette Cube World.**
- Herbe savane : `#C9A227` (ocre doré), `#8FA13A` (vert-olive sec)
- Terre/roche : `#B5622A` (terracotta), `#7A5230` (brun rocher)
- Ciel/accents chauds : `#F2C879` (sable clair), `#E4572E` (rouge Marome) / `#2E86AB` (bleu Taran)

**Landmarks.**
- **Urbus** : ville-cratère, ruelles en gradins, place centrale surélevée.
- **Marome** (rouge) et **Taran** (bleue) : hameaux fortifiés miniatures, bannières de
  faction, positionnés en vis-à-vis de part et d'autre d'un no-man's-land de plaine.
- Champs de rochers erratiques (blocs cubiques façon Cube World) servant de zone de
  chasse aux Taurus mineurs.
- Entrée du Labyrinthe à proximité de Taran.

---

## Étage 3 — La Forêt des Brumes Vacillantes

**Identité thématique.** Forêt entière d'arbres anciens et gigantesques. La partie sud,
coupée du reste par des montagnes et noyée dans un brouillard épais, porte le nom de
**Forêt des Brumes Vacillantes** (Forest of Wavering Mists). La ville principale,
**Zumfut**, est construite à l'intérieur de troncs d'arbres évidés au nord-est.

**Boss.** **Nerius l'Arbre-Démon** (Nerius the Evil Treant, canon) — attaque de zone
empoisonnée à large rayon en pattern signature. PV cible : **820**.

**Palette Cube World.**
- Canopée : `#1E5631` (vert émeraude profond), `#4A7856` (vert mousse)
- Écorce/troncs : `#4E3524` (brun sombre), `#6B4A33` (brun clair)
- Brume sud : `#B8C4C2` (gris-vert pâle), `#8FA39B` (gris-brume)
- Éclairage intérieur Zumfut : `#F4B942` (lueur ambre des lanternes)

**Landmarks.**
- **Zumfut** : ville troglodyte dans des troncs évidés, passerelles suspendues entre
  les arbres, lanternes ambrées.
- **Forêt des Brumes Vacillantes** : zone sud à visibilité réduite, dungeon annexe
  optionnel avant le Labyrinthe principal.
- Canopée haute praticable (ponts de branches, style Cube World blocky-organique).

---

## Étage 4 — Rovia, la Cité des Canaux

**Identité thématique.** Ville blanche bâtie au centre d'un lac carré ; les rues pavées
cèdent la place à des canaux, navigation en gondole obligatoire entre quartiers.
Élément additionnel du lore : le **Château de Yofel**, base instanciée des elfes noirs,
au milieu d'un grand lac circulaire de l'étage.

**Boss.** **Wythege l'Hippocampe** (canon) — hybride poisson/cheval, pattes avant
palmées, nageoire caudale. Capacité spéciale *Afflux d'Eau* : sous un certain seuil de
PV, ferme l'entrée de la salle et l'inonde (contrable en rouvrant la porte de
l'extérieur). Faible aux dégâts **Perforant** et **Terre**. PV cible : **1050**.

**Palette Cube World.**
- Architecture Rovia : `#F5F1E6` (blanc-crème), `#E8D9B5` (pierre claire)
- Eau/canaux : `#2FA4A9` (turquoise), `#1B6E73` (teal profond)
- Accents : `#C9A66B` (bois/gondoles), `#3B6FA0` (bleu ciel Yofel)

**Landmarks.**
- **Rovia** : cité-lac, canaux navigables en gondole, place centrale blanche.
- **Château de Yofel** : forteresse elfe noire au centre du lac circulaire, zone
  instanciée/quête spéciale.
- Réseau de ponts et écluses reliant les quartiers (formes cubiques posées sur l'eau).

---

## Étage 5 — Les Ruines du Royaume Nain

**Identité thématique.** Étage de ruines : ~30 % de terrain naturel, le reste forme un
vaste labyrinthe à ciel ouvert façon donjon géant. La colonie principale est perchée au
sommet des ruines, au sud. Lore du boss : un golem magique forgé par un roi humain
voulant annihiler un royaume nain rival (rivalité commerciale) ; ce roi apparaît en
sous-boss mort-vivant.

**Boss.** **Fuscus le Colosse Vide** (Fuscus the Vacant Colossus, canon) — golem géant
lent mais à zones d'effet large. Sous-boss : **[concept cohérent]** *Grendal, Roi Déchu*,
spectre couronné qui invoque des gardes squelettes naines. PV cible boss : **1340** ;
sous-boss : ~250.

**Palette Cube World.**
- Pierre de ruines : `#D8C7A1` (grès clair), `#A98F6B` (grès ombré)
- Rouille/métal golem : `#B5573D` (rouille), `#5C5C66` (gris-bleu métal)
- Runes magiques golem : `#7DD8E0` (cyan lumineux) ou `#B57DE0` (violet rune, variante nuit)

**Landmarks.**
- Colonie perchée au sommet des ruines sud (dernier bastion habité).
- Labyrinthe-donjon à ciel ouvert couvrant l'essentiel du terrain (blocs de pierre
  effondrés, arches brisées, escaliers suspendus).
- Forge de golems abandonnée : champ de golems inertes/pièces détachées géantes,
  bon point de repère visuel et zone de farm de minerai.
- Crypte du Roi Déchu : antichambre optionnelle avant la salle de Fuscus.

---

## Étage 6 — Les Marais aux Secrets

**Identité thématique.** Étage presque entièrement composé de zones humides
(wetlands), qui dissimulent des vestiges de plusieurs races anciennes (ruines
partiellement englouties). Structure : 2 champs extérieurs, 1 donjon annexe, 1
labyrinthe principal.

**Boss.** **Le Cube Irrationnel** (The Irrational Cube, canon) — entité géométrique
aberrante, cohérente à traiter comme un boss à hitbox/pattern « impossible »
(faces multiples attaquant indépendamment). PV cible : **1720**.

**Palette Cube World.**
- Marais/eau stagnante : `#4A5D45` (vert marécage), `#3A4A3F` (vert sombre)
- Boue/berges : `#6B5A3E` (brun boueux), `#8A7B57` (brun-vert clair)
- Brume/mystère : `#C9C7D1` (lilas pâle), accents runiques des vestiges engloutis :
  `#5EC9C0` (turquoise ruine)

**Landmarks.**
- Villages sur pilotis au-dessus des tourbières.
- Vestiges à demi engloutis de races anciennes (colonnades naines/elfiques émergeant
  de l'eau) — purement décoratif/lore, pas de faction active.
- Donjon annexe (grotte ou temple immergé) séparé du Labyrinthe principal.
- Labyrinthe principal : temple-marais menant à la salle du Cube Irrationnel.

---

## Étage 7 — Les Deux Automnes

**Identité thématique.** Forêt façon automne, mais coupée en deux ambiances
tranchées : une moitié où il pleut en continu, l'autre couverte de feuillages dorés
éclatants. Faune notable : Kapiyva (type capybara), boucs à grandes cornes, trolls
(dont un troll de champ nommé, *Thor l'Ennuyeux Troll*).

**Boss.** **Aghyellr le Wyrm Igné** (Aghyellr the Igneous Wyrm, canon) — dragon/wyrm
à composante rocheuse-volcanique, tranchant avec le reste de l'étage forestier
(labyrinthe = poche géothermique dans la forêt). PV cible : **2200**. Mini-boss de
champ optionnel *Thor l'Ennuyeux Troll* (~180 PV) dans la zone pluvieuse.

**Palette Cube World.**
- Zone dorée : `#E8A33D` (feuillage doré), `#C9782E` (orange automne)
- Zone pluvieuse : `#5C6B73` (gris-bleu mouillé), `#8A9BA3` (gris clair pluie)
- Labyrinthe igné (Aghyellr) : `#8B2E1F` (rouge braise), `#3A2E2A` (roche volcanique
  sombre), lueur `#F2661D` (orange lave)

**Landmarks.**
- Vallée pluvieuse : brouillard bas, sol détrempé, clairières à trolls.
- Plateau doré : bois clairsemé aux feuilles dorées, meilleure visibilité, hameaux de
  chasseurs.
- Faille géothermique menant au Labyrinthe d'Aghyellr : transition brutale forêt →
  roche volcanique (bon repère de progression visuel).

---

## Étage 8 — Frieven, le Village Suspendu

**Identité thématique.** Étage forestier où la totalité de la surface est recouverte
d'une eau insondable, donc infranchissable au sol : déplacement uniquement via
passerelles suspendues, branches d'arbres géants, et ponts artificiels. Le Labyrinthe
est un arbre monumental (noirci/charbon dans les adaptations ALO).

**Boss.** **[concept cohérent]** *Yggdrathorn, le Cœur d'Écorce* — entité-esprit
fusionnée au cœur de l'arbre-labyrinthe, racines/lianes comme attaques de zone,
cohérent avec le lore du « Labyrinthe = arbre géant ». PV cible : **2810**.

**Palette Cube World.**
- Eau insondable : `#0E3B43` (bleu-noir profond), `#1C5C63` (teal sombre)
- Canopée/village : `#2F6B4F` (vert forêt), `#5C8F6B` (vert clair feuillage)
- Bois des passerelles : `#6B4E32` (bois brun)
- Labyrinthe-arbre noirci : `#242021` (charbon), lueur intérieure `#7A3FA0` (violet
  surnaturel, cohérent avec un boss-esprit)

**Landmarks.**
- **Frieven** (village, canon) : cabanes sur pilotis/branches, réseau de ponts
  suspendus reliant les habitations, pas de sol praticable.
- Canopée-labyrinthe : ascension verticale le long de l'arbre géant jusqu'à la salle
  du boss, au lieu d'un donjon horizontal classique — bon accroche de level design
  vertical distinctif de cet étage.
- Pontons de pêche/récolte au-dessus de l'eau insondable (zone de farm optionnelle).

---

## Étage 9 — La Forêt des Elfes Déchus

**Identité thématique.** Forêt à composante magique marquée ; les ennemis de l'étage
sont majoritairement faibles aux éléments Perforant, Sacré et Ténèbres — cohérent avec
une iconographie elfique/féerique en clair-obscur (bosquets lumineux la nuit, ruines
elfiques déchues le jour).

**Boss.** **La Elfe Déchue Démoniaque** (Demonic the Fallen Elven, canon) — combat
rapproché à double dague, capacité de coup de pied étourdissant. PV cible : **3600**.

**Palette Cube World.**
- Forêt magique de nuit : `#241B3A` (indigo profond), `#3E2E5C` (violet sombre)
- Lueurs féeriques : `#7FE0C9` (turquoise lumineux), `#C9A8F2` (lilas lumineux)
- Ruines elfiques déchues : `#E8E3D8` (blanc-ivoire terni), `#8A8378` (gris-pierre sale)

**Landmarks.**
- Bosquets lumineux nocturnes (flore bioluminescente, zones de farm de mana/matériaux
  magiques).
- Ruines elfiques déchues : colonnades brisées, statues profanées, enclaves d'elfes
  hostiles (correspond aux ennemis « Fallen Elf » du lore).
- Double sanctuaire Sacré/Ténèbres en amont du Labyrinthe (mini-zone d'énigme
  thématique, cohérente avec les faiblesses élémentaires de l'étage).

---

## Étage 10 — Senja, la Cité du Bambou

**Identité thématique.** Étage inspiré d'un bourg japonais de l'ère Edo, anciennement
nommé **Château de Senja**. Premier « safe zone » interactif complet depuis l'Étage 1 :
ville paisible aux habitants en kimono/yukata, échoppes d'artisans, quêtes de vaisselle.
Extérieurs couverts de bambous, cascades ; ennemis notables : guerriers orochi et
bêtes mythiques.

**Boss.** **[concept cohérent]** *Yamikagachi, l'Orochi aux Huit Têtes* — serpent
géant multi-têtes directement dérivé du folklore Yamata no Orochi et cohérent avec les
« guerriers orochi » déjà présents dans le bestiaire de l'étage. PV cible : **4610**.

**Palette Cube World.**
- Bambouseraie : `#5B8C3E` (vert bambou), `#3E6B2E` (vert sombre)
- Architecture Senja : `#B5322E` (rouge vermillon torii/temple), `#4A3A2A` (bois brun),
  `#F2EDE0` (murs blanc-crème)
- Nuit/cascades : `#2E3A5C` (indigo nocturne), `#A8D8E0` (eau claire cascade)

**Landmarks.**
- **Senja** (canon, ex-Château de Senja) : ville-sanctuaire, toits en pagode, ponts de
  bois rouges, place de marché, accès aux toits explorables.
- Bambouseraie périphérique et cascades : zone de chasse aux orochis mineurs et
  bêtes mythiques.
- Sanctuaire de l'Orochi : dungeon final en forme de temple-serpent menant à
  Yamikagachi (torii successifs, statues de serpent, eau sacrée).

---

## Progression & équilibrage

### PV des boss d'étage

Formule d'échelle géométrique douce, ancrée sur la référence Étage 1 = 500 PV :

```
PV_Boss(n) = arrondi( 500 × 1.28^(n-1) , dizaine la plus proche )
```

| Étage | 1 (réf.) | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| PV Boss | 500 | 650 | 820 | 1050 | 1340 | 1720 | 2200 | 2810 | 3600 | 4610 |

Facteur ×1.28/étage : reste jouable en solo à condition que l'équipement/l'XP suivent
la même courbe (voir loot ci-dessous) — pas de pic brutal, pas de plateau de grind.

### PV / dégâts des ennemis normaux

```
PV_Ennemi(n)     = arrondi( 30 × 1.18^(n-1) )
Dégâts_Ennemi(n) = arrondi( 8  × 1.15^(n-1) )
```

| Étage | 1 (réf.) | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| PV ennemi normal | 30 | 35 | 42 | 49 | 58 | 68 | 81 | 95 | 113 | 133 |
| Dégâts/coup | 8 | 9 | 11 | 12 | 14 | 16 | 18 | 21 | 24 | 28 |

**Ennemis élites** (gardes de boss type Baran/Nato, Thor l'Ennuyeux Troll, etc.) :
viser **4 à 6×** les PV d'un ennemi normal du même étage, jamais plus de ~1/8 des PV
du boss de l'étage (pour rester un obstacle secondaire, pas un mur).

**Recommandation gameplay solo** : faire progresser les dégâts du joueur (arme +
niveau) sur une courbe légèrement au-dessus de celle des PV boss (~×1.3/étage) pour
compenser l'absence de raid coopératif — évite le grind excessif tout en gardant
chaque boss comme un vrai check de compétence/équipement, pas seulement de niveau.

### Table de butin par palier d'étages (chaînes compatibles `Inventory`)

**Palier Étages 2–4 (early game)**
- Armes : `"Épée Longue en Acier +2"`, `"Rapière Vive-Lame"`, `"Hache de Bûcheron Renforcée"`
- Soin : `"Potion de Soin Mineure"`, `"Antidote"`
- Craft : `"Minerai de Fer Brut"`, `"Corne de Taureau d'Urbus"`, `"Écaille de Wythege"`,
  `"Sève de Grand Arbre"`
- Utilitaire : `"Cristal de Téléportation"`, `"Cristal de Stockage"`

**Palier Étages 5–7 (mid game)**
- Armes : `"Marteau du Colosse Fuscus"`, `"Dague Jumelle de Brume"`,
  `"Arc Composite des Tourbières"`
- Soin : `"Potion de Soin Majeure"`, `"Antidote Supérieur"`,
  `"Élixir de Résistance au Poison"`
- Craft : `"Noyau de Golem Ancien"`, `"Venin Concentré de Nerius"`,
  `"Écaille Ignée d'Aghyellr"`, `"Boue Purifiée des Marais"`
- Accessoires : `"Anneau du Roi Déchu"`, `"Amulette Anti-Poison"`
- Utilitaire : `"Cristal de Réparation"`

**Palier Étages 8–10 (late early-game)**
- Armes : `"Sabre de Frieven"`, `"Lame de l'Elfe Déchue"`, `"Naginata de Senja"`
- Soin : `"Potion de Soin Suprême"`, `"Onguent Régénérant Supérieur"`
- Craft : `"Fragment de Cœur d'Écorce"`, `"Plume d'Elfe Déchu"`, `"Bambou Sacré de Senja"`,
  `"Écaille d'Orochi"`
- Quête/unique : `"Clé du Sanctuaire de Senja"`, `"Fragment du Cube Irrationnel"`
- Utilitaire : `"Cristal de Téléportation Supérieur"`

Le champ `Gold` (entier) progresse indépendamment sur `Or_Enemy(n) = arrondi(5 ×
1.2^(n-1))` par ennemi normal tué et `Or_Boss(n) = PV_Boss(n) / 2` par boss vaincu —
cohérent avec la même courbe douce que les PV pour éviter tout pic d'inflation.
