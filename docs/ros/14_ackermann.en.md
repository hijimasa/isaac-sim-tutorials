---
title: ROS 2 Ackermann Controller
---

# ROS 2 Ackermann Controller

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Drive the Leatherback car with AckermannDriveStamped messages, and control it with Twist messages via a converter. Requires `ros-$ROS_DISTRO-ackermann-msgs` plus the `isaac_tutorials` and `cmdvel_to_ackermann` packages from IsaacSim-ros_workspaces.

## Setup

On a Flat Grid environment with **Isaac Sim > ROBOTS > NVIDIA > Leatherback** at the origin, build a graph: On Playback Tick, ROS2 Context, **ROS2 Subscribe AckermannDrive** (topic `ackermann_cmd`) with a **ROS2 QoS Profile**, an **Ackermann Controller**, and two Articulation Controllers — one for steering joints (`Knuckle__Upright__Front_Left/Right`), one for wheels (`Wheel__Upright__Rear_Left/Right`, `Wheel__Knuckle__Front_Left/Right`), both targeting `/Leatherback`.

![Ackermann graph](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_ackermann_omnigraph.png)

Ackermann Controller parameters: backWheelRadius / frontWheelRadius 0.052, maxWheelRotation 0.7854, maxWheelVelocity 20.0, trackWidth 0.24, wheelBase 0.32, maxAcceleration 1.0, maxSteeringAngleVelocity 1.0.

Press Play, then:

```bash
ros2 run isaac_tutorials ros2_ackermann_publisher.py
```

Preconfigured assets: **Samples > ROS2 > Robots > Leatherback_ROS** and **Scenario > leatherback_ackermann**.

## Twist to AckermannDriveStamped

Open the `leatherback_ackermann` racetrack scene, press Play, and run:

```bash
ros2 launch cmdvel_to_ackermann cmdvel_to_ackermann.launch.py acceleration:=0.5 steering_velocity:=0.5
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Launch parameters: publish_period_ms (20), track_width (0.2), acceleration (0 = as fast as possible), steering_velocity (0 = as fast as possible). Keys: i/, forward/backward, u/o/m/. diagonal, k stop.

## Next Steps

- [Tutorial 15: Automatic ROS 2 Namespace Generation](15_auto_namespace.md)
