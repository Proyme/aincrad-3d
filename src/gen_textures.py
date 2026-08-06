"""Génération de textures de décor stylisées (Aincrad x Cube World) — SD1.5 local.

Génère une série de swatchs de matériaux (herbe, pierre, bois, toit, terre, eau...)
pour habiller les surfaces déjà construites dans Unreal (sol, murs, toits). Style visé :
couleurs plates/saturées façon Cube World, pas de photoréalisme, pas de bruit type
Minecraft — un peu de grain organique propre.

Charge le checkpoint SD1.5 une seule fois puis enchaîne toutes les générations
(mêmes optimisations VRAM que step1_concept.py : fp16, attention/VAE slicing,
model_cpu_offload, batch de 1).

Usage :
    python src/gen_textures.py
    python src/gen_textures.py --steps 25 --cfg 7.5 --size 512 --variants 2
"""
import argparse
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(__file__))
import vram  # noqa: E402

# préfixe de style commun à toutes les textures — Cube World, plat, pas de photoréalisme
# (v2 : "top-down view" + "voxel" faisaient trop souvent dériver SD1.5 vers une scène
# isométrique complète plutôt qu'un swatch de matériau — reformulé en macro/texture pure)
STYLE_PREFIX = (
    "seamless tileable texture swatch, close-up macro material sample, "
    "flat stylized game texture, Cube World inspired game art, "
    "clean saturated flat colors, painterly cel-shaded surface, "
    "subtle organic paint grain, single uniform material, repeating pattern, "
    "no scene, no landscape, no objects"
)

# négatif générique : pas de sujet/scène/paysage isométrique, pas de photoréalisme,
# pas de bruit type Minecraft, pas de motif ornemental/mosaïque
NEG_DEFAULT = (
    "character, person, people, face, figure, creature, animal, "
    "isometric scene, landscape, terrain, aerial view, bird's eye view, map, "
    "diorama, miniature scene, voxel blocks, cubes, buildings, houses, trees, "
    "plants, bushes, water pool, lake scene, sky, horizon, composition, "
    "multiple different materials, patchwork, collage, grid lines, seams, "
    "ornate carving, mosaic, decorative tile pattern, "
    "blurry, watermark, signature, text, logo, border, frame, vignette, "
    "lowres, photorealistic, photo, hyperrealistic, realistic, 3d render, "
    "cinematic lighting, harsh shadows, high frequency noise, jpeg artifacts, "
    "minecraft blocky pixelated noise"
)

