---
title: Path Planner Algorithm
---

# Path Planner Algorithm

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated"
    As of Isaac Sim 6.0, the Motion Generation extension containing this API is deprecated. For new development, consider the [Robot Motion (Experimental)](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html) API.

## Overview

A Path Planner outputs c-space waypoints that, linearly interpolated, form a collision-free path from a start c-space pose to a c-space or task-space target. The `PathPlanner` interface mirrors [Motion Policy](motion_policy.md): `get_active_joints()`/`get_watched_joints()`, world-state adders + `update_world()` (Lula RRT supports spheres/capsules/cuboids), `set_robot_base_pose()`, and `compute_path(active, watched)`.

The linearly interpolated path has sharp c-space corners, so it is a component rather than a final trajectory. `PathPlannerVisualizer.compute_plan_as_articulation_actions(max_cspace_dist)` maps the path to a list of `ArticulationAction`s (interpolation density bounded by `max_cspace_dist`). For sound following, combine with the [Lula Trajectory Generator](trajectory_interface.md). Implementation: [Lula RRT](lula_rrt.md).
