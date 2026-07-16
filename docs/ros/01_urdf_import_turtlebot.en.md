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
- `sudo apt install ros-$ROS_DISTRO-xacro`

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

3. On a new stage, drag **Isaac Sim/Environments/Simple_Room/simple_room.usd** onto the stage and zero out its Translate.
4. **File > Import** the processed URDF. Select **Referenced Model**, set **Moveable Base**, and set `wheel_left_joint` / `wheel_right_joint` drive targets to **Velocity**.
5. Click **Import**, place the robot just above the floor, press **Play**, and verify it falls onto the floor.

![Turtlebot import](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_ros_tut_gui_tb_urdf_import.png)

## Tune the Robot

- **Friction** — adjust wheel/ground friction coefficients if wheels slip.
- **Mass/inertia** — add or edit the **Physics > Mass** category on rigid-body prims when URDF values are missing.
- **Joints** — for velocity drives set stiffness 0 with non-zero damping; for this Turtlebot try **Damping 10000000.0 / Stiffness 0.0**.

!!! note
    The imported robot is loaded as a *reference*. If parameter changes don't stick, edit the original USD found via **References > Asset Path**.

## Next Steps

- [Tutorial 2: Driving TurtleBot using ROS 2 Messages](02_drive_turtlebot.md)
