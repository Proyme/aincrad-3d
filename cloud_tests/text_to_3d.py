"""Workflow TEXTE -> personnage 3D (le plus efficace pour un asset jouable).

Etapes :
  1. [local, gratuit] texte -> concept image (SD + prompt parfait Genshin de config.yaml)
  2. [pod RunPod]      concept -> mesh 3D HQ texture (Hunyuan-2 octree 512)
  3. [local]          download .glb + rendu

Pourquoi local pour le concept : gratuit/illimité, et on CURE l'image avant de
payer la 3D (on rejette les ratés pour quelques secondes).

Usage :
    python cloud_tests/text_to_3d.py --prompt "long mint hair, white teal dress, ..." --name perso1
    # plusieurs persos :
    python cloud_tests/text_to_3d.py --batch prompts.txt   (1 ligne = 1 perso "name | prompt")
"""
import argparse, os, subprocess, sys, yaml

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
POD = "root@103.196.86.39"
PORT = "50466"
KEY = os.path.join(HERE, "runpod_key")
SSHOPT = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL", "-o", "LogLevel=ERROR"]


def cfg():
    with open(os.path.join(ROOT, "config.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def gen_concept(name, subject, c):
    out = os.path.join(ROOT, "inputs", f"{name}.png")
    full = f"{subject}, {c['concept']['style_suffix']}"
    neg = c["concept"].get("negative_extra", "")
    cmd = [sys.executable, os.path.join(ROOT, "src", "step1_concept.py"),
           "--prompt", full, "--negative", neg, "--out", out,
           "--model", c["concept"]["model"], "--steps", str(c["concept"]["steps"]),
           "--cfg", str(c["concept"]["cfg"]), "--width", str(c["concept"]["width"]),
           "--height", str(c["concept"]["height"])]
    if c["concept"].get("lora"):
        cmd += ["--lora", c["concept"]["lora"], "--lora-scale", str(c["concept"]["lora_scale"])]
    subprocess.run(cmd, check=True)
    return out


def to_pod_3d(concept_paths):
    """Upload concepts -> HQ gen sur le pod -> download .glb."""
    base = ["ssh", "-i", KEY, "-p", PORT, *SSHOPT, POD]
    subprocess.run(base + ["mkdir -p /workspace/inputs_hq /workspace/outputs_hq"], check=True)
    for p in concept_paths:
        subprocess.run(["scp", "-i", KEY, "-P", PORT, *SSHOPT, p, f"{POD}:/workspace/inputs_hq/"], check=True)
    subprocess.run(["scp", "-i", KEY, "-P", PORT, *SSHOPT,
                    os.path.join(HERE, "pod_batch_gen_hq.py"), f"{POD}:/workspace/"], check=True)
    subprocess.run(base + ["export PATH=/usr/local/cuda/bin:$PATH; cd /workspace && "
                           "python -u pod_batch_gen_hq.py --indir /workspace/inputs_hq "
                           "--outdir /workspace/outputs_hq --octree 512"], check=True)
    dst = os.path.join(ROOT, "outputs", "runpod_batch")
    os.makedirs(dst, exist_ok=True)
    subprocess.run(["scp", "-i", KEY, "-P", PORT, *SSHOPT,
                    f"{POD}:/workspace/outputs_hq/*.glb", dst], check=True)
    print(f"[OK] meshes HQ -> {dst}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt")
    ap.add_argument("--name", default="perso")
    ap.add_argument("--batch", help="fichier: 'name | prompt' par ligne")
    ap.add_argument("--concept-only", action="store_true", help="s'arrete apres le concept (curation)")
    a = ap.parse_args()
    c = cfg()

    jobs = []
    if a.batch:
        for line in open(a.batch, encoding="utf-8"):
            line = line.strip()
            if line and "|" in line:
                n, p = line.split("|", 1)
                jobs.append((n.strip(), p.strip()))
    elif a.prompt:
        jobs.append((a.name, a.prompt))
    else:
        sys.exit("--prompt ou --batch requis")

    concepts = [gen_concept(n, p, c) for n, p in jobs]
    print(f"[*] {len(concepts)} concept(s) generes:", *concepts, sep="\n  ")
    if a.concept_only:
        print("[i] --concept-only : curation avant la 3D. Relance sans le flag pour la 3D.")
        return
    to_pod_3d(concepts)


if __name__ == "__main__":
    main()
