---
title: PhysX SDK Lidar
---

# PhysX SDK Lidar

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The PhysX SDK Lidar uses PhysX raycasts to simulate a Lidar (horizontal/vertical resolution, rotation rate, etc.). It **cannot interact with non-visual materials** and always reports ground truth — for physically based reflection/transmission use the [RTX Lidar Sensor](04_rtx_lidar.md).

## Usage

- **GUI**: Create a Physics Scene, then `Create > Sensors > PhysX Lidar > Rotating`. In Raw USD Properties, enable `drawLines` and set `rotationRate` (`0.0` fires in all directions at once). Detected objects need Colliders. Parent the Lidar under geometry/robots (e.g. Carter V1) by drag-and-drop so readings become relative to the parent.
- **Python API**: `from isaacsim.sensors.physx import _range_sensor`, `acquire_lidar_sensor_interface()`, `RangeSensorCreateLidar` command. Play one frame, `timeline.pause()`, then read `get_linear_depth_data`, `get_zenith_data`, `get_azimuth_data` (use `asyncio`).
- **Semantic segmentation**: create the Lidar with `enable_semantics=True`, apply `Semantics.SemanticsAPI` to prims, and read `get_point_cloud_data` + `get_prim_data`.
