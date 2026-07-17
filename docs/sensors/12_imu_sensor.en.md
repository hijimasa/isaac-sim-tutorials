---
title: IMU Sensor
---

# IMU Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The IMU Sensor tracks body motion and outputs simulated accelerometer and gyroscope readings in local x/y/z axes (stage units). Properties: `enabled` and rolling-average filter widths `angularVelocityFilterWidth`, `linearAccelerationFilterWidth`, `orientationFilterWidth` (larger = smoother). (`sensorPeriod` is deprecated; the new extension reads every physics step.) Add IMUs to rigid-body prims.

Since Isaac Sim 6.0, the `isaacsim.sensors.physics` IMU Sensor is deprecated — use `isaacsim.sensors.experimental.physics.IMUSensor` instead.

## Creating a sensor

- **GUI**: Create a Physics Scene, select a prim, then `Create > Sensors > Imu Sensor`. Edit via Transform and Raw USD Properties. Try `Robotics Examples > Sensors > IMU Sensor`.
- **OmniGraph**: `On Playback Tick` → `Isaac Read IMU Node` (set IMU Prim, optionally `read gravity`) → `To String` → `Print Text`.
- **Python API**: `IMU.create(path, ...)` (authoring class), wrapped with `IMUSensor` — `IMUSensor(IMU.create("/World/Cube/imu_sensor", ..., translations=[[0, 0, 0]], orientations=[[1, 0, 0, 0]]))`. `translations` (local) and `positions` (world) are mutually exclusive; the authoring object is reachable as `sensor.imu`.

## Reading output

`IMUSensor.get_sensor_reading(read_gravity=True)` returns an `ImuSensorReading` C++ struct (`is_valid`, `time`, `linear_acceleration_x/_y/_z`, `angular_velocity_x/_y/_z`, `orientation_w/_x/_y/_z`). `IMUSensor.get_data(read_gravity=True)` returns a dict (`time`, `physics_step`, `linear_acceleration`, `angular_velocity`, `orientation` in wxyz). Pass `read_gravity=False` to exclude gravitational acceleration.
