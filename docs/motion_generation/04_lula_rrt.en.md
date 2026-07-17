---
title: Lula RRT
---

# Lula RRT

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated in Isaac Sim 6.0"
    The official page is marked Deprecated in Isaac Sim 6.0; the Robot Motion (Experimental) API is the recommended successor. Lula RRT still works in 6.0.

## Overview

The **Lula RRT** class produces a collision-free path from a c-space start to a c-space or task-space target — global planning in static environments (vs RMPflow's reactive local policy).

## What you will learn

- **Config**: `RRT(robot_description_path, urdf_path, rrt_config_path, end_effector_frame_name)`. The RRT config YAML (`step_size`, `max_iterations`, `distance_metric_weights`, `task_space_limits`, planning params, etc.) is RRT-specific. Simplify supported robots with `interface_config_loader.load_supported_path_planner_config("Franka", "RRT")`.
- **Planning**: `add_obstacle(...)`, `set_max_iterations(...)`, then per replan: `set_end_effector_target(...)` → `update_world()` → `PathPlannerVisualizer.compute_plan_as_articulation_actions(max_cspace_dist=.01)`. Pop one action per frame and `apply_action`. The example replans every 60 frames when the target moves.
- **Limitation**: `PathPlannerVisualizer` only visualizes — the densely interpolated path isn't time-optimal or smooth. Combine RRT with the [Lula Trajectory Generator](06_lula_trajectory_generator.md) (see the Path Planning Example under Robotics Examples) for sound following.
