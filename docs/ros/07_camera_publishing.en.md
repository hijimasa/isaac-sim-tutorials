---
title: Publishing Camera's Data
---

# Publishing Camera's Data

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and complete code.

## Learning Objectives

Programmatically set up ROS 2 publishers for Isaac Sim Cameras at an approximate frequency, using the standalone Python workflow.

## Approach

A standalone script loads a warehouse environment and creates an `isaacsim.sensors.camera.Camera`, then calls helper functions:

- `publish_camera_info(camera, freq)` — CameraInfo via the `ROS2PublishCameraInfo` writer and `read_camera_info()`
- `publish_rgb(camera, freq)` / `publish_depth(camera, freq)` — image writers on the Rgb / DistanceToImagePlane render variables
- `publish_pointcloud_from_depth(camera, freq)` — PointCloud2 reconstructed from depth using camera intrinsics (no semantic labels)
- `publish_camera_tf(camera)` — publishes `/tf` with two frames: `{camera_frame_id}` (ROS camera convention, -Y up +Z forward; pointclouds are published here) and `{camera_frame_id}_world` (world convention, +Z up +X forward), linked by the static rotation quaternion `[0.5, -0.5, 0.5, 0.5]` (w, x, y, z)

Publish rate is controlled by setting the `step` input of the upstream **IsaacSimulationGate** node (`step_size = int(60/freq)`, assuming ~60 FPS rendering — hence "approximate").

## Verifying

```bash
ros2 topic list
# /camera_camera_info /camera_depth /camera_pointcloud /camera_rgb /clock /tf ...
```

In RViz2 set **Fixed Frame** to `world` and enable the camera topics and `/tf`.

![RGB and depth](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros_camera_publishing_rgbd.png)

## Next Steps

- [Tutorial 8: RTX Lidar Sensors](08_rtx_lidar.md)
