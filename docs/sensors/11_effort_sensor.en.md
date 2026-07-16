---
title: Effort Sensor
---

# Effort Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Effort Sensor tracks torque (revolute joints) or force magnitude (linear joints) applied to individual joints.

## Usage

- **Scene setup**: add `simple_articulation.usd`, then drive `RevoluteJoint` (target velocity 90 deg/s, stiffness 0).
- **Create**: use `isaacsim.sensors.physics.scripts.effort_sensor.EffortSensor(prim_path, sensor_period, use_latest_data, enabled)`. Change `dof_name`/`buffer_size` via `update_dof_name`/`change_buffer_size`.
- **Read (Python)**: `get_sensor_reading(interpolation_function=None, use_latest_data=False)` returns an `EsSensorReading` (`is_valid`/`time`/`value`). A custom interpolation function can replace the default linear interpolation.
- **OmniGraph**: `On Playback Tick` → `Isaac Read Effort Node` (set Effort Prim to the joint) → `To String` → `Print Text`.
