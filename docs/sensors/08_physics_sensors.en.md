---
title: Physics-Based Sensors
---

# Physics-Based Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim's physics-based sensors run on CPU physics simulations after rendering finishes, with access to prim physics properties (mass, velocity). They output exact measurements from the physics engine, which can be augmented in post-processing. The maximum output rate is the physics rate (use interpolation to exceed it), and ground-truth readings may already contain some noise. They live in the `isaacsim.sensors.physics` extension:

- [Articulation Joint Sensors](09_articulation_force.md)
- [Contact Sensor](10_contact_sensor.md)
- [Effort Sensor](11_effort_sensor.md)
- [IMU Sensor](12_imu_sensor.md)
- [Proximity Sensor](13_proximity_sensor.md) (provided by the `isaacsim.sensors.physx` extension)
