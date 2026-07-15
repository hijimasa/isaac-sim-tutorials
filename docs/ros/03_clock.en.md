---
title: ROS 2 Clock
---

# ROS 2 Clock

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Understand time synchronization via the `/clock` topic and the `use_sim_time` parameter
- Publish simulation (or system) time as a Clock message
- Subscribe to a ROS 2 Clock message
- Generate the clock graph with the menu shortcut

## Simulation Time and Clock

Nodes with `use_sim_time` set to true subscribe to `/clock` and synchronize to published simulation time:

```bash
ros2 param set /node_name use_sim_time true
```

## Clock Publisher

Build an Action Graph with **On Playback Tick → ROS2 Context → Isaac Read Simulation Time → ROS2 Publish Clock**.

![Clock publisher](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_clock_publisher.png)

Simulation time increases monotonically across stop/play by default; set `resetOnStop` to True to restart from 0 on reset. Verify with RViz2: run `rviz2`, set `ros2 param set /rviz use_sim_time true` while stopped (ROS Time becomes 0), then press Play — ROS Time follows `/clock`.

To publish **system time** instead, replace the read node with **Isaac Read System Time**. For Camera/RTX Lidar Helper pipelines, set their `useSystemTime` input to True.

## Clock Subscriber

Build **On Playback Tick → ROS2 Context → ROS2 Subscribe Clock**, press Play, then:

```bash
ros2 topic pub -t 1 /clock rosgraph_msgs/Clock "clock: { sec: 1, nanosec: 200000000 }"
```

The node's `timeStamp` output changes to 1.2.

## Graph Shortcut

**Tools > Robotics > ROS 2 OmniGraphs > Clock** generates the publisher graph in a few clicks.

## Next Steps

- [Tutorial 4: ROS 2 Publish Real Time Factor (RTF)](04_rtf.md)
