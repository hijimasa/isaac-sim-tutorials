---
title: Proximity Sensor
---

# Proximity Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Proximity Sensor wraps a physics callback that can be attached to any prim. During simulation it records collisions between its prim and other prims each frame, accessible via a callback. It is provided by the **`isaacsim.sensors.physx`** extension (not `isaacsim.sensors.physics`).

## Usage

Enable the extension (`enable_extension("isaacsim.sensors.physx")`), then `from isaacsim.sensors.physx import ProximitySensor, register_sensor, clear_sensors`. Create `s = ProximitySensor(cube_1.prim)`, `register_sensor(s)`, and add a physics callback that reads `s.get_data()` — a dict keyed by colliding prim path, each entry containing `distance` and `duration`. See the Japanese page for a full two-cube standalone example.
