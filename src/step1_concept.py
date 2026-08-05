"""Étape 1 du pipeline — Texte -> Image concept (Stable Diffusion).

Génère l'image de référence du personnage à partir d'un prompt. Pour le style
Genshin : utiliser un checkpoint anime + un LoRA Genshin (Civitai) renseignés
dans config.yaml. Optimisé 8 Go (fp16, attention/VAE slicing, offload CPU).

Usage :
    python src/step1_concept.py --prompt "anime girl, genshin impact style, ..." --out inputs/concept.png
"""
import argparse
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(__file__))
import vram  # noqa: E402

# prompt négatif générique pour un concept propre, sujet centré, fond neutre
NEG_DEFAULT = (
    "lowres, bad anatomy, bad hands, extra fingers, missing fingers, "
    "blurry, watermark, signature, multiple views, cropped, out of frame, "
    "realistic, photo, 3d render, busy background"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default=NEG_DEFAULT)
    ap.add_argument("--out", default="inputs/concept.png")
    ap.add_argument("--model", default="sd-legacy/stable-diffusion-v1-5",
                    help="repo HF ou chemin local du checkpoint")
    ap.add_argument("--lora", default=None, help="chemin .safetensors d'un LoRA (ex. Genshin)")
    ap.add_argument("--lora-scale", type=float, default=0.8)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--seed", type=int, default=-1)
    args = ap.parse_args()

    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"[*] Device : {device} | dtype : {dtype}")

    print(f"[*] Chargement du checkpoint : {args.model}")
    pipe = StableDiffusionPipeline.from_pretrained(
        args.model, torch_dtype=dtype, safety_checker=None, requires_safety_checker=False
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

    # économies VRAM (Turing 8 Go)
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    if device == "cuda":
        pipe.enable_model_cpu_offload()  # garde la VRAM basse
    else:
        pipe = pipe.to(device)

    if args.lora and os.path.exists(args.lora):
        print(f"[*] LoRA : {args.lora} (scale {args.lora_scale})")
        pipe.load_lora_weights(args.lora)
        pipe.fuse_lora(lora_scale=args.lora_scale)

    gen = None
    if args.seed >= 0:
        gen = torch.Generator(device="cpu").manual_seed(args.seed)

    vram.report("SD prêt")
    print("[*] Génération...")
    image = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative,
        num_inference_steps=args.steps,
        guidance_scale=args.cfg,
        width=args.width,
        height=args.height,
        generator=gen,
    ).images[0]

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    image.save(args.out)
    print(f"[OK] Concept -> {args.out}")

    del pipe
    vram.free()


if __name__ == "__main__":
    main()
