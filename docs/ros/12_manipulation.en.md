---
title: "ROS2 Joint Control: Extension Python Scripting"
---

# ROS2 Joint Control: Extension Python Scripting

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Add a ROS 2 Joint State publisher/subscriber for the Franka Panda — via UI, menu shortcut, and the OmniGraph Python API — and mix position/velocity control modes.

!!! note "Isaac Sim 6.0"
    Direct prim inputs (targetPrim) on ROS2 Publish Joint State are deprecated in Isaac Sim 6.0; the recommended setup feeds it from an **Isaac Read Joint State** node (`isaacsim.sensors.physics.nodes`). The official tutorial still uses targetPrim as of 6.0.1, so this page follows it. See the [ROS 2 OmniGraph Nodes migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/ros2_omnigraph_migration.html).

## Add Joint States in UI

Open **Isaac Sim > Robots > FrankaRobotics > FrankaPanda > franka.usd** and build an Action Graph with On Playback Tick, Isaac Read Simulation Time, **ROS2 Publish Joint State** (targetPrim `/panda`, topic `/joint_states`), **ROS2 Subscribe Joint State** (`/joint_command`), and **Articulation Controller** (targetPrim or robotPath `/panda`); wire the subscriber's jointNames/position/velocity/effort outputs into the controller.

![Joint state graph](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_ros_tut_gui_ros2_manipulation_1.png)

Test with:

```bash
ros2 run isaac_tutorials ros2_publisher.py
ros2 topic echo /joint_states
```

Shortcut: **Tools > Robotics > ROS 2 OmniGraphs > JointStates** (optionally adds the Articulation Controller).

## Scripted Setup

The same graph can be created once per stage from the Script Editor with `og.Controller.edit(...)` creating OnPlaybackTick / PublishJointState / SubscribeJointState / ArticulationController / ReadSimTime, connecting them, and setting `robotPath` and `targetPrim` to `/panda`. See the Japanese page for the full snippet.

## Position and Velocity Control Modes

Each joint uses one mode at a time, but different joints may use different modes (position: stiffness >> damping; velocity: stiffness = 0). Publish separate JointState messages per mode, or one message using `float('nan')` for entries not controlled by that mode.

## Next Steps

- [Tutorial 13: NameOverride Attribute](13_name_override.md)