# palette validée par la recherche visuelle Aincrad x Cube World du projet — ne pas dévier
MATERIALS = [
    {
        "name": "herbe",
        "prompt": "seamless grass texture, sage green desaturated grass blades, "
                  "painted meadow surface, uniform texture",
        "negative": "flowers, mushrooms, rocks, dirt patches, realistic grass blades, mud, "
                    "distinct horizontal bands, gradient stripes, multiple tones layered",
        "target_material": "MI_Grass",
    },
    {
        "name": "pierre_claire",
        "prompt": "seamless pale beige cream sandstone paving texture, smooth flat stone "
                  "slabs, simple stone paving pattern",
        "negative": "ornate carving, decorative tile, faces, figures, diamond pattern, "
                    "dark grout lines, gothic pattern, cracks, moss, dirt, realistic marble veining",
        "target_material": "MI_Path (rue de la ville)",
    },
    {
        "name": "pierre_sombre",
        "prompt": "seamless dark slate ardoise stone wall texture, dark blue-grey stone "
                  "blocks, flat stone wall surface",
        "negative": "landscape, terrain, voxel blocks scene, cubes, green, water, grass, "
                    "bright colors, moss, realistic granite texture",
        "target_material": "MI_TowerStone (coque Aincrad / tour du Labyrinthe)",
    },
    {
        "name": "bois_clair",
        "prompt": "seamless light honey wood plank texture, pale warm wood beams, "
                  "timber framing, windmill wood",
        "negative": "dark wood, knots, varnish reflections, realistic wood grain",
        "target_material": "MI_Wall (charpente / moulins)",
    },
    {
        "name": "toit_terracotta",
        "prompt": "seamless terracotta clay roof tile texture, warm orange-red "
                  "overlapping roof tiles, rows of curved tiles",
        "negative": "diamond pattern, green tiles, mosaic, patchwork, checkerboard, "
                    "moss, snow, realistic clay texture",
        "target_material": "MI_Roof",
    },
    {
        "name": "terre",
        "prompt": "seamless warm brown dirt path texture, packed earth surface, "
                  "uniform brown soil",
        "negative": "plants, bushes, arrows, symbols, compass, cross pattern, green, "
                    "rocks, footprints, puddles, realistic mud texture",
        "target_material": "MI_Path (chemin)",
    },
    {
        "name": "pierre_noire",
        "prompt": "seamless very dark black matte stone texture, deep black stone "
                  "blocks, obsidian black matte surface, near-black charcoal tone",
        "negative": "beige, tan, light grey, ivory, bright stone, sandstone color, "
                    "shiny reflections, glossy, cracks, realistic obsidian texture",
        "target_material": "MI_BlackIron (nouveau — Black Iron Palace)",
    },
    {
        "name": "eau",
        "prompt": "seamless abstract stylized water surface texture, blue-grey toon "
                  "water ripples, flat shaded water pattern",
        "negative": "island, shore, land, trees, aerial map, landscape, bird's eye view "
                    "scene, camouflage pattern, random color blobs, "
                    "realistic reflections, foam, waves, transparent glass look",
        "target_material": "MI_Water (nouveau — lac)",
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="outputs/textures/decor")
    ap.add_argument("--model", default="sd-legacy/stable-diffusion-v1-5",
                     help="repo HF ou chemin local du checkpoint")
    ap.add_argument("--lora", default=None, help="chemin .safetensors d'un LoRA (optionnel)")
    ap.add_argument("--lora-scale", type=float, default=0.8)
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--cfg", type=float, default=7.5)
    ap.add_argument("--size", type=int, default=512, help="512 ou 768 max (VRAM limitée)")
    ap.add_argument("--variants", type=int, default=2, help="nombre de variantes par matériau")
    ap.add_argument("--seed-base", type=int, default=1000)
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

    # économies VRAM (Turing 8 Go) — mêmes réglages que step1_concept.py
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    if device == "cuda":
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(device)

    if args.lora and os.path.exists(args.lora):
        print(f"[*] LoRA : {args.lora} (scale {args.lora_scale})")
        pipe.load_lora_weights(args.lora)
        pipe.fuse_lora(lora_scale=args.lora_scale)

    os.makedirs(args.out_dir, exist_ok=True)
    vram.report("SD pret")

    log_entries = []
    seed_counter = args.seed_base
    n_total = len(MATERIALS) * args.variants
    i = 0
    for mat in MATERIALS:
        full_prompt = f"{STYLE_PREFIX}, {mat['prompt']}"
        full_negative = f"{NEG_DEFAULT}, {mat['negative']}"
        for v in range(1, args.variants + 1):
            i += 1
            seed = seed_counter
            seed_counter += 1
            gen = torch.Generator(device="cpu").manual_seed(seed)
            fname = f"{mat['name']}_{v:02d}.png"
            fpath = os.path.join(args.out_dir, fname)
            print(f"[{i}/{n_total}] Génération {fname} (seed={seed})...")
            image = pipe(
                prompt=full_prompt,
                negative_prompt=full_negative,
                num_inference_steps=args.steps,
                guidance_scale=args.cfg,
                width=args.size,
                height=args.size,
                generator=gen,
            ).images[0]
            image.save(fpath)
            print(f"[OK] -> {fpath}")
            log_entries.append({
                "file": fname,
                "material": mat["name"],
                "target_material": mat["target_material"],
                "prompt": full_prompt,
                "negative": full_negative,
                "seed": seed,
                "size": args.size,
                "steps": args.steps,
                "cfg": args.cfg,
            })

    del pipe
    vram.free()

    log_path = os.path.join(args.out_dir, "_generation_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, ensure_ascii=False, indent=2)
    print(f"[OK] Log -> {log_path}")
    print(f"[TERMINE] {n_total} textures générées dans {args.out_dir}")


if __name__ == "__main__":
    main()
