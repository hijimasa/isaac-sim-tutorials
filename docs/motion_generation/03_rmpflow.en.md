---
title: Lula RMPflow
---

# Lula RMPflow

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated in Isaac Sim 6.0"
    The official page is marked Deprecated in Isaac Sim 6.0; the Robot Motion (Experimental) API is the recommended successor. Lula RMPflow still works in 6.0. The Motion Generation Examples extension (`isaacsim.robot_motion.motion_generation.examples`) is deprecated too — `isaacsim.robot_motion.cumotion.examples` is the replacement.

## Overview

**RMPflow** is a reactive local motion policy that generates smooth motions to task-space targets while avoiding dynamic obstacles. The `RmpFlow` class implements the Motion Policy Algorithm interface and pairs with `ArticulationMotionPolicy` to drive a robot.

## What you will learn

- **Direct instantiation**: `RmpFlow(robot_description_path, urdf_path, rmpflow_config_path, end_effector_frame_name, maximum_substep_size)` (configs under the `motion_generation` extension's `/motion_policy_configs`). Each frame: `set_end_effector_target(...)`, then `ArticulationMotionPolicy.get_next_articulation_action(step)` → `apply_action`.
- **World state**: register obstacles via `add_obstacle(...)`, call `update_world()` each frame, and `set_robot_base_pose(...)` if the base moves (positions are in world coordinates).
- **Supported robots**: `load_supported_motion_policy_config("Franka", "RMPflow")` → `RmpFlow(**rmp_config)`; list names with `get_supported_robot_policy_pairs()`.
- **Debugging**: `visualize_collision_spheres()` and `set_ignore_state_updates(True)` decouple the policy from the simulated Articulation to diagnose issues (e.g. weak gains causing the robot to lag behind commanded motions).

!!! note
    RMPflow uses the config URDF's structure — update the URDF (and Robot Description file) for assembled robots (e.g. UR10 + gripper).
