---
title: PhysX SDK Sensors
---

# PhysX SDK Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim's PhysX SDK sensors use **PhysX SDK raycasts** to measure range between objects, outputting exact PhysX measurements. The maximum output rate is the render rate. They do not interact with non-visual materials — they always report ground truth. Organized in the `isaacsim.sensors.physx` extension:

- [PhysX SDK Generic Sensor](15_physx_generic.md)
- [PhysX SDK Lidar](16_physx_lidar.md)
- [PhysX SDK Lightbeam Sensor](17_physx_lightbeam.md)
- [Proximity Sensor](13_proximity_sensor.md)

Deprecated since Isaac Sim 6.0: the `isaacsim.sensors.physx` extension is deprecated. Use `isaacsim.sensors.experimental.physics` instead, which provides the `RaycastSensor` as the replacement for PhysX-based range sensors.
