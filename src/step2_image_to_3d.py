"""Étape 2 du pipeline — Image -> Mesh 3D texturé.

Deux backends sélectionnables (--backend) :
  - triposr   : rapide/léger (~1,6 Go VRAM, 24 s), couleurs de sommets. Défaut.
  - hunyuan3d : qualité supérieure (géométrie + texture UV), plus lourd.

Calibré 8 Go : modèle en fp16, déchargement VRAM entre étapes.

Usage :
    python src/step2_image_to_3d.py --input inputs/perso.png --out outputs/perso.glb
    python src/step2_image_to_3d.py --input inputs/perso.png --out outputs/perso.glb --backend hunyuan3d
"""
import argparse
import os
import sys
import time

import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import vram  # noqa: E402


# ----------------------------------------------------------------------------
# Backend 1 : TripoSR
# ----------------------------------------------------------------------------
def run_triposr(args, device):
    sys.path.insert(0, os.path.join(ROOT, "third_party", "TripoSR"))
    from tsr.system import TSR
    from tsr.utils import remove_background, resize_foreground
    import rembg

    print("[*] [TripoSR] Chargement du modèle...")
    model = TSR.from_pretrained(
        "stabilityai/TripoSR", config_name="config.yaml", weight_name="model.ckpt"
    )
    model.renderer.set_chunk_size(8192)
    model.to(device)
    vram.report("TripoSR chargé")

    img = Image.open(args.input)
    if not args.no_remove_bg:
        print("[*] Détourage (rembg)...")
        session = rembg.new_session()
        img = remove_background(img, session)
        img = resize_foreground(img, args.fg_ratio)
        arr = np.array(img).astype(np.float32) / 255.0
        arr = arr[:, :, :3] * arr[:, :, 3:4] + 0.5 * (1 - arr[:, :, 3:4])
        img = Image.fromarray((arr * 255.0).astype(np.uint8))
    else:
        img = img.convert("RGB")

    print("[*] Inférence 3D...")
    with torch.no_grad():
        scene_codes = model([img], device=device)
    print(f"[*] Extraction du mesh (résolution {args.resolution})...")
    mesh = model.extract_mesh(scene_codes, has_vertex_color=True, resolution=args.resolution)[0]

    mesh.export(args.out)
    print(f"[OK] Mesh -> {args.out} ({len(mesh.vertices)} sommets, {len(mesh.faces)} faces)")
    del model
    vram.free()


# ----------------------------------------------------------------------------
# Backend 2 : Hunyuan3D 2.x  (forme, puis texture si rasterizer dispo)
# ----------------------------------------------------------------------------
def run_hunyuan3d(args, device):
    sys.path.insert(0, os.path.join(ROOT, "third_party", "Hunyuan3D-2"))
    from hy3dgen.rembg import BackgroundRemover
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

    model_path = args.hunyuan_model  # ex. tencent/Hunyuan3D-2mini (léger) ou tencent/Hunyuan3D-2

    img = Image.open(args.input).convert("RGBA")
    if img.mode == "RGB" or not args.no_remove_bg:
        print("[*] Détourage (Hunyuan rembg)...")
        img = BackgroundRemover()(img)

    # le repo "mini" range le DiT dans un sous-dossier spécifique
    subfolder = args.hunyuan_subfolder or (
        "hunyuan3d-dit-v2-mini" if "mini" in model_path else "hunyuan3d-dit-v2-0"
    )
    print(f"[*] [Hunyuan3D] Chargement shapegen : {model_path} / {subfolder}")
    shape_pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(model_path, subfolder=subfolder)
    # économies VRAM
    try:
        shape_pipe.enable_flashvdm()
    except Exception:
        pass
    vram.report("Hunyuan shapegen chargé")

    print("[*] Génération de la forme...")
    mesh = shape_pipe(image=img)[0]
    del shape_pipe
    vram.free()

    # texture (optionnelle — nécessite custom_rasterizer compilé)
    if args.bake_texture:
        try:
            from hy3dgen.texgen import Hunyuan3DPaintPipeline
            # les sous-modèles delight/paint ne sont QUE dans le repo standard
            print(f"[*] Génération de la texture UV ({args.hunyuan_texgen_model})...")
            tex_pipe = Hunyuan3DPaintPipeline.from_pretrained(
                args.hunyuan_texgen_model, subfolder=args.hunyuan_paint_subfolder
            )
            mesh = tex_pipe(mesh, image=img)
            del tex_pipe
            vram.free()
        except Exception as e:
            print(f"[!] Texture non générée (rasterizer non compilé ?) : {e}")
            print("[!] Export de la forme sans texture UV.")

    mesh.export(args.out)
    print(f"[OK] Mesh -> {args.out}")
    vram.free()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="outputs/mesh.glb")
    ap.add_argument("--backend", choices=["triposr", "hunyuan3d"], default="triposr")
    # options TripoSR
    ap.add_argument("--resolution", type=int, default=256)
    ap.add_argument("--no-remove-bg", action="store_true")
    ap.add_argument("--fg-ratio", type=float, default=0.85)
    # options Hunyuan3D
    ap.add_argument("--hunyuan-model", default="tencent/Hunyuan3D-2mini")
    ap.add_argument("--hunyuan-subfolder", default=None)
    ap.add_argument("--hunyuan-texgen-model", default="tencent/Hunyuan3D-2",
                    help="repo des sous-modèles texture (delight+paint)")
    ap.add_argument("--hunyuan-paint-subfolder", default="hunyuan3d-paint-v2-0")
    ap.add_argument("--bake-texture", action="store_true")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Device : {device} | backend : {args.backend}")
    if device == "cpu":
        print("[!] Pas de CUDA — la génération 3D sera très lente.")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    t0 = time.time()
    if args.backend == "triposr":
        run_triposr(args, device)
    else:
        run_hunyuan3d(args, device)
    print(f"[OK] Durée totale : {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
