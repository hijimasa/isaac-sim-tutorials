---
title: RTX Lidar Sensor
---

# RTX Lidar Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

RTX Lidar sensors are simulated at render time on the GPU; results are copied to the `GenericModelOutput` AOV. They are rendered using **`OmniLidar` prims** with the `OmniSensorGenericLidarCoreAPI` schema. Camera-prim-based RTX Lidars are deprecated as of Isaac Sim 5.0.

## What you will learn

- **Create via command**: `IsaacSensorCreateRtxLidar` (low-level) references a Lidar USD/USDA asset or generic `OmniLidar` prim. Set `config` (e.g. `Example_Rotary`), `variant`, attributes like `omni:sensor:Core:scanRateBaseHz`, and `force_camera_prim` for deprecated workflows.
- **Create via `LidarRtx` class**: higher-level Python interface that wraps the `OmniLidar` prim, attaches a render product, and exposes annotator/writer APIs plus `get_data()`.
- **Collect data**: use Replicator Annotators (RTX Sensor Annotators + `GenericModelOutput`).
- **Asset library**: load real Lidar models by `config` / `config_file_name` (e.g. `HESAI_XT32_SD10`, `picoScan150` with `variant="Normal_11"`).
- **Sensor materials**: Lidar returns depend on material emissivity/reflectivity — see [RTX Sensor Non-Visual Materials](07_rtx_materials.md).
- **JSON → USD conversion**: `./python.sh tools/isaacsim.sensors.rtx/convert_lidar_json_to_usda.py` converts legacy JSON configs into `OmniLidar` USD files.

## Standalone examples

`isaacsim.ros2.bridge/rtx_lidar.py`, `isaacsim.sensors.rtx/inspect_lidar_metadata.py`, `resolve_object_ids_from_gmo.py`, `rotating_lidar_rtx.py`, and `isaacsim.util.debug_draw/rtx_lidar.py --config Example_Rotary|Example_Solid_State`.
