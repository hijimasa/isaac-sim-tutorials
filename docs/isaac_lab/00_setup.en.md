---
title: Isaac Lab Setup
---

# Isaac Lab Setup (Linux / Windows)

## About This Page

This page collects the **setup steps** for the Isaac Lab tutorial series. From the [official Isaac Lab installation guide](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html), it covers the **pip method** recommended for new setups and the **binary method (Binary + Source)** for people who already use a binary installation of Isaac Sim, organized so that the differences between Linux and Windows are easy to see.

!!! note "How much setup do you need?"
    The Isaac Lab tutorials on this site require different environments depending on the page:

    - The **demo run (Step 1)** of [Tutorial 1: Policy Deployment](01_policy_deployment.md), [Tutorial 2: Getting Started with Cloner](02_cloner.md), and [Tutorial 3: Instanceable Assets](03_instanceable_assets.md) — these run with **Isaac Sim alone**. No Isaac Lab installation is required.
    - Running the **training / export (Step 2)** of [Tutorial 1](01_policy_deployment.md) yourself — this **requires installing Isaac Lab** (the steps on this page).

## Supported Platforms and Requirements

| Item | Requirement |
|---|---|
| OS | Ubuntu 22.04 (Linux x64) / Windows 11 (x64) |
| Python | **3.11** (matching Isaac Sim 5.x) |
| Isaac Sim | 5.1.0 recommended (support for 4.2.0 and earlier has ended) |
| RAM | 32 GB or more |
| GPU VRAM | 16 GB or more recommended |

