---
title: Depth Sensors
---

# Depth Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim models **stereoscopic depth cameras** from a single camera view via `isaacsim.sensors.camera.SingleViewDepthSensor`, which wraps `Camera` and configures a post-processing pipeline for stereoscopic depth estimation. This pipeline is intended for stereo depth cameras only — not time-of-flight or structured-light sensors.

## What you will learn

- **Single-view pipeline**: Run `standalone_examples/api/isaacsim.sensors.camera/camera_stereoscopic_depth.py`. Enable **Render Settings > Post Processing > Depth Sensor** and select **Disparity** in the **RGB Depth Output Mode** dropdown to view the disparity map. These settings apply to all render products; use `SingleViewDepthSensor` for per-render-product control.
- **Annotators**: Run with `--test` (headless) to generate `depth_sensor_distance.png` (`DepthSensorDistance`) and `distance_to_image_plane.png` (`DistanceToImagePlane`).
- **Depth Camera Asset Wrapper**: `SingleViewDepthSensorAsset` loads official depth-sensor assets (e.g. RealSense D455 at `/Isaac/Sensors/Intel/RealSense/rsd455.usd`), wrapping their `Camera` prims as `SingleViewDepthSensor` instances. Use `initialize()`, `get_all_depth_sensor_paths()`, `get_child_depth_sensor()`, and `attach_annotator()`.
- **Building a model**: Update an existing asset via `camera_add_depth_sensor.py` (sets `omni:rtx:post:depthSensor:baselineMM`), or build a new stereo depth sensor by importing to USD, adding cameras, calibrating intrinsics/extrinsics against real images, and tuning the depth-sensor schema.

!!! warning
    AOV texture-size errors on the first depth frame are expected and will be corrected in a future release.
