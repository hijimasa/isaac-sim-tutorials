---
title: ROS 2 Quality of Service (QoS)
---

# ROS 2 Quality of Service (QoS)

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Set QoS for ROS 2 OmniGraph nodes and build a static publisher with a custom QoS profile.

!!! warning "Known issue"
    The ROS2 QoS Profile node cannot save custom profiles in USD unless `createProfile` is set to "Custom" before modifying other fields.

## Setting QoS Profiles

Create a Generic Publisher (**Tools > Robotics > ROS 2 OmniGraphs > Generic Publisher**, Publish String). Every ROS 2 OmniGraph node has a `qosProfile` JSON-string input; the default is:

```json
{
    "history": "keepLast",
    "depth": 10,
    "reliability": "reliable",
    "durability": "volatile",
    "deadline": 0.0,
    "lifespan": 0.0,
    "liveliness": "systemDefault",
    "leaseDuration": 0.0
}
```

(`depth` integer; `deadline`/`lifespan`/`leaseDuration` floats.) Rather than hand-writing JSON, add a **ROS2 QoS Profile** node and connect its output to publishers/subscribers. Set `createProfile` to **Sensor Data**, press Play, and verify with:

```bash
ros2 topic info /topic -v
```

Fast DDS may report depth as UNKNOWN; Cyclone DDS (Linux only) can retrieve it.

## Static Publishers

Useful for publish-once messages that must reach late-joining subscribers. Add **On Stage Event** (eventName `Simulation Start Play`) and **Countdown** (duration 3, period 1 — the publisher uses 2 frames for setup and publishes on the 3rd). Set the QoS Profile node to **Default for publisher/subscribers** with depth `1` and durability `transientLocal`. After Play, `ros2 topic echo /topic` shows the message even in a second terminal opened later.

## Next Steps

- [Tutorial 12: ROS2 Joint Control: Extension Python Scripting](12_manipulation.md)
