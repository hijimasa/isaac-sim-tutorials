---
title: Publishing Camera's Data
---

# Publishing Camera's Data

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and complete code.

## Learning Objectives

Programmatically set up ROS 2 publishers for Isaac Sim Cameras using the standalone Python workflow. Under multitick rendering (Isaac Sim 6.0), the publish cadence is driven by the camera's `tick_rate` set on the `RtxCamera` — no per-publisher rate divider (IsaacSimulationGate step) is needed anymore. See ROS2 Setting Publish Rates for per-sensor rates.

## Approach

A standalone script loads a warehouse environment and creates an `isaacsim.sensors.experimental.rtx` **`RtxCamera`** (`tick_rate=30.0`) wrapped by a **`CameraSensor`** (`resolution=(256, 256)`, annotators `rgb` / `distance_to_image_plane`), then calls helper functions (a shared `_get_sensor_info(sensor)` extracts render-product path, prim path, and frame id):

- `publish_camera_info(sensor)` — CameraInfo via the `ROS2PublishCameraInfo` writer and `read_camera_info()` from **`isaacsim.ros2.core`** (moved from `isaacsim.ros2.bridge`)
- `publish_rgb(sensor)` / `publish_depth(sensor)` — image writers on the Rgb / DistanceToImagePlane render variables
- `publish_pointcloud_from_depth(sensor)` — PointCloud2 reconstructed from depth using camera intrinsics (no semantic labels)
- `publish_camera_tf(sensor)` — publishes `/tf` with two frames: `{camera_frame_id}` (ROS camera convention, -Y up +Z forward; pointclouds are published here) and `{camera_frame_id}_world` (world convention, +Z up +X forward), linked by the static rotation quaternion `[0.5, -0.5, 0.5, 0.5]` (w, x, y, z). In 6.0 the graph creates three nodes per camera: an **Isaac Compute Transform Tree** node (`isaacsim.core.nodes.IsaacComputeTransformTree`, receives `targetPrims`), the **ROS2 Publish Transform Tree** node fed by its outputs, and a **ROS2 Publish Raw Transform Tree** node for the static rotation.

Environment/stage utilities come from `isaacsim.core.experimental.utils.{app,stage,transform}` and `isaacsim.storage.native.get_assets_root_path`.

## Verifying

```bash
ros2 topic list
# /clock /floating_camera_camera_info /floating_camera_depth /floating_camera_pointcloud /floating_camera_rgb /tf ...
```

In RViz2 set **Fixed Frame** to `world` and enable the `/floating_camera_*` topics and `/tf`.

![RGB and depth](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros_camera_publishing_rgbd.png)

## Next Steps

- [Tutorial 8: RTX Lidar Sensors](08_rtx_lidar.md)
