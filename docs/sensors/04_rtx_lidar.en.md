---
title: RTX Lidar Sensor
---

# RTX Lidar Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

RTX Lidar sensors are simulated at render time on the GPU; results are copied to the `GenericModelOutput` AOV. They are rendered using **`OmniLidar` prims** with the `OmniSensorGenericLidarCoreAPI` schema. In Isaac Sim 6.0 the deprecated `isaacsim.sensors.rtx` APIs (`LidarRtx`, `IsaacSensorCreateRtxLidar`) are replaced by `isaacsim.sensors.experimental.rtx` (`Lidar` authoring + `LidarSensor` runtime); Camera-prim-based RTX Lidars have been removed.

## What you will learn

- **Create via the `Lidar` class**: `Lidar.create(path, config="Example_Rotary", translations=..., orientations=..., attributes={"omni:sensor:Core:scanRateBaseHz": 20})`. `config` and `usd_path` are mutually exclusive; transforms use plural arrays (N=1).
- **Key parameters**: `tick_rate` (Hz; 0 = autotrigger every frame; must equal `omni:sensor:Core:scanRateBaseHz` on OmniLidar prims), `aux_output_level` (`NONE`/`BASIC`/`EXTRA`/`FULL`), `accumulate_outputs` (accumulate frames into a full scan).
- **Collect data**: wrap with `LidarSensor(lidar, annotators=["generic-model-output"])`, then `data, info = sensor.get_data("generic-model-output")` and `parse_generic_model_output_data(data)`.
- **Visualize**: Debug Draw (`create_lidar_basic.py`), the viewport debug view **RTX - Real-Time > Debug View > Non-Visual Material ID**, or RViz2 via ROS 2.
- **ROS 2**: publish `PointCloud2` / `LaserScan` via **Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar**.
- **Asset library**: load real Lidar models by `config` / `variant` on `Lidar.create()` (e.g. `HESAI_XT32_SD10`; SICK `picoScan100` takes a dict variant `{"Product": ..., "Profile": ...}`). Enumerate via `SUPPORTED_LIDAR_CONFIGS`.
- **Sensor materials**: Lidar returns depend on material emissivity/reflectivity — see [RTX Sensor Non-Visual Materials](07_rtx_materials.md).

!!! warning
    On multi-GPU systems some RTX Lidar assets can crash with CUDA error 700; launch with `--/renderer/multiGpu/enabled=false` (or `multi_gpu=False` in `SimulationApp`).

## Standalone examples

Under `standalone_examples/api/isaacsim.sensors.experimental.rtx/`: `create_lidar_basic.py`, `create_lidar_with_config_and_variants.py`, `inspect_lidar_gmo.py --aux-data-level FULL`, `resolve_lidar_object_ids.py`, `lidar_robot_integration.py`; plus `isaacsim.ros2.bridge/rtx_lidar.py`.
