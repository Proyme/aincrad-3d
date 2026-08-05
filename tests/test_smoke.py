"""Tests de fumée — vérifient que l'environnement et les briques de base
chargent sans erreur (et sans OOM) sur la RTX 2070.

Lancer :
    .\.venv\Scripts\python.exe -m pytest tests/test_smoke.py -v
    # ou simplement :
    .\.venv\Scripts\python.exe tests/test_smoke.py
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_torch_cuda():
    import torch
    assert torch.cuda.is_available(), "CUDA indisponible — vérifier le build PyTorch cu12x"
    name = torch.cuda.get_device_name(0)
    print(f"GPU : {name}")


def test_fp16_supported():
    """Turing supporte fp16 (mais pas bf16 nativement)."""
    import torch
    x = torch.randn(8, 8, device="cuda", dtype=torch.float16)
    y = (x @ x).sum().item()
    assert y == y  # pas NaN


def test_imports_pipeline():
    """Les dépendances clés des étapes s'importent."""
    import trimesh  # noqa
    import mcubes  # noqa  (PyMCubes — marching cubes sans compilation)
    import rembg  # noqa
    import diffusers  # noqa
    import transformers  # noqa


def test_triposr_available():
    sys.path.insert(0, os.path.join(ROOT, "third_party", "TripoSR"))
    from tsr.system import TSR  # noqa


def test_config_loads():
    import yaml
    with open(os.path.join(ROOT, "config.yaml"), encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["hardware"]["dtype"] == "float16"  # contrainte Turing
    assert cfg["image_to_3d"]["backend"] in ("triposr", "hunyuan3d")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"[OK]   {name}")
            except Exception as e:
                failures += 1
                print(f"[FAIL] {name} : {e}")
    print(f"\n{'TOUS OK' if not failures else str(failures) + ' échec(s)'}")
    sys.exit(1 if failures else 0)
