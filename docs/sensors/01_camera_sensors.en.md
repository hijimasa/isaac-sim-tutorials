---
title: Camera Sensors
---

# Camera Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Cameras in Isaac Sim are modeled using the USD **Camera** prim type. Image data is acquired from camera prims through **render products**, which can be created by extensions such as `omni.replicator`. Isaac Sim camera functionality is based on Omniverse cameras.

## What you will learn

- **GUI**: Create a camera prim (`Create > Camera`), then switch the viewport to it via the video icon > Cameras menu.
- **Standalone Python**: Use the `Camera` class from `isaacsim.sensors.camera` to retrieve image data. Run `./python.sh standalone_examples/api/isaacsim.sensors.camera/camera.py`. Key APIs: `get_rgba()`, `get_current_frame()`, `get_image_coords_from_world_points()`, `get_world_points_from_image_coords()`.
- **Lens distortion (OpenCV)**: Omniverse natively supports OpenCV **pinhole** and **fisheye** models. Set intrinsics/distortion via `set_opencv_pinhole_properties()` / `set_opencv_fisheye_properties()`. See `camera_opencv_pinhole.py` and `camera_opencv_fisheye.py`.
- **Extrinsic calibration**: Convert a calibration toolkit's transformation matrix into Isaac Sim units (axis/rotation-order conventions vary per toolkit).
- **Camera sensor rigs**: A collection of camera sensors attached to a single prim (e.g. the RealSense D455 digital twin at `/Isaac/Sensors/Intel/RealSense/rsd455.usd`).
- **Pre-ISP pipeline**: `camera_pre_isp_pipeline.py --draw-output` renders and saves HDR, raw sensor, and ISP outputs.
- **Camera Inspector Extension** (`Tools > Sensors > Camera Inspector`): create multiple viewports, check coverage, and copy camera poses into code.

!!! warning "Deprecated APIs"
    The `fisheyePolynomial` approximation APIs and the RTX Camera Projection Attributes are deprecated in favor of native OpenCV models and the `OmniLensDistortion` schema.
