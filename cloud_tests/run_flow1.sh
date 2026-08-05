#!/usr/bin/env bash
export PATH=/usr/local/cuda/bin:$PATH
cd /workspace
python -u pod_batch_gen_hq.py --indir /workspace/inputs_hq --outdir /workspace/outputs_hq --octree 256 > /workspace/hq.log 2>&1
