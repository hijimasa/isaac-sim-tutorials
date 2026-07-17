---
title: Lula Kinematics Solver
---

# Lula Kinematics Solver

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated in Isaac Sim 6.0"
    The official page is marked Deprecated in Isaac Sim 6.0; the Robot Motion (Experimental) API is the recommended successor. The Lula Kinematics Solver still works in 6.0.

## Overview

`LulaKinematicsSolver` computes forward/inverse kinematics for a robot defined by a robot-description + URDF (same files as Lula RMPflow). It is purely kinematic (no collision spheres needed) and works at any frame in the URDF (`get_all_frame_names()`).

## What you will learn

- **Instantiate**: `LulaKinematicsSolver(robot_description_path, urdf_path)` (or `interface_config_loader.load_supported_lula_kinematics_solver_config("Franka")`).
- **Articulation wrapper**: `ArticulationKinematicsSolver(articulation, solver, end_effector_name)` → `compute_end_effector_pose()` (FK) and `compute_inverse_kinematics(pos, orient)` (IK, warm-started from the current pose, returns `(action, success)`). Apply only if `success`.
- **Base pose**: call `set_robot_base_pose(...)` each frame so FK/IK use world coordinates.

!!! note
    IK alone yields only a rudimentary path; combine with planning/trajectory generation for realistic motion. The solver also works without an Articulation on the stage.
