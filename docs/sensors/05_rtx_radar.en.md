---
title: RTX Radar Sensor
---

# RTX Radar Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

RTX Radar sensors are simulated at render time on the GPU; results are copied to the `GenericModelOutput` AOV. They are rendered using **`OmniRadar` prims** with the `OmniSensorGenericRadarWpmDmatAPI` schema. In Isaac Sim 6.0 the deprecated `IsaacSensorCreateRtxRadar` command is replaced by the `isaacsim.sensors.experimental.rtx` `Radar` (authoring) + `RadarSensor` (runtime) classes.

!!! warning
    RTX Radar requires **Motion BVH** to be enabled (Doppler effect, and therefore RTX Radar entirely). Enable it via launch flags, `SimulationApp({"enable_motion_bvh": True})`, or `carb.settings` — see [RTX Sensors](03_rtx_sensors.md).

## What you will learn

- **Create via the `Radar` class**: `Radar(path="/World/radar", tick_rate=10, translations=..., orientations=...)` creates an `OmniRadar` prim. `Radar.create()` accepts `config` (from `SUPPORTED_RADAR_CONFIGS`) or `usd_path`; pass extra `schemas=[...]` through `Radar(...)` directly.
- **Key parameters**: `tick_rate` (Hz; known issue in 6.0 GA — Radar autotriggers regardless of `omni:sensor:tickRate`), `aux_output_level` (`NONE`/`BASIC`; `BASIC` enables radial velocity `rv_ms` in the GMO output).
- **Collect data**: `RadarSensor(radar, annotators=["generic-model-output"])`, then `data, info = sensor.get_data("generic-model-output")` and `parse_generic_model_output_data(data)` — see [RTX Sensor Annotators](06_rtx_annotators.md).
- **Sensor materials**: Radar returns depend on material emissivity/reflectivity — see [RTX Sensor Non-Visual Materials](07_rtx_materials.md).

## Standalone examples

`./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_radar_basic.py` (Debug Draw visualization) and `inspect_radar_gmo.py`. For ROS 2 PointCloud2 publishing, see the official RTX Radar ROS 2 tutorial.
