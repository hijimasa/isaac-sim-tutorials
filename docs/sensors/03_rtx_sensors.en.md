---
title: RTX Sensors
---

# RTX Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

RTX sensors use the Omniverse RTX Renderer's **RTX Sensor SDK** to sense the environment across visual and non-visual spectra. An RTX Lidar can model returns from transparent or reflective surfaces; an RTX Radar can model returns accounting for material emissivity and reflectivity in the radio spectrum. Utilities live in the `isaacsim.sensors.rtx` extension, which includes:

- [RTX Lidar Sensor](04_rtx_lidar.md)
- [RTX Radar Sensor](05_rtx_radar.md)
- [RTX Sensor Annotators](06_rtx_annotators.md)
- [RTX Sensor Non-Visual Materials](07_rtx_materials.md)

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
