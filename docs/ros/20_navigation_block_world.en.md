---
title: ROS 2 Navigation with Block World Generator
---

# ROS 2 Navigation with Block World Generator

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! warning "Status in Isaac Sim 6.0"
    This tutorial was removed from the official Isaac Sim 6.0 documentation. This page is this site's own walkthrough based on the 5.1.0 content. As an alternative, the official 6.0 docs added a new tutorial: [ROS 2 Navigation with Heightmap](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_navigation_heightmap.html).

## Learning Objectives

Generate a 3D world from a 2D occupancy map and navigate it with Nav2 — the reverse direction of Tutorial 18, useful for quickly turning a real-world SLAM map into a simulation environment.

## Steps

1. **Tools > Robotics > Block World Generator** → **Load Image** (`carter_navigation/maps/carter_warehouse_navigation.png`) → **Generate**. Occupied pixels get collision meshes automatically.
2. Drag `Nova_Carter_ROS.usd` (from **Isaac Sim > Samples > ROS2 > Robots**) anywhere on the ground inside the walls.
3. Add a ROS_Clock graph via **Tools > Robotics > ROS 2 OmniGraphs > Clock**.
4. Press Play, then:

    ```bash
    ros2 launch carter_navigation carter_navigation.launch.py
    ```

5. Use **2D Pose Estimate** first (the robot was placed manually, so its pose is not pre-localized), then send a **Navigation2 Goal**.

## Next Steps

- [Tutorial 21: MoveIt 2](21_moveit.md)
