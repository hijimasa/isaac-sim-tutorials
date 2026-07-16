---
title: Articulation Joint Sensors
---

# Articulation Joint Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Articulation sensors read the active and passive components of joint forces via `Articulation` / `ArticulationView` APIs:

- `get_applied_joint_efforts` — efforts set by the user through `set_joint_efforts`.
- `get_measured_joint_forces` — 6-dimensional spatial forces per joint (total joint forces); read from a fixed joint to mimic a force-torque sensor.
- `get_measured_joint_efforts` — active component (projection of joint forces on the motion direction).

The reported forces correspond to the joint connecting a child link to its parent (incoming joint forces). See the Japanese page for a full Script Editor example loading the Ant robot and mapping joint names to link indices.
