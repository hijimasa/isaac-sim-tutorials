---
title: ROS 2 Generic Publisher and Subscriber
---

# ROS 2 Generic Publisher and Subscriber

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Publish and subscribe to **any** ROS 2 message type with the generic ROS2 Publisher / ROS2 Subscriber nodes. List available types with `ros2 interface list --only-msgs`.

## Generic Publisher

Build On Playback Tick + ROS2 Context + **ROS2 Publisher**, then set the message type as `messagePackage` / `messageSubfolder` / `messageName` — the node's input attributes reconfigure automatically (no Play needed). Embedded messages (e.g. `std_msgs/Header`) unroll into attributes; arrays of embedded messages become token arrays with JSON-encoded tokens.

Examples:

- **Joint states** — Franka URDF example + Isaac Read Simulation Time + **Isaac Time Splitter** + **Articulation State** (targetPrim `/panda`) → ROS2 Publisher (sensor_msgs / JointState / joint_states). Verify with `ros2 topic echo /joint_states`.
- **Object pose** — a rigid-body Cube + two **Read Prim Attribute** nodes (`xformOp:translate`, `xformOp:orient`) + Break 3-Vector → ROS2 Publisher (geometry_msgs / Pose / object_pose).

![Joint states example](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_publisher_example_joint_states.png)

## Generic Subscriber

Same pattern with **ROS2 Subscriber** — output attributes reconfigure per message type. Example: subscribe to `/object_pose` (geometry_msgs/Pose) and drive two **Write Prim Attribute** nodes (+ Make 3-Vector) to teleport a cube:

```bash
ros2 topic pub -1 /object_pose geometry_msgs/msg/Pose "{position: {x: 1, y: 2, z: 3}, orientation: {x: 0.4619398, y: 0.1913417, z: 0.4619398, w: 0.7325378}}"
```

## Next Steps

- [Tutorial 23: ROS 2 Generic Server and Client](23_generic_server_client.md)
