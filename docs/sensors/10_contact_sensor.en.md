---
title: Contact Sensor
---

# Contact Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Contact Sensor uses the PhysX Contact Report API to emulate contact/pressure pads. It filters contacts by the object it is placed in, supports an optional spherical region filter, and provides persistent contact data even when PhysX stops streaming. Properties: `radius` (`-1` uses the prim's collision geometry), `enabled`, `min threshold`, `max threshold`. (`sensorPeriod` is deprecated; the new extension reads every physics step.)

Since Isaac Sim 6.0, the `isaacsim.sensors.physics` Contact Sensor is deprecated — use `isaacsim.sensors.experimental.physics.ContactSensor` instead.

## Creating a sensor

- **GUI**: Create a Physics Scene, select a prim, then `Create > Sensors > Contact_sensor`. Edit via Translate/Orientate and Raw USD Properties. Try the example at `Robotics Examples > Sensors > Contact Sensor`.
- **OmniGraph**: Use `On Playback Tick` → `Isaac Read Contact Sensor` (set Contact Sensor Prim) → `To String` → `Print Text`. Visualize with the `Isaac xPrim Radius Visualizer` node.
- **Python API**: `Contact.create(path, ...)` (authoring class), wrapped with `ContactSensor` for runtime access — `ContactSensor(Contact.create("/World/Cube/Contact_Sensor", ...))`. Requires an enabled rigid-body ancestor + Contact Report API (applied automatically by `Contact.create()`).
- Property setters/getters (`set_min_threshold`, `set_radius`, ...) live on the authoring object, reachable as `sensor.contact`. `translations` (local) and `positions` (world) are mutually exclusive.

## Reading output

Sensors are created on Play; moving the prim during simulation invalidates it. Three methods: `ContactSensor.get_sensor_reading()` (returns `ContactSensorReading` with `is_valid`/`time`/`value`/`in_contact`), `ContactSensor.get_data()` (dict with `time`/`physics_step`/`in_contact`/`force`/`number_of_contacts`), and the `Isaac Read Contact Sensor` OmniGraph node. `ContactSensor.get_raw_data()` returns raw per-contact records (ignores thresholds); call `add_raw_contact_data_to_frame()` to include a `contacts` list in `get_data()`.
