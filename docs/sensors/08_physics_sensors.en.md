---
title: Physics-Based Sensors
---

# Physics-Based Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim's physics-based sensors run on CPU physics simulations after rendering finishes, with access to prim physics properties (mass, velocity). They output exact measurements from the physics engine, which can be augmented in post-processing. The maximum output rate is the physics rate (use interpolation to exceed it), and ground-truth readings may already contain some noise. They live in the `isaacsim.sensors.experimental.physics` extension (the former `isaacsim.sensors.physics` extension is deprecated in Isaac Sim 6.0 — see the [migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physics_to_experimental_physics.html)):

- [Articulation Joint Sensors](09_articulation_force.md)
- [Contact Sensor](10_contact_sensor.md)
- [Effort Sensor](11_effort_sensor.md)
- [IMU Sensor](12_imu_sensor.md)
- Joint state sensor (new in 6.0 — official docs)
- Physics raycast sensor (new in 6.0, successor to the PhysX Lidar/Generic/Lightbeam sensors — official docs)

[Proximity Sensor](13_proximity_sensor.md) is provided by the `isaacsim.sensors.physx` extension and is now categorized under PhysX SDK sensors in the official docs.
