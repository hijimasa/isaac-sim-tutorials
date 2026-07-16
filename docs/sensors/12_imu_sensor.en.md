---
title: IMU Sensor
---

# IMU Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The IMU Sensor tracks body motion and outputs simulated accelerometer and gyroscope readings in local x/y/z axes (stage units). Properties: `enabled`, `sensor period`, and rolling-average filter widths `angularVelocityFilterWidth`, `linearAccelerationFilterWidth`, `orientationFilterWidth` (larger = smoother). Add IMUs to rigid-body prims.

## Creating a sensor

- **GUI**: Create a Physics Scene, select a prim, then `Create > Sensors > Imu Sensor`. Edit via Transform and Raw USD Properties. Try `Robotics Examples > Sensors > IMU Sensor`.
- **OmniGraph**: `On Playback Tick` → `Isaac Read IMU Node` (set IMU Prim, optionally `read gravity`) → `To String` → `Print Text`.
- **Python command**: `IsaacSensorCreateImuSensor` (only `parent` required).
- **Python wrapper**: `isaacsim.sensors.physics.IMUSensor(...)`.

## Reading output

`get_sensor_reading(path, interpolation_function=None, use_latest_data=False, read_gravity=True)` returns an `IsSensorReading` (`is_valid`, `time`, `lin_acc_x/y/z`, `ang_vel_x/y/z`, `orientation`). `IMUSensor.get_current_frame(read_gravity=True)` returns a dict (`lin_acc`, `ang_vel`, `orientation`, `time`, `physics_step`). With a custom interpolation function and `read_gravity=True`, raw acceleration is passed to the function and gravity applied afterward.
