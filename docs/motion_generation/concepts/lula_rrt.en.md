---
title: Lula RRT (Concept)
---

# Lula RRT (Concept)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated"
    As of Isaac Sim 6.0, the Motion Generation extension (including the Lula implementation) is deprecated. For new development, consider the [Robot Motion (Experimental)](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html) API, which provides improved interfaces and additional features over Lula.

## Overview

A Lula implementation of RRT fulfilling the [Path Planner](path_planner.md) interface: c-space RRT uses **RRT-Connect**, task-space RRT uses **Jacobian-transpose RRT**. It does **not** support orientation targets.

Configuration requires three files: a **URDF** (kinematics, joint/link names, position limits), a **robot description YAML** (c-space joints + default configuration), and an **RRT config YAML** (termination conditions, exploration weights, step size — editable via `RRT.set_param()`). See the [Lula RRT tutorial](../04_lula_rrt.md).
