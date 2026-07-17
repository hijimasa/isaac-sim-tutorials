---
title: ROS 2 Setup
---

# ROS 2 Setup (Linux / Windows)

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

This page consolidates the setup required for the ROS 2 tutorial series, based on the official [ROS 2 Installation (Default)](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html) (Ubuntu 24.04 + Jazzy) and [ROS 2 Installation (Other Platforms)](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros_other_platforms.html) (Ubuntu 22.04 / Windows) guides.

!!! warning "Windows users: Pixi-based native ROS 2 is now officially supported"
    Isaac Sim 6.0 officially supports ROS 2 Jazzy natively on Windows 11 via the **Pixi workspace** in [IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) (RoboStack conda packages, Zenoh middleware). WSL2 is no longer required and all ROS 2 tutorials are supported. The legacy **WSL2 method is deprecated** (custom ROS interfaces are not supported there).

## Supported platforms

| Platform | ROS 2 |
|---|---|
| Ubuntu 24.04 | Jazzy (recommended, default configuration) |
| Ubuntu 22.04 | Humble, Jazzy (source build) — see Other Platforms |
| Windows 11 | Jazzy (**Pixi**), Humble / Jazzy (WSL2, deprecated) |

!!! note "Isaac Sim 6.0 uses Python 3.12"
    Ubuntu 24.04 / ROS 2 Jazzy also uses Python 3.12, so the default workflow is now to **source your native ROS 2 (and workspace) and launch Isaac Sim from the same terminal**. If nothing is sourced, the internal ROS 2 Jazzy libraries load automatically. Experimental: other natively installed distros may also work when sourced.

## Linux (Ubuntu 24.04 + Jazzy)

1. Install ROS 2 Jazzy per the official docs. Optional: `ros-jazzy-vision-msgs`, `ros-jazzy-ackermann-msgs`.
2. Build the [IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) `jazzy_ws` (`rosdep install --rosdistro jazzy` + `colcon build`) and source it. Note: the `isaacsim` package was renamed to **`isaacsim_bringup`** in 6.0 (`ros2 launch isaacsim_bringup ...`); a new `isaac_compressed_image_decoder` package was added.
3. Launch Isaac Sim from the sourced terminal: `./isaac-sim.sh`.
4. Optional (Docker workflows / `./python.sh` standalone scripts with internal libs): set `ROS_DISTRO=jazzy`, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, and append `$isaac_sim_package_path/exts/isaacsim.ros2.core/jazzy/lib` to `LD_LIBRARY_PATH` (path changed from `isaacsim.ros2.bridge/<distro>/lib` in 5.1).
5. For multi-machine/Docker communication, enable the UDP FastDDS profile via `FASTRTPS_DEFAULT_PROFILES_FILE`. Cyclone DDS (Humble/Jazzy) and RMW Zenoh (Jazzy, `ros-jazzy-rmw-zenoh-cpp` + `rmw_zenohd` router) are also supported on Linux.

## Windows — Method 1: Pixi (recommended)

Prerequisites: Windows 11 x64, `winget install prefix-dev.pixi`, Git, MSVC Build Tools 2022 (Desktop C++), Isaac Sim 6.0 at `C:\isaacsim` (otherwise edit `isaac_sim_package_path` in `pixi.toml`). Keep the workspace path short (260-char limit):

```bat
git clone https://github.com/isaac-sim/IsaacSim-ros_workspaces.git C:\IsaacSim-ros_workspaces
cd C:\IsaacSim-ros_workspaces\jazzy_ws
pixi install
pixi run build
```

Run each in its own Command Prompt: `pixi run zenoh` (Zenoh router, start first), `pixi run sim` (Isaac Sim with ROS 2 bridge), `pixi run ros2 topic list`. `RMW_IMPLEMENTATION=rmw_zenoh_cpp` is preset. Run standalone scripts with `pixi run python <script.py>` (not `python.bat`).

## Windows — Method 2: WSL2 (deprecated)

1. `wsl --set-default-version 2` then `wsl --install -d Ubuntu-22.04` (Humble) or `-d Ubuntu-24.04` (Jazzy); reboot.
2. Install ROS 2 and the workspaces inside WSL2 following the Linux steps.
3. Port-forward the default FastDDS ports from admin PowerShell (get `$WSL2_IP` via `hostname -I` in WSL2, `$Windows_IP` via `ipconfig /all`):

    ```powershell
    netsh interface portproxy add v4tov4 listenport=7400 listenaddress=$Windows_IP connectport=7400 connectaddress=$WSL2_IP
    netsh interface portproxy add v4tov4 listenport=7410 listenaddress=$Windows_IP connectport=7410 connectaddress=$WSL2_IP
    netsh interface portproxy add v4tov4 listenport=9387 listenaddress=$Windows_IP connectport=9387 connectaddress=$WSL2_IP
    ```

4. Launch Isaac Sim on Windows (internal libraries load automatically; the ROS bridge is disabled by default on Windows):

    ```bat
    C:\isaacsim\isaac-sim.bat --/isaac/startup/ros_bridge_extension=isaacsim.ros2.bridge
    ```

    To pin a distro or run `python.bat` standalone scripts, set `ROS_DISTRO`, `RMW_IMPLEMENTATION`, and add `C:\isaacsim\exts\isaacsim.ros2.core\<distro>\lib` to `PATH`.

!!! tip "Site note"
    The WSL2 IP changes on every reboot; re-run the port proxy commands as needed. If DDS traffic still fails, Windows 11 22H2+ offers WSL2 mirrored networking (`networkingMode=mirrored` in `.wslconfig`) as an alternative. RViz2 and other GUI tools run inside WSL2 via WSLg.

**WSL2 limitations (official):** custom ROS interfaces, the Docker workflow, and Cyclone DDS are not supported on Windows/WSL2. (Pixi supports custom interfaces; it uses Zenoh, so FastDDS/Cyclone settings do not apply.)

## rclpy / custom packages inside Isaac Sim

Workspaces must be built with **Python 3.12**. On Ubuntu 24.04 + Jazzy the normal build already is — no extra steps. On Ubuntu 22.04, build with the provided Dockerfile: `./build_ros.sh -d humble -v 22.04` (or `-d jazzy`), then source `build_ws/<distro>/...` before launching Isaac Sim. On Windows, supported via Pixi (not via WSL2).

## Next Steps

- [Tutorial 1: URDF Import: Turtlebot](01_urdf_import_turtlebot.md)
