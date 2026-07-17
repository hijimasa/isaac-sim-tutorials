---
title: PhysX SDK Lightbeam Sensor
---

# PhysX SDK Lightbeam Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The PhysX SDK Lightbeam sensor uses PhysX raycasts to detect whether an object has intersected a light beam. Specify the number of rays and height to build a safety light "curtain".

Deprecated since Isaac Sim 6.0: use `isaacsim.sensors.experimental.physics.RaycastSensor` configured as a beam curtain — `numRays` maps to the length of `rayOrigins`/`rayDirections`, `curtainLength`/`curtainAxis` to `rayOrigins`, `forwardAxis` to `rayDirections`; read per-ray depths/hit positions/normals via `get_sensor_reading()`. See the [official migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physx_lightbeam_to_physics_raycast.html).

## Usage

Run `Robotics Examples > Sensors > Lightbeam` (activate via `Windows > Examples > Robotics Examples`). Press PLAY to populate the per-beam data — whether each beam was hit, the linear depth of the hit, and the exact xyz hit position. `SHIFT + LEFT_CLICK` to drag the cube or sensor and watch the readings change.
