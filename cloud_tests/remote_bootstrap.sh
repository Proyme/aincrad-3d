#!/usr/bin/env bash
# S'execute SUR le pod RunPod (Linux, CUDA devel). Installe Hunyuan3D + texgen.
set -e
export PATH=/usr/local/cuda/bin:$PATH
export TORCH_CUDA_ARCH_LIST="8.9"   # L40S = Ada sm_89 (A100 = 8.0)
cd /workspace

echo "=== GPU / CUDA ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
nvcc --version | grep release || echo "WARN nvcc absent"

echo "=== Clone Hunyuan3D-2 ==="
[ -d Hunyuan3D-2 ] || git clone --depth 1 https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git
cd Hunyuan3D-2

echo "=== Deps Python ==="
pip install -q -r requirements.txt
pip install -q gradio_client trimesh pymeshlab pygltflib xatlas

echo "=== Patch trust_remote_code (diffusers recent) ==="
sed -i 's/custom_pipeline=custom_pipeline_path, torch_dtype=torch.float16)/custom_pipeline=custom_pipeline_path, torch_dtype=torch.float16, trust_remote_code=True)/' hy3dgen/texgen/utils/multiview_utils.py || true

echo "=== Build texgen (Linux, compile direct) ==="
pip install -q -e . || true
( cd hy3dgen/texgen/custom_rasterizer && python setup.py install )
( cd hy3dgen/texgen/differentiable_renderer && python setup.py install )

echo "=== Bootstrap OK ==="
