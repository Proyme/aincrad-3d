@echo off
REM Build texgen native modules for Hunyuan (RTX 2070 / sm_75)
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
set "CUDA_HOME=%CUDA_PATH%"
set "PATH=%CUDA_PATH%\bin;%PATH%"
set "TORCH_CUDA_ARCH_LIST=7.5"
set "DISTUTILS_USE_SDK=1"
set "NVCC_PREPEND_FLAGS=-allow-unsupported-compiler"
set "PY=C:\Users\jules\Desktop\recherches 3d perso\.venv\Scripts\python.exe"

echo === nvcc ===
nvcc --version | findstr release

echo === Build custom_rasterizer ===
cd /d "C:\Users\jules\Desktop\recherches 3d perso\third_party\Hunyuan3D-2\hy3dgen\texgen\custom_rasterizer"
"%PY%" setup.py install
if errorlevel 1 (echo CUSTOM_RASTERIZER_FAILED) else (echo CUSTOM_RASTERIZER_OK)

echo === Build differentiable_renderer ===
cd /d "C:\Users\jules\Desktop\recherches 3d perso\third_party\Hunyuan3D-2\hy3dgen\texgen\differentiable_renderer"
"%PY%" setup.py install
if errorlevel 1 (echo DIFF_RENDERER_FAILED) else (echo DIFF_RENDERER_OK)

echo BUILD_DONE
