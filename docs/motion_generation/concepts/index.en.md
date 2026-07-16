---
title: Motion Generation Concepts
---

# Motion Generation Concepts

<span class="badge badge-advanced">Advanced</span>

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The Motion Generation API provides abstract interfaces for adding motion-control algorithms to Isaac Sim: it simplifies integrating new algorithms and gives a standard structure for comparing them. Three interfaces are provided:

- [Motion Policy Algorithm](motion_policy.md)
- [Path Planner Algorithm](path_planner.md)
- [Kinematics Solvers](kinematics_solver.md)

Robots are USD Articulations, but algorithms have their own kinematic representations. Interface functions (which joints an algorithm cares about, and their order) plus helper classes — **Articulation Motion Policy**, **Path Planner Visualizer**, **Articulation Kinematics Solver** — map joint states between the USD Articulation and the algorithm.

## Pages

[Motion Policy](motion_policy.md) · [RMPflow](rmpflow.md) · [RMPflow Tuning Guide](rmpflow_tuning_guide.md) · [Path Planner](path_planner.md) · [Lula RRT](lula_rrt.md) · [Kinematics Solvers](kinematics_solver.md) · [Trajectory Generation](trajectory_interface.md)
