"""Déploiement RunPod via REST API (https://rest.runpod.io/v1).

Cycle de vie d'un pod GPU : create -> wait running -> infos SSH -> terminate.
La clé API est lue dans la variable d'env RUNPOD_API_KEY (jamais écrite sur disque).

Usage :
    set RUNPOD_API_KEY=...                      (PowerShell : $env:RUNPOD_API_KEY="...")
    python runpod_deploy.py create  --pubkey "ssh-ed25519 AAAA..."  --gpu "NVIDIA A100 80GB PCIe"
    python runpod_deploy.py status  --id <podId>
    python runpod_deploy.py terminate --id <podId>
"""
import argparse
import json
import os
import sys
import time
import requests

BASE = "https://rest.runpod.io/v1"
# image devel = contient nvcc (CUDA 12.4) pour compiler le texgen Hunyuan
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"

# liste de priorité : on prend le 1er GPU disponible
GPU_PRIORITY = [
    "NVIDIA A100 80GB PCIe",
    "NVIDIA A100-SXM4-80GB",
    "NVIDIA L40S",
]


def headers():
    key = os.environ.get("RUNPOD_API_KEY")
    if not key:
        sys.exit("ERREUR: variable d'env RUNPOD_API_KEY absente.")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def create(pubkey, gpu=None):
    body = {
        "name": "hunyuan3d-batch",
        "imageName": IMAGE,
        "cloudType": "SECURE",
        "computeType": "GPU",
        "gpuTypeIds": [gpu] if gpu else GPU_PRIORITY,
        "gpuCount": 1,
        "gpuTypePriority": "availability",
        "containerDiskInGb": 80,
        "volumeInGb": 60,
        "volumeMountPath": "/workspace",
        "ports": ["22/tcp", "8888/http"],
        "env": {"PUBLIC_KEY": pubkey},
    }
    r = requests.post(f"{BASE}/pods", headers=headers(), json=body, timeout=60)
    r.raise_for_status()
    pod = r.json()
    print("POD_ID:", pod.get("id"))
    print(json.dumps(pod, indent=2)[:1500])
    return pod


def get(pod_id):
    r = requests.get(f"{BASE}/pods/{pod_id}", headers=headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def wait_running(pod_id, budget_min=15):
    """Attend RUNNING + IP/port SSH publics. Stoppe si dépassement budget temps."""
    t0 = time.time()
    while time.time() - t0 < budget_min * 60:
        pod = get(pod_id)
        status = pod.get("desiredStatus") or pod.get("lastStatusChange")
        runtime = pod.get("runtime") or {}
        ports = runtime.get("ports") or []
        ssh = next((p for p in ports if str(p.get("privatePort")) == "22" and p.get("isIpPublic")), None)
        print(f"[wait] status={status} ports={len(ports)}")
        if ssh:
            print(f"SSH: ssh root@{ssh['ip']} -p {ssh['publicPort']}")
            return pod
        time.sleep(10)
    print("[!] Timeout — pod pas prêt dans le budget.")
    return None


def terminate(pod_id):
    r = requests.delete(f"{BASE}/pods/{pod_id}", headers=headers(), timeout=60)
    print("terminate:", r.status_code)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["create", "status", "wait", "terminate", "gpus"])
    ap.add_argument("--id")
    ap.add_argument("--pubkey")
    ap.add_argument("--gpu")
    a = ap.parse_args()

    if a.action == "create":
        if not a.pubkey:
            sys.exit("--pubkey requis")
        pod = create(a.pubkey, a.gpu)
    elif a.action == "status":
        print(json.dumps(get(a.id), indent=2)[:2000])
    elif a.action == "wait":
        wait_running(a.id)
    elif a.action == "terminate":
        terminate(a.id)
