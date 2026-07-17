---
title: Depth Sensors
---

# Depth Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim models **stereoscopic depth cameras** from a single camera view via `isaacsim.sensors.experimental.rtx.SingleViewDepthCameraSensor`, which wraps `RtxCamera` and configures a post-processing pipeline for stereoscopic depth estimation. This pipeline is intended for stereo depth cameras only — not time-of-flight or structured-light sensors. (The former `isaacsim.sensors.camera.SingleViewDepthSensor` / `SingleViewDepthSensorAsset` classes are deprecated in Isaac Sim 6.0.)

## What you will learn

- **Single-view pipeline**: Run `standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_stereoscopic_depth.py`. Enable **Render Settings > Post Processing > Depth Sensor** and select **Disparity** in the **RGB Depth Output Mode** dropdown to view the disparity map. These settings apply to all render products; use `SingleViewDepthCameraSensor` for per-render-product control.
- **Annotators**: Run with `--test` (headless) to generate `depth_sensor_distance.png` (`DepthSensorDistance`) and `distance_to_image_plane.png` (`DistanceToImagePlane`).
- **Depth Camera Asset Wrapper**: Load official depth-sensor assets (e.g. RealSense D455 at `/Isaac/Sensors/RealSense/D455/rsd455.usd`) with `RtxCamera.create(path, usd_path=...)`, then wrap with `SingleViewDepthCameraSensor(cam, resolution=..., annotators=["depth_sensor_distance"])` and call `set_enabled_post_processing(True)`. Depth-sensor attributes are copied automatically from `RenderProduct` prims with `OmniSensorDepthSensorSingleViewAPI` embedded in the asset.
- **Building a model**: `create_camera_depth_sensor.py` builds a camera asset with an embedded template render product (sets `omni:rtx:post:depthSensor:baselineMM`) and exports `example_camera_with_depth_sensor.usd`; or build a new stereo depth sensor by importing to USD, adding cameras, calibrating intrinsics/extrinsics against real images, and tuning the depth-sensor schema.
