---
title: Kinematics Solvers
---

# Kinematics Solvers

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated"
    As of Isaac Sim 6.0, the Motion Generation extension containing this API is deprecated. For new development, consider the [Robot Motion (Experimental)](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html) API.

## Overview

The `KinematicsSolver` interface computes forward/inverse kinematics at any frame, with one implementation ([Lula Kinematics Solver](../05_lula_kinematics.md)). It has its own robot representation:

- **`get_joint_names()`** — joints of interest and their order (FK input / IK output match this shape).
- **`get_all_frame_names()`** — frames referenceable by name (from the solver config, not necessarily the Articulation).
- **`set_robot_base_pose()`** — the solver works in world coordinates; set to origin for base-frame I/O.
- **`supports_collision_avoidance()`** — optional; collision-aware solvers fulfill the same world-state functions as a Motion Policy.

`ArticulationKinematicsSolver` maps to the Articulation: FK queries joint positions in `get_joint_names()` order; IK returns an `ArticulationAction`, warm-started from the current pose. `LulaKinematicsSolver` (no collision avoidance) adds settings like `set_max_iterations()`. Config: URDF + robot description YAML.
