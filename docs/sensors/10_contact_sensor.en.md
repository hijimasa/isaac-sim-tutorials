---
title: Contact Sensor
---

# Contact Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Contact Sensor uses the PhysX Contact Report API to emulate contact/pressure pads. It filters contacts by the object it is placed in, supports an optional spherical region filter, and provides persistent contact data even when PhysX stops streaming. Properties: `radius`, `enabled`, `min threshold`, `max threshold`, `sensor period` (cannot exceed the physics rate).

## Creating a sensor

- **GUI**: Create a Physics Scene, select a prim, then `Create > Sensors > Contact_sensor`. Edit via Translate/Orientate and Raw USD Properties. Try the example at `Robotics Examples > Sensors > Contact Sensor`.
- **OmniGraph**: Use `On Playback Tick` → `Isaac Read Contact Sensor` (set Contact Sensor Prim) → `To String` → `Print Text`. Visualize with the `Isaac xPrim Radius Visualizer` node.
- **Python command**: `IsaacSensorCreateContactSensor` (only `parent` is required).
- **Python wrapper**: `isaacsim.sensors.physics.ContactSensor` — adds helper functions. Requires a collider prim + Contact Report API (added automatically).

## Reading output

Sensors are created on PLAY; moving the prim during simulation invalidates it. Three methods: `get_sensor_reading(path, use_latest_data)` (recommended, returns `CsSensorReading` with `is_valid`/`time`/`value`/`in_contact`), `ContactSensor.get_current_frame()` (dict), and the `Isaac Read Contact Sensor` OmniGraph node. `get_contact_sensor_raw_data()` returns raw `CsRawData` (ignores thresholds) but is deprecated.
