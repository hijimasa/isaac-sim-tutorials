---
title: Lula RRT (Concept)
---

# Lula RRT (Concept)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

A Lula implementation of RRT fulfilling the [Path Planner](path_planner.md) interface: c-space RRT uses **RRT-Connect**, task-space RRT uses **Jacobian-transpose RRT**. It does **not** support orientation targets.

Configuration requires three files: a **URDF** (kinematics, joint/link names, position limits), a **robot description YAML** (c-space joints + default configuration), and an **RRT config YAML** (termination conditions, exploration weights, step size — editable via `RRT.set_param()`). See the [Lula RRT tutorial](../04_lula_rrt.md).