!!! note "No WSL needed on Windows (runs natively)"
    Unlike ROS 2, **Isaac Lab runs natively on Windows 11**. The only differences from Linux are that the script is `isaaclab.bat` instead of `isaaclab.sh`, and that paths use backslashes (`\`).

    However, if you later move on to **deploying trained policies via ROS 2** ([ROS 2 tutorials](../ros/index.md)), Windows requires ROS 2 running on WSL2. See [ROS 2 Setup](../ros/00_setup.md).

## Choosing an Installation Method

There are four official methods. This page explains the first two (pip and binary) with switchable tabs:

| Method | Description | Best for |
|---|---|---|
| **pip + source (recommended)** | Install Isaac Sim via pip and get Isaac Lab from GitHub | First-time Isaac Lab setups → the "Pip method" tab on this page |
| **Binary + source** | Use an existing official Isaac Sim binary and install Isaac Lab from source | People already using a binary Isaac Sim → the "Binary method" tab on this page |
| Full source build | Build both from source | Developers modifying Isaac Sim itself (see the [official guide](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)) |
| pip only | Both as pip packages | External extension use only (the learning samples are not available) |

!!! note "Which tab should you pick?"
    If you have been following the other chapters of this site (e.g. [Core API](../core_api/index.md)) with a standalone (zip) Isaac Sim downloaded via the [Isaac Sim Quick Install](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/quick-install.html), use the **"Binary method" tab**. Running the pip steps as-is would install a separate pip version of Isaac Sim, leaving you with a duplicate installation.

## Installation Steps

=== "Pip method (recommended for new setups)"

    This method installs Isaac Sim itself as a pip package inside a Python virtual environment.

    **1. Create a Python 3.11 virtual environment**

    Using conda (recommended, same on Linux / Windows):

    ```bash
    conda create -n env_isaaclab python=3.11
    conda activate env_isaaclab
    ```

    Using venv (Linux):

    ```bash
    python3.11 -m venv env_isaaclab
    source env_isaaclab/bin/activate
    ```

    Using venv (Windows):

    ```bat
    python3.11 -m venv env_isaaclab
    env_isaaclab\Scripts\activate
    ```

    **2. Install Isaac Sim and PyTorch**

    Same on Linux / Windows:

    ```bash
    pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
    pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
    ```

    **3. Clone and install the Isaac Lab repository**

    Same on Linux / Windows:

    ```bash
    git clone https://github.com/isaac-sim/IsaacLab.git --branch main
    cd IsaacLab
    ```

    Linux:

    ```bash
    ./isaaclab.sh --install
    ```

    Windows:

    ```bat
    isaaclab.bat --install
    ```

    !!! note "Run everything inside the virtual environment from here on"
        Whenever you run `isaaclab.sh` / `isaaclab.bat`, always use a terminal with this virtual environment activated (e.g. `conda activate env_isaaclab`).

=== "Binary method (using an existing binary Isaac Sim)"

    This method adds Isaac Lab from source to an environment that already has the standalone (zip) Isaac Sim 5.1.0 installed.

    !!! note "No virtual environment or pip install needed"
        The binary Isaac Sim ships with its own Python 3.11 and PyTorch, and `isaaclab.sh` / `isaaclab.bat` uses them automatically. **Do not run** the virtual environment creation or the `pip install isaacsim...` / `pip install torch...` steps from the pip method (doing so would give you a duplicate Isaac Sim installation).

    **1. Clone the Isaac Lab repository**

    ```bash
    git clone https://github.com/isaac-sim/IsaacLab.git --branch main
    cd IsaacLab
    ```

    **2. Create a symbolic link to Isaac Sim**

    In the root of the IsaacLab repository, create a link named `_isaac_sim` pointing to your binary Isaac Sim installation directory. This lets `isaaclab.sh` / `isaaclab.bat` find the bundled Python environment and the Isaac Sim extensions.

    Linux (assuming the installation is at `~/isaacsim`):

    ```bash
    ln -s ${HOME}/isaacsim _isaac_sim
    ```

    Windows (assuming the installation is at `C:\isaacsim`) — in a PowerShell **launched as administrator**:

    ```powershell
    New-Item -ItemType SymbolicLink -Path _isaac_sim -Target C:\isaacsim
    ```

    If `New-Item` does not work for you, the link can also be created with the Command Prompt (cmd) `mklink` command used in the [official documentation](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/binaries_installation.html):

    ```bat
    mklink /D _isaac_sim C:\isaacsim
    ```

    !!! warning "Notes on creating symbolic links on Windows"
        - Creating a symbolic link generally requires **administrator privileges**. Open PowerShell / Command Prompt with "Run as administrator" before running the command.
        - `mklink` is a built-in of the Command Prompt (cmd) only — **running it in PowerShell fails with a "'mklink' is not recognized" error**. Be sure to run it from a Command Prompt.
        - If Windows "Developer Mode" is enabled, cmd's `mklink` works without administrator privileges (Windows PowerShell 5.1's `New-Item` still requires administrator privileges even with Developer Mode).

    **3. Install Isaac Lab**

    Linux:

    ```bash
    ./isaaclab.sh --install
    ```

    Windows:

    ```powershell
    ./isaaclab.bat --install
    ```

## Verifying the Installation

The commands from here on are the same for both methods (for the pip method, run them in a terminal with the virtual environment activated). If an empty scene launches, the installation succeeded. The first launch takes a while due to asset downloads and similar one-time work.

**Linux:**

```bash
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```

**Windows:**

```powershell
./isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py
```

## Example Training Run

Once installed, you can train the H1 flat-terrain locomotion policy used in [Tutorial 1: Policy Deployment](01_policy_deployment.md):

**Linux:**

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

**Windows:**

```powershell
./isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

!!! warning "Known issue (Windows): launch fails with an h5py DLL load error"
    On Windows, the launch may fail with `Windows fatal exception: code 0xc0000139` and an error like the following while loading `isaaclab_tasks`:

    ```
    ImportError: DLL load failed while importing _errors: The specified procedure could not be found.
    ```

    This is a known conflict between h5py 3.16.0+ and the HDF5 DLLs bundled with Isaac Sim ([isaac-sim/IsaacLab #5076](https://github.com/isaac-sim/IsaacLab/issues/5076)). Downgrading h5py to 3.15.1 from the root of the IsaacLab repository resolves it:

    ```powershell
    ./isaaclab.bat -p -m pip install h5py==3.15.1
    ```

    (On Linux: `./isaaclab.sh -p -m pip install h5py==3.15.1`)

!!! warning "Known issue (Windows): the training script crashes with a tensordict access violation"
    Launching the rsl_rl training script may crash with `Windows fatal exception: access violation` while importing `tensordict` (the traceback shows `site-packages\tensordict\utils.py`).

    This is a known issue caused by the tensordict 0.12 series (released April 2026) being binary-incompatible with the PyTorch 2.7.0 bundled with Isaac Sim 5.1.0 ([isaac-sim/IsaacLab #5393](https://github.com/isaac-sim/IsaacLab/issues/5393), [Discussion #5373](https://github.com/isaac-sim/IsaacLab/discussions/5373)). Downgrading tensordict to a pre-0.12 version resolves it:

    ```powershell
    ./isaaclab.bat -p -m pip install tensordict==0.11.0
    ```

    (On Linux: `./isaaclab.sh -p -m pip install tensordict==0.11.0`. If this does not resolve it, downgrade to `tensordict==0.9.0` and reinstall rsl-rl-lib with `./isaaclab.bat -p -m pip install --force-reinstall rsl-rl-lib`.)

!!! tip "Troubleshooting"
    If you run into problems during installation or launch, see the [official Isaac Lab troubleshooting guide](https://isaac-sim.github.io/IsaacLab/main/source/refs/troubleshooting.html).

## Next Steps

- [Tutorial 1: Policy Deployment](01_policy_deployment.md) - Run a trained policy in Isaac Sim.
