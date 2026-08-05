"""Helpers de gestion VRAM — critique sur 8 Go (RTX 2070).

Règle d'or : un seul gros modèle en VRAM à la fois. Charger -> utiliser ->
décharger -> empty_cache avant l'étape suivante.
"""
import gc
import torch


def free():
    """Libère la VRAM (à appeler entre deux étapes lourdes)."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def report(tag=""):
    """Affiche l'usage VRAM courant."""
    if torch.cuda.is_available():
        used = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        print(f"[VRAM {tag}] alloue={used:.2f} Go | reserve={reserved:.2f} Go")


def device_dtype(cfg):
    """Retourne (device, dtype) en respectant la contrainte Turing (fp16)."""
    use_cuda = cfg["hardware"]["device"] == "cuda" and torch.cuda.is_available()
    device = "cuda" if use_cuda else "cpu"
    dtype = torch.float16 if (use_cuda and cfg["hardware"]["dtype"] == "float16") else torch.float32
    return device, dtype
