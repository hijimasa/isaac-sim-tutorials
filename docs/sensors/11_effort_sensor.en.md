---
title: Effort Sensor
---

# Effort Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Effort Sensor tracks torque (revolute joints) or force magnitude (linear joints) applied to individual joints.

Since Isaac Sim 6.0, the `isaacsim.sensors.physics` Effort Sensor is deprecated — use `isaacsim.sensors.experimental.physics.EffortSensor` instead.

## Usage

- **Scene setup**: add `simple_articulation.usd`, then drive `RevoluteJoint` (target velocity 90 deg/s, stiffness 0).
- **Create**: use `isaacsim.sensors.experimental.physics.EffortSensor(path="/World/simple_articulation/Arm/RevoluteJoint", enabled=True)` — the joint prim itself is the sensor's prim (no separate authoring class). Change `dof_name`/`buffer_size` via `update_dof_name`/`change_buffer_size`.
- **Read (Python)**: `get_sensor_reading()` returns an `EffortSensorReading` (`is_valid`/`time`/`value`); `get_data()` returns a dict (`value`/`is_valid`/`time`/`physics_step`).
- **OmniGraph**: `On Playback Tick` → `Isaac Read Effort Node` (set Effort Prim to the joint) → `To String` → `Print Text`.
