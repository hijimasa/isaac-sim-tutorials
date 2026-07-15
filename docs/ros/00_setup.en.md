---
title: ROS 2 Setup
---

# ROS 2 Setup (Linux / Windows)

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

This page consolidates the setup required for the ROS 2 tutorial series, based on the official [ROS 2 Installation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_ros.html) guide.

!!! warning "Windows users: ROS 2 runs in WSL2 — this is the officially supported method"
    Isaac Sim 5.1 officially supports ROS 2 on Windows **only via WSL2 (Ubuntu 22.04 + ROS 2 Humble)**. Isaac Sim itself runs on the Windows side using its internal ROS 2 libraries; external ROS 2 nodes (teleop, Nav2, RViz2) run inside WSL2, communicating over DDS.

## Supported platforms

| Platform | ROS 2 |
|---|---|
| Ubuntu 24.04 | Jazzy (recommended) |
| Ubuntu 22.04 | Humble (recommended), Jazzy (source build) |
| Windows 10 / 11 | Humble — **inside WSL2** |

!!! note "Isaac Sim is Python 3.11 only"
    Isaac Sim ships internal ROS 2 libraries built with Python 3.11. Do **not** source your regular ROS 2 installation in the terminal that launches Isaac Sim; do source it in terminals running external nodes (DDS handles transport across Python versions).

## Linux

1. Install ROS 2 Humble (Ubuntu 22.04) or Jazzy (Ubuntu 24.04) per the official docs. Optional: `ros-<distro>-vision-msgs`, `ros-<distro>-ackermann-msgs`.
2. Launch Isaac Sim from a clean (non-sourced) terminal: `./isaac-sim.sh` — internal ROS 2 libraries load automatically.
3. Build the [IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) (`rosdep install` + `colcon build`) and source it in external-node terminals.
4. For multi-machine/Docker communication, enable the UDP FastDDS profile via `FASTRTPS_DEFAULT_PROFILES_FILE`.

## Windows (WSL2)

1. `wsl --set-default-version 2` then `wsl --install -d Ubuntu-22.04` (admin PowerShell); reboot.
2. Install ROS 2 Humble inside WSL2 following the Ubuntu 22.04 steps above (including workspaces).
3. Port-forward the default FastDDS ports from admin PowerShell (get `$WSL2_IP` via `hostname -I` in WSL2, `$Windows_IP` via `ipconfig /all`):

    ```powershell
    netsh interface portproxy add v4tov4 listenport=7400 listenaddress=$Windows_IP connectport=7400 connectaddress=$WSL2_IP
    netsh interface portproxy add v4tov4 listenport=7410 listenaddress=$Windows_IP connectport=7410 connectaddress=$WSL2_IP
    netsh interface portproxy add v4tov4 listenport=9387 listenaddress=$Windows_IP connectport=9387 connectaddress=$WSL2_IP
    ```

4. Launch Isaac Sim on Windows with the internal libraries:

    ```bat
    set ROS_DISTRO=humble
    set RMW_IMPLEMENTATION=rmw_fastrtps_cpp
    set PATH=%PATH%;C:\isaacsim\exts\isaacsim.ros2.bridge\humble\lib
    C:\isaacsim\isaac-sim.bat --/isaac/startup/ros_bridge_extension=isaacsim.ros2.bridge
    ```

!!! tip "Site note"
    The WSL2 IP changes on every reboot; re-run the port proxy commands as needed. If DDS traffic still fails, Windows 11 22H2+ offers WSL2 mirrored networking (`networkingMode=mirrored` in `.wslconfig`) as an alternative. RViz2 and other GUI tools run inside WSL2 via WSLg.

**Windows limitations (official):** custom packages inside Isaac Sim, the Docker workflow, and Cyclone DDS are not supported on Windows/WSL2.

## rclpy / custom packages inside Isaac Sim (Linux only)

Build a Python 3.11 workspace using the provided Dockerfile: `./build_ros.sh -d humble -v 22.04`, then source `build_ws/humble/...` before launching Isaac Sim.

## Next Steps

- [Tutorial 1: URDF Import: Turtlebot](01_urdf_import_turtlebot.md)
