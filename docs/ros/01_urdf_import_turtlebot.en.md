---
title: "URDF Import: Turtlebot"
---

# URDF Import: Turtlebot

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Set up a [Turtlebot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview) in Isaac Sim and prepare it to drive around: preprocess the URDF with xacro, import it, and tune the robot.

## Prerequisites

- Completed ROS 2 Installation (ROS 2 available, ROS 2 extension enabled, environment variables set)
- Basic understanding of ROS workspaces
- xacro: `sudo apt install ros-$ROS_DISTRO-xacro` (Linux) / `pixi add ros-$ROS_DISTRO-xacro` (Windows Pixi)

## Importing TurtleBot URDF

1. Clone the description package:

    ```bash
    git clone -b $ROS_DISTRO https://github.com/ROBOTIS-GIT/turtlebot3.git turtlebot3
    cd turtlebot3/turtlebot3_description/urdf
    ```

2. Preprocess the URDF to remove namespace arguments:

    ```bash
    namespace=""
    xacro ./turtlebot3_burger.urdf "namespace:=${namespace:+$namespace/}" > tb3_burger_processed.urdf
    ```

    On Windows (Pixi): `xacro .\turtlebot3_burger.urdf "namespace:=" > tb3_burger_processed.urdf` in Command Prompt; in PowerShell pipe through `Out-File -Encoding utf8` (plain `>` writes UTF-16 LE, which the importer cannot parse).

3. **File > Import** the processed URDF. Set **Base Type** to **Mobile**, optionally set **Robot Type** to **Wheeled**, then click **Import** — the importer automatically opens the generated USD (robot prim: `/World/tb3_burger_processed`).

![Turtlebot import](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_tb_urdf_import.png)

## Tune the Robot

- **Friction** — adjust wheel/ground friction coefficients if wheels slip.
- **Mass/inertia** — add or edit the **Physics > Mass** category on rigid-body prims when URDF values are missing.
- **Joint gains** — open **Tools > Robotics > Asset Editors > Gain Tuner**, select the robot, set **Damping 10000000.0** for `wheel_left_joint` / `wheel_right_joint`, and click **Save Gains to Physics Layer**. (Velocity drives need stiffness 0 with non-zero damping.)

## Assemble the Scene

On a new stage, drag **Isaac Sim/Environments/Simple_Room/simple_room.usd** onto the stage and zero out its Translate, then drag the Turtlebot USD asset onto the stage. Place it just above the floor (the official screenshot uses `(0, 1.5, -0.75)`), press **Play**, and verify it falls onto the floor.

!!! warning
    On multi-GPU Windows systems, loading and playing this scene may currently crash the application (known issue).

## Next Steps

- [Tutorial 2: Driving TurtleBot using ROS 2 Messages](02_drive_turtlebot.md)
