"""Sonde les HF Spaces gratuits (API gradio) — découvre les endpoints disponibles."""
from gradio_client import Client

SPACES = [
    "tencent/Hunyuan3D-2",
    "tencent/Hunyuan3D-2.1",
    "trellis-community/TRELLIS",
    "JeffreyXiang/TRELLIS",
]

for sp in SPACES:
    print("=" * 70)
    print(f"SPACE: {sp}")
    try:
        c = Client(sp, verbose=False)
        api = c.view_api(return_format="dict")
        named = api.get("named_endpoints", {})
        print(f"  OK — {len(named)} endpoints nommes:")
        for name, info in list(named.items())[:12]:
            params = [p.get("python_type", {}).get("type", "?") for p in info.get("parameters", [])]
            print(f"    {name}  ({len(params)} params)")
    except Exception as e:
        print(f"  ECHEC: {type(e).__name__}: {str(e)[:200]}")
