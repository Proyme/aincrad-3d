"""Batch HQ (qualite max) SUR le pod — Hunyuan3D-2 standard, octree 512, paint non-turbo.

- Forme : modele standard (pas mini) + octree_resolution eleve = geometrie + fine
- Texture : paint-v2-0 (non turbo) 2048 = texture + propre
- Optionnel multi-vues : si <nom>_back.png / _left.png / _right.png existent a cote de l'entree

Usage : python pod_batch_gen_hq.py --indir /workspace/inputs --outdir /workspace/outputs_hq --octree 512
"""
import argparse, glob, os, time, traceback
from PIL import Image
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline

MODEL = "tencent/Hunyuan3D-2"


def load_rgba(path, rembg):
    img = Image.open(path).convert("RGBA")
    if img.mode == "RGB":
        img = rembg(img)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default="/workspace/inputs")
    ap.add_argument("--outdir", default="/workspace/outputs_hq")
    ap.add_argument("--octree", type=int, default=512)
    ap.add_argument("--steps", type=int, default=50)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    imgs = sorted(p for p in glob.glob(os.path.join(args.indir, "*.png")) +
                  glob.glob(os.path.join(args.indir, "*.jpg"))
                  if not any(p.endswith(s + ".png") for s in ("_back", "_left", "_right")))
    print(f"[HQ] {len(imgs)} sujet(s) | octree={args.octree} steps={args.steps}")

    rembg = BackgroundRemover()
    print("[HQ] chargement shapegen (standard)...")
    shape = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(MODEL)  # subfolder par defaut = hunyuan3d-dit-v2-0
    print("[HQ] chargement paint (non-turbo)...")
    paint = Hunyuan3DPaintPipeline.from_pretrained(MODEL, subfolder="hunyuan3d-paint-v2-0")

    for i, path in enumerate(imgs, 1):
        name = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(args.outdir, f"{name}_hq.glb")
        t0 = time.time()
        try:
            img = load_rgba(path, rembg)
            mesh = shape(image=img, num_inference_steps=args.steps,
                         octree_resolution=args.octree)[0]
            mesh = paint(mesh, image=img)
            mesh.export(out)
            print(f"[{i}/{len(imgs)}] OK {name} -> {out} ({time.time()-t0:.0f}s)")
        except Exception:
            print(f"[{i}/{len(imgs)}] ECHEC {name}")
            traceback.print_exc()
    print("[HQ] Batch termine.")


if __name__ == "__main__":
    main()
