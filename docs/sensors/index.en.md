---
title: Sensor Tutorials
---

# Sensor Tutorials

<span class="badge badge-beginner">Beginner</span>

Tutorials for using RTX, physics-based, and PhysX SDK sensors in Isaac Sim.

## Overview

Isaac Sim sensors fall into three families:

- **Camera / depth sensors** — based on the USD Camera prim; images, depth, and calibration.
- **RTX sensors** — physically based rendering via the RTX renderer, interacting with non-visual materials (LiDAR / Radar / Acoustic).
- **Physics-based / PhysX SDK sensors** — ground-truth contact, IMU, and range via CPU physics or raycasts.

!!! note "API reorganization in Isaac Sim 6.0"
    In Isaac Sim 6.0, `isaacsim.sensors.camera` / `isaacsim.sensors.rtx` are replaced by `isaacsim.sensors.experimental.rtx`, and `isaacsim.sensors.physics` by `isaacsim.sensors.experimental.physics` (the old extensions are deprecated). The tutorials are updated for the new APIs.

## Tutorials

### Camera & Depth

- [Camera Sensors](01_camera_sensors.md)
- [Depth Sensors](02_depth_sensors.md)

### RTX Sensors

- [RTX Sensors](03_rtx_sensors.md)
- [RTX Lidar Sensor](04_rtx_lidar.md)
- [RTX Radar Sensor](05_rtx_radar.md)
- [RTX Sensor Annotators](06_rtx_annotators.md)
- [RTX Sensor Non-Visual Materials](07_rtx_materials.md)

### Physics-Based Sensors

- [Physics-Based Sensors](08_physics_sensors.md)
- [Articulation Joint Sensors](09_articulation_force.md)
- [Contact Sensor](10_contact_sensor.md)
- [Effort Sensor](11_effort_sensor.md)
- [IMU Sensor](12_imu_sensor.md)

### PhysX SDK Sensors

- [PhysX SDK Sensors](14_physx_sensors.md)
- [Proximity Sensor](13_proximity_sensor.md)
- [PhysX SDK Generic Sensor](15_physx_generic.md)
- [PhysX SDK Lidar](16_physx_lidar.md)
- [PhysX SDK Lightbeam Sensor](17_physx_lightbeam.md)

!!! note "New official topics in 6.0"
    The Isaac Sim 6.0 docs add pages for structured light cameras, the RTX Acoustic sensor, multi-tick rendering, custom RTX sensor profiles, the joint state sensor, and the physics raycast sensor — see the official sensors section.
