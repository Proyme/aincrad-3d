"""Test gratuit : Hunyuan3D-2 sur HF Space (calcul cote Hugging Face, pas le PC)."""
import os
import shutil
import time
from gradio_client import Client, handle_file

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "cloud")
os.makedirs(OUT, exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), "..", "inputs", "concept_v2.png")

print("[*] Connexion au Space tencent/Hunyuan3D-2 ...")
c = Client("tencent/Hunyuan3D-2", verbose=False)
t0 = time.time()
print("[*] Appel /generation_all (forme + texture) ...")
res = c.predict(
    caption=None,
    image=handle_file(IMG),
    mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
    steps=30, guidance_scale=5.0, seed=1234, octree_resolution=256,
    check_box_rembg=True, num_chunks=8000, randomize_seed=True,
    api_name="/generation_all",
)
print(f"[OK] Termine en {time.time()-t0:.1f}s")
print("[*] Resultat brut:", res)

# res = (file, file, output_html, mesh_stats, seed) -> on copie les meshes
n = 0
for item in res:
    if isinstance(item, str) and os.path.exists(item) and item.lower().endswith((".glb", ".obj", ".ply")):
        dst = os.path.join(OUT, f"hunyuan_space_{n}{os.path.splitext(item)[1]}")
        shutil.copy(item, dst)
        print(f"[OK] Mesh -> {dst}")
        n += 1
print(f"[OK] {n} mesh(es) recupere(s).")
