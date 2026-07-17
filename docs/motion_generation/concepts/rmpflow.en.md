---
title: RMPflow (Theory)
---

# RMPflow (Theory)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated"
    As of Isaac Sim 6.0, the Motion Generation extension (including the Lula implementation) is deprecated. For new development, consider the [Robot Motion (Experimental)](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html) API, which provides improved interfaces and additional features over Lula.

## Overview

A **Riemannian Motion Policy (RMP)** is an acceleration policy plus an "inertia matrix" M(q, q̇) (related to a Riemannian metric). **RMPflow** combines multiple competing RMPs into one global acceleration policy using Riemannian geometry. Acceleration policies (q̈ = π(q, q̇)) are integrated (e.g. Euler) to produce position/velocity control.

## Debugging features

`RmpFlow.visualize_collision_spheres()` / `visualize_end_effector_position()` show internal state; `set_ignore_state_updates(True)` decouples the policy from the simulated Articulation to isolate whether bad behavior comes from RMPflow or the PD gains.

## Configuration

Three files: **URDF** (kinematics, joint/link names, position limits), **robot description YAML** (c-space joints, default configuration, collision spheres, fixed joints), and **RMPflow config YAML** (parameters for all enabled RMPs). Each RMP is disabled by setting its `metric_scalar`/`metric_weight` to 0.

## RMP set

- **c-space_target_rmp** — default c-space posture for redundancy resolution (`position_gain`, `damping_gain`, `robust_position_term_thresh`, `inertia`).
- **target_rmp** — drives the end effector to a position target; metric blends directional S and isotropic I (`accel_p/d_gain`, `metric_alpha_length_scale`, `min/max_metric_scalar`, proximity boost).
- **axis_target_rmp** — aligns orientation to a target (with position-distance priority boosting).
- **joint_limit_rmp** — avoids joint limits.
- **joint_velocity_cap_rmp** — robot-specific velocity cap (`max_velocity`, `velocity_damping_region`).
- **collision_rmp** — repels collision spheres from obstacles (`repulsion_gain`, `metric_modulation_radius`).
- **damping_rmp** — nonlinear damping to reduce jerk.

See the [RMPflow Tuning Guide](rmpflow_tuning_guide.md) and the [Lula RMPflow tutorial](../03_rmpflow.md).
