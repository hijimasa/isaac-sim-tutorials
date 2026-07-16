---
title: Multiple Robot ROS2 Navigation
---

# Multiple Robot ROS2 Navigation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! warning
    Fully supported on Linux; may produce errors on Windows. Requires [Tutorial 18](18_navigation.md) completed.

## Overview

Multiple robots share one environment via **namespaces**: each `Nova_Carter_ROS_X`'s action graphs set `node_namespace` to the robot name, matching the `multiple_robot_carter_navigation_{hospital,office}.launch.py` launch files.

## Occupancy Maps

Generate maps for the Hospital and Office environments with the Occupancy Map extension (same procedure as Tutorial 18; Upper Z 0.62), saving as `carter_navigation/maps/carter_hospital_navigation.yaml` / `carter_office_navigation.yaml` plus matching images.

## Running

Open **Robotics Examples > ROS2 > Navigation > Multiple Robots > Hospital Scene** (or Office Scene), press Play, then:

```bash
ros2 launch carter_navigation multiple_robot_carter_navigation_hospital.launch.py   # or _office
```

Three RViz2 windows open (one per robot; check the Map topic to identify the namespace). Robots are pre-localized via `carter_navigation/params/{hospital,office}/`. Use **2D Nav Goal** in each window for `/carter1`–`/carter3`.

**Troubleshooting high CPU load:** enable **Publish Full Scan** on `publish_front_3d_lidar_scan` in each robot's `ros_lidars` graph; if issues persist try `./isaac-sim.fabric.sh --reset-user` (experimental). Image pipelines are disabled by default (Sensor Data QoS — use Best Effort in RViz).

## Sending Goals Programmatically for Multiple Robots

In `isaac_ros_navigation_goal.launch.py`, define one Node per robot with `namespace="carter1"` (etc.), correct initial poses, and add all nodes to the LaunchDescription. With GoalReader, each namespaced node needs its own goal file. Launch after the simulation and Nav2 stacks are running.

## Next Steps

- [Tutorial 20: ROS 2 Navigation with Block World Generator](20_navigation_block_world.md)
