---
title: Lula Trajectory Generator
---

# Lula Trajectory Generator

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Lula Trajectory Generator creates c-space and task-space trajectories easily applied to a robot Articulation. All generators share a robot-description + URDF config.

## What you will learn

- **C-space**: `LulaCSpaceTrajectoryGenerator` connects c-space waypoints via spline interpolation. `compute_c_space_trajectory(points)` gives a **time-optimal** trajectory (saturates a velocity/acceleration/jerk limit throughout); `compute_timestamped_c_space_trajectory(points, timestamps)` hits waypoints at set times. Returns `None` if unreachable.
- **Task-space (simple)**: `LulaTaskSpaceTrajectoryGenerator.compute_task_space_trajectory_from_points(positions, quaternions, end_effector_name)` linearly interpolates between waypoints.
- **Task-space (advanced)**: build a `lula.TaskSpacePathSpec` (`add_translation`, `add_rotation`, `add_linear_path`, `add_three_point_arc`, `add_tangent_arc`, each with constant/tangent/target orientation) and optionally combine with a `lula.CSpacePathSpec` inside a `lula.CompositePathSpec` (transition modes `LINEAR_TASK_SPACE`/`FREE`/`SKIP`), then `compute_task_space_trajectory_from_path_spec(spec, ee_name)`.
- **Apply**: wrap any trajectory in `ArticulationTrajectory(articulation, trajectory, physics_dt)` and use `get_action_sequence()`.
