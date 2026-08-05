# Processus RunPod — déploiement + génération 3D en batch

Génère des persos 3D **texturés en batch** sur un GPU 80 Go loué (A100/H100),
puis rapatrie les `.glb` sur le PC. Concepts générés en local (gratuit) → batch
lourd (forme+texture 2048) dans le cloud.

## Prérequis
- **Clé API RunPod** dans `RUNPOD_API_KEY` (env, jamais sur disque). À révoquer après.
- Crédits sur le compte RunPod.

## GPU cible
`NVIDIA A100 80GB PCIe` (priorité `availability` : bascule sur SXM/H100/L40S si indispo).
80 Go = texture 2048 sans thrash + batch + GPU exploité à fond.

## Flux (orchestré depuis le PC)

```
1. [local]  Générer/choisir N concepts -> inputs_cloud/*.png   (étape SD locale, gratuite)
2. [local]  ssh-keygen -> clé dédiée runpod
3. [API]    runpod_deploy.py create --pubkey "<pub>"           # crée le pod (DÉBUT facturation)
4. [API]    runpod_deploy.py wait   --id <podId>               # attend RUNNING + SSH
5. [scp]    pousser : remote_bootstrap.sh, pod_batch_gen.py, inputs_cloud/*  -> pod:/workspace
6. [ssh]    bash /workspace/remote_bootstrap.sh                # install Hunyuan + compile texgen
7. [ssh]    python /workspace/pod_batch_gen.py                 # BATCH forme+texture
8. [scp]    rapatrier pod:/workspace/outputs/*.glb -> outputs/cloud/
9. [API]    runpod_deploy.py terminate --id <podId>            # FIN facturation (impératif)
10.[local]  rendu Blender + contrôle qualité
```

## Commandes concrètes (exemples)
```powershell
$env:RUNPOD_API_KEY = "..."
ssh-keygen -t ed25519 -f .\runpod_key -N '""'
$pub = Get-Content .\runpod_key.pub
python cloud_tests\runpod_deploy.py create --pubkey "$pub"     # note le POD_ID
python cloud_tests\runpod_deploy.py wait --id <POD_ID>         # note IP + port SSH
# upload
scp -i runpod_key -P <port> cloud_tests\remote_bootstrap.sh cloud_tests\pod_batch_gen.py root@<ip>:/workspace/
scp -i runpod_key -P <port> -r inputs_cloud\* root@<ip>:/workspace/inputs/
# run
ssh -i runpod_key -p <port> root@<ip> "bash /workspace/remote_bootstrap.sh && python /workspace/pod_batch_gen.py"
# download
scp -i runpod_key -P <port> -r root@<ip>:/workspace/outputs/* outputs\cloud\
# stop facturation
python cloud_tests\runpod_deploy.py terminate --id <POD_ID>
```

## Garde-fous coût
- A100 80 Go ≈ **1,2–1,8 $/h**. Session test (setup ~10-15 min + batch) ≈ **0,5–1,5 $**.
- **Terminer le pod systématiquement** en fin de run (idle facturé sinon).
- Plafond : si setup/run dépasse le budget convenu, on `terminate` et on debug à froid.
```
