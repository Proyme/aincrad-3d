"""S'exécute SUR le pod RunPod — génération 3D EN BATCH (forme + texture).

Parcourt /workspace/inputs/*.png, génère pour chacun un .glb texturé dans
/workspace/outputs/. Sur A100/H100 80 Go : texture 2048, GPU exploité à fond.

Usage (sur le pod) :
    python pod_batch_gen.py --indir /workspace/inputs --outdir /workspace/outputs
"""
import argparse
import glob
import os
import time
import traceback

from PIL import Image
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline

MODEL = "tencent/Hunyuan3D-2"  # repo complet (forme + texture) — la VRAM 80 Go encaisse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default="/workspace/inputs")
    ap.add_argument("--outdir", default="/workspace/outputs")
    ap.add_argument("--no-texture", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    imgs = sorted(glob.glob(os.path.join(args.indir, "*.png")) +
                  glob.glob(os.path.join(args.indir, "*.jpg")))
    print(f"[*] {len(imgs)} image(s) à traiter")

    print("[*] Chargement des pipelines (1 fois, réutilisés pour tout le batch)...")
    rembg = BackgroundRemover()
    shape = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(MODEL)
    paint = None if args.no_texture else Hunyuan3DPaintPipeline.from_pretrained(MODEL)

    for i, path in enumerate(imgs, 1):
        name = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(args.outdir, f"{name}.glb")
        t0 = time.time()
        try:
            img = Image.open(path).convert("RGBA")
            if img.mode == "RGB":
                img = rembg(img)
            mesh = shape(image=img)[0]
            if paint is not None:
                mesh = paint(mesh, image=img)
            mesh.export(out)
            print(f"[{i}/{len(imgs)}] OK {name} -> {out} ({time.time()-t0:.0f}s)")
        except Exception:
            print(f"[{i}/{len(imgs)}] ECHEC {name}")
            traceback.print_exc()

    print("[*] Batch terminé.")


if __name__ == "__main__":
    main()
