---
title: RTX Radar Sensor
---

# RTX Radar Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

RTX Radar sensors are simulated at render time on the GPU; results are copied to the `GenericModelOutput` AOV. They are rendered using **`OmniRadar` prims** with the `OmniSensorGenericRadarWpmDmatAPI` schema. Camera-prim-based RTX Radars are deprecated as of Isaac Sim 5.0.

!!! warning
    RTX Radar Doppler modeling requires **Motion BVH** to be enabled — see [RTX Sensors](03_rtx_sensors.md#motion-bvh).

## What you will learn

- **Create via command**: `IsaacSensorCreateRtxRadar` creates a generic `OmniRadar` prim (or a Camera prim with `force_camera_prim=True` for deprecated workflows). Set attributes like `omni:sensor:tickRate`. See the `OmniSensorGenericRadarWpmDmatAPI` schema for available attributes.
- **Collect data**: attach annotators to the `OmniRadar` prim to visualize returns — see [RTX Sensor Annotators](06_rtx_annotators.md).
- **Sensor materials**: Radar returns depend on material emissivity/reflectivity — see [RTX Sensor Non-Visual Materials](07_rtx_materials.md).

## Standalone example

`./python.sh standalone_examples/api/isaacsim.util.debug_draw/rtx_radar.py`
