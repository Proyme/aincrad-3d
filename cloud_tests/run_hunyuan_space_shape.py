"""Test gratuit Hunyuan3D-2 HF Space — forme seule (quota ZeroGPU plus court)."""
import os, shutil, time
from gradio_client import Client, handle_file

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "cloud")
os.makedirs(OUT, exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), "..", "inputs", "concept_v2.png")

c = Client("tencent/Hunyuan3D-2", verbose=False)
t0 = time.time()
print("[*] /shape_generation ...")
res = c.predict(
    caption=None, image=handle_file(IMG),
    mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
    steps=30, guidance_scale=5.0, seed=1234, octree_resolution=256,
    check_box_rembg=True, num_chunks=8000, randomize_seed=True,
    api_name="/shape_generation",
)
print(f"[OK] {time.time()-t0:.1f}s")
n = 0
for item in res:
    if isinstance(item, str) and os.path.exists(item) and item.lower().endswith((".glb", ".obj", ".ply")):
        dst = os.path.join(OUT, f"hunyuan_space_shape{os.path.splitext(item)[1]}")
        shutil.copy(item, dst); print(f"[OK] Mesh -> {dst}"); n += 1
print(f"[OK] {n} mesh(es).")
