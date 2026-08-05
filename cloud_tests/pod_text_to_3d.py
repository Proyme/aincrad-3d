"""FLOW 2 — TEXTE -> 3D, 100% sur le pod RunPod.

Pour chaque prompt (fichier --prompts, 1 ligne = 'nom | description') :
  1. SD (sur le pod) genere le concept image (prompt parfait Genshin, A-pose, fond blanc)
  2. Hunyuan-2 : forme (octree 512) + texture
  3. export .glb dans outdir  (+ le concept .png pour controle)

Usage (sur le pod) :
    python pod_text_to_3d.py --prompts /workspace/prompts.txt --outdir /workspace/outputs_t2d
"""
import argparse, os, time, traceback
import torch
from PIL import Image

# prompt parfait (cel-shading plat, sujet unique, A-pose, fond blanc) — ideal concept + 3D
STYLE = ("1girl, solo, full body, head to toe, Genshin Impact official character concept art, "
         "standing A-pose, arms slightly apart, facing viewer, front view, symmetrical, "
         "cel shading, flat colors, clean bold lineart, two-tone shading, vibrant colors, "
         "detailed costume, plain white background, centered, character fully visible")
NEG = ("multiple views, character sheet, turnaround, multiple characters, 2girls, text, watermark, "
       "signature, logo, cropped, out of frame, close-up, portrait, from behind, back view, "
       "realistic, photorealistic, 3d render, cinematic, soft gradient shading, blurry, lowres, "
       "bad anatomy, bad hands, extra fingers, extra limbs, fused fingers, busy background, scenery")

SD_MODEL = "sd-legacy/stable-diffusion-v1-5"   # fiable ; remplacer par un checkpoint anime pour + beau
HY_MODEL = "tencent/Hunyuan3D-2"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--outdir", default="/workspace/outputs_t2d")
    ap.add_argument("--octree", type=int, default=256)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    jobs = []
    for line in open(a.prompts, encoding="utf-8"):
        line = line.strip()
        if line and "|" in line:
            n, p = line.split("|", 1)
            jobs.append((n.strip(), p.strip()))
    print(f"[T2D] {len(jobs)} perso(s) a generer")

    # --- 1. SD concept ---
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    print("[T2D] chargement SD...")
    sd = StableDiffusionPipeline.from_pretrained(SD_MODEL, torch_dtype=torch.float16,
                                                 safety_checker=None, requires_safety_checker=False)
    sd.scheduler = DPMSolverMultistepScheduler.from_config(sd.scheduler.config)
    sd = sd.to("cuda")
    concepts = []
    for n, p in jobs:
        img = sd(prompt=f"{p}, {STYLE}", negative_prompt=NEG, num_inference_steps=30,
                 guidance_scale=7.0, width=512, height=768).images[0]
        cp = os.path.join(a.outdir, f"{n}.png")
        img.save(cp); concepts.append((n, cp))
        print(f"[T2D] concept {n} -> {cp}")
    del sd; torch.cuda.empty_cache()

    # --- 2+3. Hunyuan 3D + texture ---
    from hy3dgen.rembg import BackgroundRemover
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
    from hy3dgen.texgen import Hunyuan3DPaintPipeline
    rembg = BackgroundRemover()
    shape = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(HY_MODEL)
    paint = Hunyuan3DPaintPipeline.from_pretrained(HY_MODEL, subfolder="hunyuan3d-paint-v2-0-turbo")

    for i, (n, cp) in enumerate(concepts, 1):
        out = os.path.join(a.outdir, f"{n}.glb")
        t0 = time.time()
        try:
            img = Image.open(cp).convert("RGBA")
            if img.mode == "RGB":
                img = rembg(img)
            mesh = shape(image=img, octree_resolution=a.octree, num_inference_steps=50)[0]
            mesh = paint(mesh, image=img)
            mesh.export(out)
            print(f"[{i}/{len(concepts)}] OK {n} -> {out} ({time.time()-t0:.0f}s)")
        except Exception:
            print(f"[{i}/{len(concepts)}] ECHEC {n}"); traceback.print_exc()
    print("[T2D] termine.")


if __name__ == "__main__":
    main()
