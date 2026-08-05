"""Genere UN perso (image -> mesh+texture) — Hunyuan-2 standard + paint TURBO.
Concu pour etre lance en PLUSIEURS instances paralleles (sature le GPU/CPU du pod).

Usage : python pod_gen_one.py --input x.png --out x.glb --octree 256
"""
import argparse, time, traceback
import torch
from PIL import Image
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline

MODEL = "tencent/Hunyuan3D-2"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--octree", type=int, default=256)
    a = ap.parse_args()
    t0 = time.time()
    try:
        # TOUJOURS retirer le fond, sinon Hunyuan fait un panneau plat (billboard)
        img = Image.open(a.input).convert("RGB")
        img = BackgroundRemover()(img)
        shape = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(MODEL)
        mesh = shape(image=img, octree_resolution=a.octree, num_inference_steps=50)[0]
        del shape; torch.cuda.empty_cache()
        paint = Hunyuan3DPaintPipeline.from_pretrained(MODEL, subfolder="hunyuan3d-paint-v2-0-turbo")
        mesh = paint(mesh, image=img)
        mesh.export(a.out)
        print(f"OK {a.out} ({time.time()-t0:.0f}s)")
    except Exception:
        print(f"ECHEC {a.input}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
