---
title: Articulation Joint Sensors
---

# Articulation Joint Sensors

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Articulation sensors read the active and passive components of joint forces via the `Articulation` class from the `isaacsim.core.experimental.prims` extension (Isaac Sim 6.0):

- `get_link_incoming_joint_force()` — 6D force and torque (shape `(N, L, 3)` each) for each link's incoming joint; read from a fixed joint to mimic a force-torque sensor.
- `get_dof_projected_joint_forces()` — active component of the joint forces projected onto the motion direction for each DOF.

The reported forces correspond to the joint connecting a child link to its parent (incoming joint forces). See the Japanese page for a full Script Editor example loading the Ant robot and mapping joint names to link indices.
