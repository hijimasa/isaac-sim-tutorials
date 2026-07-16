---
title: Trajectory Generation
---

# Trajectory Generation

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The extension defines c-space and task-space trajectories via three pieces:

- **Trajectory Interface** — returns c-space position as a continuous function of time within `[start_time, end_time]`, with accessors `start_time`, `end_time`, `active_joints`, and `joint_targets(time)`.
- **Articulation Trajectory** — maps a `Trajectory` to a robot: `get_action_at_time(time)` and `get_action_sequence(timestep)`. Bring the robot to the trajectory's initial state before following.
- **Lula Trajectory Generator** — `LulaCSpaceTrajectoryGenerator` (spline interpolation between c-space waypoints, time-optimal, zero start/end velocity) and `LulaTaskSpaceTrajectoryGenerator` (task-space targets or `lula.TaskSpacePathSpec` primitives, internally converted to c-space via the kinematics solver). Config: URDF + robot description YAML (with acceleration/jerk limits). See the [tutorial](../06_lula_trajectory_generator.md).
