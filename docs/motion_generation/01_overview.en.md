---
title: Motion Generation Overview
---

# Motion Generation Overview

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated in Isaac Sim 6.0"
    The official Motion Generation (Lula) page is marked Deprecated in Isaac Sim 6.0. For new development, use the Robot Motion (Experimental) API (`isaacsim.robot_motion.experimental.motion_generation`), the cuMotion integration, or the PINK integration. Lula still works in 6.0.

## Overview

**Lula** is a high-performance motion generation library for robotic manipulation. Isaac Sim exposes:

- **RMPflow** — real-time, reactive local policies guiding a manipulator to a task-space target while avoiding dynamic obstacles.
- **RRT** (RRT-Connect, JT-RRT) — global planning in static environments.
- **Trajectory generation** — time-optimal trajectories for c-space/task-space paths.
- **Kinematics solvers** — performant forward/inverse kinematics.

Isaac Sim also interfaces with **cuRobo**, a GPU-accelerated library adding batched collision-free IK, collision-free motion planning, and reactive control with mesh/Nvblox obstacles.

## Tools

[Robot Description & XRDF Editor](02_robot_description_editor.md) · [Lula RMPflow](03_rmpflow.md) · [Lula RRT](04_lula_rrt.md) · [Lula Kinematics Solver](05_lula_kinematics.md) · [Lula Trajectory Generator](06_lula_trajectory_generator.md) · [Configure RMPflow for a New Manipulator](07_configure_rmpflow_denso.md) · [cuRobo and cuMotion](08_curobo.md)

## Examples

Interactive: `Windows > Examples > Robotics Examples` → Follow Target, RoboFactory, RoboParty (use **RESET**, not STOP/PLAY). Standalone: `follow_target_with_rmpflow.py` (Franka and UR10) and `follow_target_with_ik.py` (UR10) under `standalone_examples/api/isaacsim.robot.experimental.manipulators/`.
