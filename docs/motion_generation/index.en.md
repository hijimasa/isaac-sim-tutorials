---
title: Motion Generation Tutorials
---

# Motion Generation Tutorials

<span class="badge badge-advanced">Advanced</span>

Tutorials for manipulator motion generation in Isaac Sim (trajectory planning, inverse kinematics, reactive control).

## Overview

Isaac Sim provides **Lula** (high-performance library) and **cuRobo** (GPU-accelerated) for manipulator motion generation. Lula includes RMPflow, RRT, trajectory generation, and kinematics solvers; cuRobo adds batched collision-free IK and reactive control with mesh/Nvblox obstacles.

## Tutorials

- [Motion Generation Overview](01_overview.md)
- [Lula Robot Description and XRDF Editor](02_robot_description_editor.md)
- [Lula RMPflow](03_rmpflow.md)
- [Lula RRT](04_lula_rrt.md)
- [Lula Kinematics Solver](05_lula_kinematics.md)
- [Lula Trajectory Generator](06_lula_trajectory_generator.md)
- [Configuring RMPflow for a New Manipulator](07_configure_rmpflow_denso.md)
- [cuRobo and cuMotion](08_curobo.md)

## Concepts

Design and theory behind each algorithm: [Motion Generation Concepts](concepts/index.md) — [Motion Policy](concepts/motion_policy.md), [RMPflow](concepts/rmpflow.md), [RMPflow Tuning Guide](concepts/rmpflow_tuning_guide.md), [Path Planner](concepts/path_planner.md), [Lula RRT](concepts/lula_rrt.md), [Kinematics Solvers](concepts/kinematics_solver.md), [Trajectory Generation](concepts/trajectory_interface.md).
