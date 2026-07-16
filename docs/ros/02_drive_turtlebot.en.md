---
title: Driving TurtleBot using ROS 2 Messages
---

# Driving TurtleBot using ROS 2 Messages

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Add controllers (Differential Controller / Articulation Controller) to Turtlebot3
- Learn ROS 2 bridge OmniGraph nodes
- Drive the robot with a ROS 2 Twist message on `/cmd_vel`

## Prerequisites

- A rigged Turtlebot, or completed [URDF Import: Turtlebot](01_urdf_import_turtlebot.md)
- Completed ROS 2 Installation (environment sourced before launching Isaac Sim, ROS 2 extension enabled)

## Building the Graph

Open **Window > Graph Editors > Action Graph**, create a new graph, and build:

![Turtlebot graph](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_turtlebot_graph.png)

Key nodes:

- **On Playback Tick** — ticks the graph every simulation step; it (not the subscriber's Exec Out) must tick the Differential Controller and Articulation Controller.
- **ROS2 Context** — sets the DDS Domain ID (default 0; can read `ROS_DOMAIN_ID`).
- **ROS2 Subscribe Twist** — set topicName to `/cmd_vel`.
- **Break 3-Vector** — extracts forward velocity and z angular velocity from the Twist vectors.
- **Differential Controller** — Max Angular Speed 1.0, Max Linear Speed 0.22, Wheel Distance 0.16, Wheel Radius 0.025.
- **Articulation Controller** — Add Target = the prim holding the Articulation Root API (move it to `/World/turtlebot3_burger` if it is on `base_footprint`).
- **Constant Token + Make Array** — joint names `wheel_left_joint`, `wheel_right_joint` (token type, not string).

## Verifying ROS Connections

Press **Play**, then in a ROS-sourced terminal:

```bash
ros2 topic list                      # /cmd_vel should be listed
ros2 topic pub /cmd_vel geometry_msgs/Twist "{'linear': {'x': 0.2, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}"
```

For keyboard teleop:

```bash
sudo apt-get install ros-$ROS_DISTRO-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

!!! tip
    Keep the robot on the floor — the table has different physics properties.
