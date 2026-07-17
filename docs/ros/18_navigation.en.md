---
title: ROS 2 Navigation (Nav2)
---

# ROS 2 Navigation (Nav2)

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! warning
    Fully supported on Linux and on Windows with the Pixi-based installation; partially supported on Windows (WSL). On multi-GPU Windows systems this scene may currently crash the application (known issue). Requires Nav2 plus the `carter_navigation`, `iw_hub_navigation`, and `isaac_ros_navigation_goal` packages from the Isaac Sim ROS workspaces. Source ROS 2 before launching Isaac Sim.

## Topics Published to Nav2

`/tf`, `/odom`, `/map`, `/point_cloud`, and `/scan` (via an external pointcloud_to_laserscan node).

## Occupancy Map

Open **Robotics Examples > ROS2 > Navigation > Nova Carter**, switch the camera to Top, open **Tools > Robotics > Occupancy Map** (Origin 0/0/0, Lower Z 0.1, Upper Z 0.62 — the Nova Carter lidar height), select `warehouse_with_forklifts`, **BOUND SELECTION**, delete the robot prim, then **CALCULATE → VISUALIZE IMAGE** with Rotate 180° and ROS YAML coordinate type. Click **Save YAML** to save `carter_navigation/maps/carter_warehouse_navigation.yaml`, and save the image as `carter_warehouse_navigation.png`.

## Running Nav2

Play the Nova Carter example, then:

```bash
ros2 launch carter_navigation carter_navigation.launch.py
```

The robot is pre-localized via `carter_navigation_params.yaml` (use 2D Pose Estimate if needed); send goals with **Navigation2 Goal**. Notes: hawk image pipelines are disabled by default (enable `_camera_render_product`; images use Sensor Data QoS — set RViz Reliability to Best Effort); sparse scenes can hurt localization; the "invalid dt" differential-controller warning is harmless.

Variants: robot description display (`nova_carter_description` package + `nova_carter_description_isaac_sim.launch.py`), a robot_state_publisher-based asset (**Nova Carter Joint States** — Isaac Sim publishes joint states and one ground-truth odom→base_link raw TF; camera static TFs come from Isaac Sim acting as the device driver), and **iw.hub** (`iw_hub_navigation.launch.py`).

## Sending Goals Programmatically

`isaac_ros_navigation_goal` sends random (`RandomGoalGenerator`) or scripted (`GoalReader`) goals; key parameters: map_yaml_path, iteration_count, action_server_name, obstacle_search_distance_in_meters, goal_text_file_path, initial_pose. Launch with `ros2 launch isaac_ros_navigation_goal isaac_ros_navigation_goal.launch.py`.

## Sending Goals Using ActionGraph

**Robotics Examples > ROS2 > Navigation > Add Waypoint Follower** creates a waypoint or patrolling (2–50 waypoints) graph; move `/World/Waypoints/waypoint_n`, then trigger **Send Impulse** on the OnImpulseEvent node. Requires a sourced ROS 2 installation (not the internal libraries); uses AMCL.

## Next Steps

- [Tutorial 19: Multiple Robot ROS2 Navigation](19_multi_navigation.md)
