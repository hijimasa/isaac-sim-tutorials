---
title: Camera Sensors
---

# Camera Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Cameras in Isaac Sim are modeled using the USD **Camera** prim type. Image data is acquired from camera prims through **render products**, which can be created by extensions such as `omni.replicator`. Isaac Sim camera functionality is based on Omniverse cameras.

!!! warning "Deprecated in 6.0"
    The `isaacsim.sensors.camera` extension (`Camera` / `CameraView` classes) is deprecated in Isaac Sim 6.0. Use `isaacsim.sensors.experimental.rtx` instead, which splits authoring (`RtxCamera`) from runtime (`CameraSensor`, `TiledCameraSensor`, `SingleViewDepthCameraSensor`, `StructuredLightCamera`). See the official [migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_camera_to_experimental_rtx.html).

## What you will learn

- **GUI**: Create a camera prim (`Create > Camera`), then switch the viewport to it via the video icon > Cameras menu.
- **Standalone Python**: Wrap an `RtxCamera` authoring object in a `CameraSensor`, request annotators (`rgb`, `distance_to_image_plane`, ...), and read `(data, info) = sensor.get_data("rgb")`. Run `./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_camera_basic.py`. `tick_rate` (Hz) controls render frequency (0 = every simulation frame); `TiledCameraSensor` batches many cameras into one tiled render product.
- **Lens distortion (OpenCV)**: Omniverse natively supports OpenCV **pinhole** and **fisheye** models. Apply them via `RtxCamera(schemas=["OmniLensDistortionOpenCvFisheyeAPI"], attributes={...})` (or the pinhole equivalent). See `camera_opencv_pinhole.py` and `camera_opencv_fisheye.py` under `standalone_examples/api/isaacsim.sensors.experimental.rtx/`.
- **Extrinsic calibration**: Convert a calibration toolkit's transformation matrix into Isaac Sim units, passing plural-array `positions=` / `orientations=` to `RtxCamera`.
- **Camera sensor rigs**: A collection of camera sensors attached to a single prim (e.g. the RealSense D455 digital twin at `/Isaac/Sensors/RealSense/D455/rsd455.usd`).
- **ISP pipeline**: `camera_isp_pipeline.py` saves per-stage ISP outputs (HDR read, color correction, CFA, noise, companding, ISP output, YUV) to `camera_isp_pipeline_outputs` (sample ISP program is Linux x86_64 only).
- **Camera Inspector Extension** (`Tools > Sensors > Camera Inspector`): create multiple viewports, check coverage, and copy camera poses into code.

!!! warning "Deprecated APIs and 6.0 known issues"
    The `fisheyePolynomial` approximation APIs and the RTX Camera Projection Attributes are deprecated in favor of native OpenCV models and the `OmniLensDistortion` schemas. In Isaac Sim 6.0, the `OmniLensDistortionLutAPI` schema does not function correctly (the renderer falls back to pinhole); use the deprecated projection attributes for arbitrary distortion models until it is fixed.
