---
title: RTX Lidar Sensors
---

# RTX Lidar Sensors

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Create RTX Lidar sensors, publish LaserScan / PointCloud2 to ROS 2, and visualize multiple sensors in RViz2.

RTX Lidar simulates lidar beams with RTX ray tracing, supporting rotating and solid-state configurations via JSON config files. Do not re-dock UI windows while an RTX Lidar simulation is running (pause first). Bandwidth-heavy topics may not be viewable in RViz2 under WSL.

## Adding an RTX Lidar ROS 2 Bridge

1. **Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D** (2D) and **Example Rotary** (3D); drag both under `/World/turtlebot3_burger/base_scan` and zero their transforms.
2. Build an Action Graph: On Playback Tick, ROS2 Context, Isaac Run One Simulation Frame, two **Isaac Create Render Product** nodes (one per lidar), and two **ROS2 RTX Lidar Helper** nodes — one for laser_scan (frameId `base_scan`), one with type `point_cloud`, topic `point_cloud`.

![RTX Lidar graph](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_ros_tut_gui_rtx_lidar_graph.png)

With type laser_scan, the message publishes only on full scans — e.g. a 10 Hz rotary lidar at 1/60 s steps publishes every 6 frames; solid-state lidars publish every frame. PointCloud publishing depends on the **Publish Full Scan** setting.

In RViz2 set Fixed Frame to `base_scan`, add LaserScan (`/scan`) and PointCloud2 (`/point_cloud`). A menu shortcut exists at **Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar**.

## Standalone Script

```bash
rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/rtx_lidar.rviz
./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
```

Key calls: `IsaacSensorCreateRtxLidar` (config `Example_Rotary`, `Example_Rotary_2D`, or `Example_Solid_State`), `rep.create.render_product(...)`, and writers `RtxLidarROS2PublishPointCloud` / `RtxLidarROS2PublishLaserScan`.

## Multiple Sensors in RViz2

Feed all publishers' timestamps from **Isaac Read Simulation Time**, publish `/clock`, and follow the frameId/topicName conventions (camera: `(device)_(type)` frame, `image_raw`/`image_rect_raw` topics; lidar: `base_scan` frame, `scan`/`point_cloud` topics). Sample: `turtlebot_tutorial.usd`. Open the provided config with `rviz2 -d .../camera_lidar.rviz` and set `ros2 param set /rviz use_sim_time true`.

## Next Steps

- [Tutorial 9: ROS2 Transform Trees and Odometry](09_tf.md)
