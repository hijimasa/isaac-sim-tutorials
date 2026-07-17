---
title: RTX Sensors
---

# RTX Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

RTX sensors use the Omniverse RTX Renderer's **RTX Sensor SDK** to sense the environment across visual and non-visual spectra. An RTX Lidar can model returns from transparent or reflective surfaces; an RTX Radar can model returns accounting for material emissivity and reflectivity in the radio spectrum. Utilities live in the `isaacsim.sensors.experimental.rtx` extension:

- [RTX Lidar Sensor](04_rtx_lidar.md)
- [RTX Radar Sensor](05_rtx_radar.md)
- [RTX Sensor Annotators](06_rtx_annotators.md)
- [RTX Sensor Non-Visual Materials](07_rtx_materials.md)

!!! warning "Deprecated in 6.0"
    The `isaacsim.sensors.rtx` extension is deprecated in Isaac Sim 6.0. Use `isaacsim.sensors.experimental.rtx` instead (authoring `Lidar`/`Radar`/`Acoustic` + runtime `LidarSensor`/`RadarSensor`/`AcousticSensor`); OmniGraph nodes, annotators, and debug drawing ship in the still-active `isaacsim.sensors.rtx.nodes`. See the [migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_rtx_to_experimental_rtx.html). Isaac Sim 6.0 also adds RTX Acoustic sensors, Multi-Tick Rendering, and custom RTX sensor profiles (see the official docs).

## Important settings

Key flags (defaults): `--/app/sensors/nv/lidar/outputBufferOnGPU=false` and `--/app/sensors/nv/radar/outputBufferOnGPU=false` (must stay `false` for annotators to work), `--/app/sensors/nv/lidar/publishNormals=false`, `--/rtx/materialDb/nonVisualMaterialCSV/enabled=false`, `--/rtx/rtxsensor/useHydraTimeAlways=true`, `--/rtx-transient/stableIds/enabled=false`, `--/renderer/raytracingMotion/enabled=false`.

## Motion BVH

RTX sensors use **Motion BVH** to accurately model motion-related effects (object motion during exposure, sensor motion during capture). It is **disabled by default** for performance. RTX Lidar motion compensation and RTX Radar Doppler modeling both require it.

Enable via `SimulationApp({"enable_motion_bvh": True})`, or on the command line:

```bash
--/renderer/raytracingMotion/enabled=true \
--/renderer/raytracingMotion/enableHydraEngineMasking=true \
--/renderer/raytracingMotion/enabledForHydraEngines='0,1,2,3,4'
```

!!! warning
    Enabling Motion BVH increases VRAM usage and rendering time significantly. Leave it disabled when not needed.

## Auxiliary output level (GMO channels)

RTX Lidar/Radar/Acoustic sensors emit a GenericModelOutput (GMO) AOV. The amount of auxiliary data is controlled by the `_replicator:rendervar:GenericModelOutput:channels` attribute on the sensor prim, conveniently authored via the `aux_output_level` constructor parameter (Lidar: `NONE`/`BASIC`/`EXTRA`/`FULL`; Radar and Acoustic: `NONE`/`BASIC`). The old `omni:sensor:Core:auxOutputType` / `omni:sensor:WpmDmat:auxOutputType` attributes were removed. Known issue: the channels value is effectively global per render-product-attach event ("last attach wins") — keep all RTX sensors on a stage at the same level.
