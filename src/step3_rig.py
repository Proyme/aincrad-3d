"""Étape 3 du pipeline — Rigging (squelette + skinning).

⚠ Sur RTX 2070 (Turing), UniRig est bloqué (flash_attn exige Ampere sm_80+, et
transformers 4.51 entre en conflit avec le pin 4.49). Voir docs/rigging.md.

Ce module :
  - tente UniRig s'il est installé dans un environnement compatible ;
  - sinon, affiche la procédure de fallback (Mixamo en ligne / AccuRIG local) et
    laisse le mesh tel quel (riggable ensuite manuellement).

Usage :
    python src/step3_rig.py --input outputs/perso.glb --out outputs/perso_rigged.fbx
"""
import argparse
import os
import shutil
import sys

MIXAMO_HELP = """
========================================================================
 RIGGING - fallback recommande (humanoide) : MIXAMO (gratuit, en ligne)
========================================================================
 1. https://www.mixamo.com  (compte Adobe gratuit)
 2. Upload : {mesh}
 3. Placer les marqueurs -> auto-rig + skinning automatiques
 4. Download FBX "With Skin" -> importer dans Unreal Engine 5

 Alternative 100% locale (desktop, GUI) : AccuRIG
   https://actorcore.reallusion.com/auto-rig

 Details et option UniRig avancee : docs/rigging.md
========================================================================
"""


def try_unirig(input_mesh, out_path):
    """Tente UniRig si présent et fonctionnel. Retourne True si riggé."""
    unirig_dir = os.path.join(
        os.path.dirname(__file__), "..", "third_party", "UniRig"
    )
    if not os.path.isdir(unirig_dir):
        return False
    try:
        # flash_attn est la dépendance qui casse sur Turing : on vérifie tôt.
        import flash_attn  # noqa: F401
    except Exception:
        print("[!] flash_attn indisponible (normal sur Turing/RTX 2070) — UniRig sauté.")
        return False
    # … intégration complète UniRig à implémenter dans un venv compatible …
    print("[!] UniRig détecté mais intégration non activée dans cet environnement.")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="mesh à rigger (.glb/.fbx/.obj)")
    ap.add_argument("--out", default=None, help="sortie riggée (sinon = passthrough)")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERREUR] Introuvable : {args.input}")
        sys.exit(1)

    if try_unirig(args.input, args.out):
        print(f"[OK] Riggé -> {args.out}")
        return

    # Fallback : on n'a pas riggé localement -> instructions + passthrough du mesh
    print(MIXAMO_HELP.format(mesh=os.path.abspath(args.input)))
    if args.out and args.out != args.input:
        shutil.copy(args.input, args.out)
        print(f"[i] Mesh non riggé copié -> {args.out} (à rigger via Mixamo/AccuRIG).")


if __name__ == "__main__":
    main()
