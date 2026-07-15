---
title: MoveIt 2
---

# MoveIt 2

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Run a manipulation scene in Isaac Sim with MoveIt 2. Requires the `isaac_moveit` package from the Isaac Sim ROS workspaces and completion of [Tutorial 12: ROS2 Joint Control](12_manipulation.md) — MoveIt 2 connects through the same `/joint_states` + `/joint_command` interface.

## Running MoveIt 2

1. Open **Robotics Examples > ROS2 > MoveIt > Franka MoveIt** and press Play.
2. Launch:

    ```bash
    ros2 launch isaac_moveit isaac_moveit.launch.py
    ```

3. In RViz: Planning Group `hand`, Goal State `open`, **Plan** then **Execute**. (On some machines, `close` may fail/abort or execute late.)
4. For the arm: Planning Group `panda_arm`, drag the interactive markers (or Goal State `<random_valid>`), **Plan** → **Execute**.

## Troubleshooting

Black robot area in RViz → update the mesa driver (`sudo add-apt-repository ppa:kisak/kisak-mesa` etc.).

## Next Steps

- [Tutorial 22: ROS 2 Generic Publisher and Subscriber](22_generic_pub_sub.md)
- [MoveIt 2 documentation](https://moveit.picknik.ai/humble/index.html)
