---
title: Motion Policy Algorithm
---

# Motion Policy Algorithm

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

A Motion Policy is a collision-aware algorithm outputting per-frame actions to navigate one robot to one task-space target. The `MotionPolicy` interface pairs with `ArticulationMotionPolicy` to move a robot in a few lines. The provided implementation is [RMPflow](rmpflow.md) (Lula).

## Key concepts

- **Active vs watched joints**: `get_active_joints()` (directly controlled) and `get_watched_joints()` (observed only), each returning names in the expected order. E.g. RMPflow on the 9-DOF Franka controls the 7 arm joints; the gripper is watched-empty.
- **World state**: add obstacles from `isaacsim.core.api.objects` (RMPflow supports spheres/capsules/cuboids), query them via `update_world()`; unimplemented adders warn.
- **Robot state**: `set_robot_base_pose()` (defaults to origin) and `compute_joint_targets(active/watched positions & velocities)`.
- **Output**: next-frame position + velocity targets (always both). `ArticulationMotionPolicy.get_next_articulation_action()` maps the active-joint result to a full `ArticulationAction` (padding untouched joints with `None`). `MotionPolicyController` wraps a policy as a `BaseController`.
