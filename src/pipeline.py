"""Orchestrateur du pipeline complet (= Meshy).

Enchaîne les étapes en respectant la contrainte VRAM 8 Go (séquentiel) :
    [prompt texte] -> étape 1 (concept SD)  ┐
    [image]        ----------------------→  ├→ étape 2 (mesh) -> étape 4 (Blender : export + cel-shader)
                                            ┘
L'étape 3 (rig UniRig) sera insérée entre 2 et 4 une fois validée.

Usage :
    # depuis une image existante
    python src/pipeline.py --image inputs/perso.png --name perso --toon
    # depuis un prompt texte (génère d'abord le concept)
    python src/pipeline.py --prompt "anime cat girl, ..." --name perso --backend hunyuan3d --toon
"""
import argparse
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))


def load_cfg():
    with open(os.path.join(ROOT, "config.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(cmd):
    print(f"\n>>> {' '.join(str(c) for c in cmd)}\n")
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--image", help="image d'entrée du personnage")
    g.add_argument("--prompt", help="description texte (génère le concept via SD)")
    ap.add_argument("--name", default="perso")
    ap.add_argument("--backend", choices=["triposr", "hunyuan3d"], default=None)
    ap.add_argument("--toon", action="store_true", help="applique le cel-shader (preview EEVEE)")
    args = ap.parse_args()

    cfg = load_cfg()
    py = sys.executable
    out_dir = os.path.join(ROOT, cfg["paths"]["outputs"])
    in_dir = os.path.join(ROOT, cfg["paths"]["inputs"])
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(in_dir, exist_ok=True)
    backend = args.backend or cfg["image_to_3d"]["backend"]

    # --- Étape 1 : concept (si prompt) ---
    if args.prompt:
        c = cfg["concept"]
        image_path = os.path.join(in_dir, f"{args.name}_concept.png")
        prompt = f"{args.prompt}, {c['style_suffix']}"
        cmd = [
            py, os.path.join(HERE, "step1_concept.py"),
            "--prompt", prompt, "--out", image_path,
            "--model", c["model"], "--steps", str(c["steps"]),
            "--cfg", str(c["cfg"]), "--width", str(c["width"]), "--height", str(c["height"]),
        ]
        if c.get("lora"):
            cmd += ["--lora", c["lora"], "--lora-scale", str(c["lora_scale"])]
        run(cmd)
    else:
        image_path = args.image

    # --- Étape 2 : image -> mesh 3D ---
    # TripoSR -> .obj (vertex colors), Hunyuan -> .glb (sort déjà debout)
    ext = "obj" if backend == "triposr" else "glb"
    mesh_path = os.path.join(out_dir, f"{args.name}.{ext}")
    cmd = [
        py, os.path.join(HERE, "step2_image_to_3d.py"),
        "--input", image_path, "--out", mesh_path, "--backend", backend,
        "--resolution", str(cfg["image_to_3d"]["resolution"]),
        "--hunyuan-model", cfg["image_to_3d"]["hunyuan_model"],
    ]
    if cfg["image_to_3d"].get("bake_texture"):
        cmd.append("--bake-texture")
    run(cmd)

    # --- Étape 3 : rigging (fallback Mixamo/AccuRIG documenté) ---
    run([py, os.path.join(HERE, "step3_rig.py"), "--input", mesh_path])

    # --- Étape 4 : Blender (export GLB/FBX + cel-shader) ---
    out_base = os.path.join(out_dir, args.name)
    cmd = [
        cfg["blender"]["exe"], "--background",
        "--python", os.path.join(ROOT, "blender", "cleanup_export.py"),
        "--", mesh_path, out_base,
    ]
    if args.toon:
        cmd.append("--toon")
    if backend == "triposr":
        cmd.append("--triposr-orient")
    run(cmd)

    print(f"\n[PIPELINE OK] -> {out_base}.glb / {out_base}.fbx")


if __name__ == "__main__":
    main()
