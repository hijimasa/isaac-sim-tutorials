---
title: Isaac Lab Setup
---

# Isaac Lab Setup (Linux / Windows)

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! note "How much setup do you need?"
    The demos in [Tutorial 1](01_policy_deployment.md) and all of Tutorials 2–3 run with **Isaac Sim alone** — no Isaac Lab install required. Installing Isaac Lab is only needed to train/export policies yourself.

## Requirements

| Item | Requirement |
|---|---|
| OS | Ubuntu 22.04 (x64) / Windows 11 (x64) |
| Python | 3.11 (matching Isaac Sim 5.x) |
| Isaac Sim | 5.1.0 recommended |
| RAM / VRAM | 32 GB / 16 GB+ |

Unlike ROS 2, **Isaac Lab runs natively on Windows 11** — no WSL needed. Differences are just `isaaclab.bat` vs `./isaaclab.sh` and backslash paths. (Deploying policies via ROS 2 on Windows still requires WSL2 — see [ROS 2 Setup](../ros/00_setup.md).)

## Pip installation (recommended)

```bash
# 1. Python 3.11 environment
conda create -n env_isaaclab python=3.11
conda activate env_isaaclab

# 2. Isaac Sim + PyTorch
pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

# 3. Isaac Lab
git clone https://github.com/isaac-sim/IsaacLab.git --branch main
cd IsaacLab
./isaaclab.sh --install        # Windows: isaaclab.bat --install

# 4. Verify
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py   # Windows: isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py
```

Other install methods (binary + source, full source, pip-only) are described in the [official installation guide](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html).

## Next Steps

- [Tutorial 1: Policy Deployment](01_policy_deployment.md)
