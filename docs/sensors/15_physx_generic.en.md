---
title: PhysX SDK Generic Sensor
---

# PhysX SDK Generic Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The PhysX SDK generic sensor uses PhysX raycasts to measure ground-truth depth with a **fully custom ray pattern**. Try `Robotics Examples > Sensors > Custom Pattern Range Sensor` (Load Sensor → Load Scene → Set Sensor Pattern → PLAY; Save Pattern Image to inspect the zigzag).

Deprecated since Isaac Sim 6.0: use `isaacsim.sensors.experimental.physics.RaycastSensor` instead — `sensor_pattern` maps to `rayDirections` (Cartesian), `origin_offsets` to `rayOrigins`, and batching/streaming to `rayTimeOffsets`. See the [official migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physx_generic_to_physics_raycast.html).

## Scanning-pattern parameters

- `streaming`: `True` = continuous streaming, `False` = send one batch and repeat.
- `sampling_rate`: scans per second.
- `batch_size`: scans per batch (must satisfy `sampling_rate/fps` or scanning slows down).
- `sensor_pattern`: Nx2 array of `[azimuth, zenith]` (azimuth from x-axis, zenith from z-axis).
- `origin_offsets`: optional Nx3 array of per-ray `[x,y,z]` offsets.

Patterns can be generated programmatically or loaded from CSV (`np.deg2rad(pattern).T.copy()`). When `send_next_batch(path)` returns `True`, feed the next batch via `set_next_batch_rays(path, pattern)` and `set_next_batch_offsets(path, offsets)`.
