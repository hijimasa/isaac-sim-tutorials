---
title: RTX Lidar Sensors
---

# RTX Lidar Sensors

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Create RTX Lidar sensors, publish LaserScan / PointCloud2 to ROS 2, and optionally expose RTX Lidar metadata (intensity, Object IDs, timestamps) in the PointCloud2 message.

RTX Lidar simulates lidar beams with RTX ray tracing, supporting rotating and solid-state configurations. In Isaac Sim 6.0, publish rates are governed by `omni:sensor:tickRate` on the OmniLidar prim (must equal `omni:sensor:Core:scanRateBaseHz`), not by `frameSkipCount`. Do not re-dock UI windows while an RTX Lidar simulation is running (pause first). Bandwidth-heavy topics may not be viewable in RViz2 under WSL.

## Adding an RTX Lidar ROS 2 Bridge

1. **Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D** (2D) and **Example Rotary** (3D); drag both under `/World/tb3_burger_processed/Geometry/base_footprint/base_link/base_scan` and zero their transforms.
2. Select the `base_scan` prim in the Stage panel and create an Action Graph named `ROS_LidarRTX` with: On Playback Tick, ROS2 Context, Isaac Run One Simulation Frame, two **Isaac Create Render Product** nodes (one per lidar), and two **ROS2 RTX Lidar Helper** nodes — one for laser_scan (topic `scan`, frameId `base_scan`), one with type `point_cloud`, topic `point_cloud`, frameId `base_scan`, and **Publish Full Scan** checked.

![RTX Lidar graph](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_ros_tut_gui_rtx_lidar_graph.png)

With type laser_scan, the message publishes only on full scans — e.g. a 10 Hz rotary lidar at 1/60 s steps publishes every six frames; solid-state lidars publish every frame. PointCloud publishing depends on the **Publish Full Scan** setting.

In RViz2 set Fixed Frame to `base_scan`, add LaserScan (`/scan`) and PointCloud2 (`/point_cloud`). A menu shortcut exists at **Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar**.

## Standalone Script

```bash
rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/rtx_lidar.rviz
./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
```

The sample uses the `isaacsim.sensors.experimental.rtx` Python API (replacing the `IsaacSensorCreateRtxLidar` command / JSON configs):

```python
from isaacsim.sensors.experimental.rtx import Lidar
lidar = Lidar.create(path="/sensor", config="Example_Rotary", tick_rate=10.0, translations=[[0.0, 0.0, 1.0]])
```

`Example_Rotary` / `Example_Rotary_2D` / `Example_Solid_State` select configuration USDs; keep `tick_rate` equal to the asset's `scanRateBaseHz`. Attach with `rep.create.render_product(lidar.paths[0], [1, 1], name="Isaac")` and writers `RtxLidarROS2PublishPointCloud` / `RtxLidarROS2PublishLaserScan`.

## (Optional) Exposing RTX Lidar Metadata

Create the lidar with `aux_output_level="BASIC"` (or `"FULL"`), launch Isaac Sim with `--/rtx-transient/stableIds/enabled=true`, then either add a **ROS2 RTX Lidar Point Cloud Config** node (Include Intensity / ObjectId, wire `selectedMetadata` into the helper, tick `enableObjectIdMap` for the `/object_id_map` topic) or, in Python, initialize `RtxLidarROS2PublishPointCloud` with `outputIntensity=True, outputObjectId=True` plus a `ROS2PublishObjectIdMap` writer. Timestamps arrive as two uint32 fields (`timestamp_0` low / `timestamp_1` high bits of a uint64 nanosecond value — changed from a single float32 in 5.x); Object IDs as four uint32 fields forming a 128-bit ID resolvable via `/object_id_map` (`ros2 run isaac_tutorials ros2_object_id_subscriber.py`).

Note: the "Multiple Sensors in RViz2" section moved to [Tutorial 9: ROS2 Transform Trees and Odometry](09_tf.md).

## Next Steps

- [Tutorial 9: ROS2 Transform Trees and Odometry](09_tf.md)
