---
title: Configuring RMPflow for a New Manipulator
---

# Configuring RMPflow for a New Manipulator

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

This tutorial fully configures RMPflow on a new robot (Denso **Cobotta Pro 900**, 6-DOF) after creating a Robot Description File. Verify configs interactively with the **Lula Test Widget** (`Tools > Robotics > Lula Test Widget`).

## Three config files

1. **URDF** — kinematics, joint/link names, position limits (masses/inertia/meshes ignored).
2. **Robot Description YAML** — from the Robot Description Editor.
3. **RMPflow config YAML** — 50+ parameters; the template (tuned for the Franka Panda) is a good start for most 6/7-DOF arms.

## Key steps

- **Bare minimum**: set `joint_limit_buffers` to the robot's DOF count (6), omit `rmp_params`, and point `body_collision_controllers` at a real URDF frame (e.g. `right_inner_finger`).
- **Self-collision**: `body_cylinders` (capsules approximating the base/links) and `body_collision_controllers` (spheres on URDF frames) may not collide. Be conservative only where self-collision is actually observed.
- **End-effector frame**: RMPflow's EE frame must exist in the URDF. Add a fixed `gripper_center` link offset from `onrobot_rg6_base_link` (e.g. Z `.24`).
- **Parameters**: mostly reuse the template; tune the robot-specific `joint_velocity_cap_rmp` (`max_velocity`, `velocity_damping_region`) to the URDF joint velocity limits. See the RMPflow Tuning Guide for details.
