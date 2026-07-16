---
title: RMPflow Tuning Guide
---

# RMPflow Tuning Guide

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Parameters that work for one robot usually work for morphologically similar robots and across many tasks. Start from an example config (7-DOF Franka Panda or 6-DOF UR10); rescale length-unit parameters for very different sizes, and adjust `cspace_target_rmp/robust_position_term_thresh` if the joint count differs.

## Tuning from scratch

1. **Disable all RMPs** (set `metric_weight`/`metric_scalar` to 0; for target RMP zero `min/max_metric_scalar` and `min_metric_alpha`; zero all `inertia` terms).
2. **Re-enable one at a time**, in order:
   - **cspace_target_rmp** — small `metric_scalar` (1–100, sets global scale); set a natural "ready" default configuration.
   - **target_rmp** — start with the directional S term off (`min_metric_alpha` 0, large `metric_alpha_length_scale`), boost off, large `max_metric_scalar`; tune `accel_p/d_gain`, `accel_norm_eps`.
   - **collision_rmp** — set `metric_scalar` comparable to `target_rmp/max_metric_scalar`.
   - **target_rmp (redux)** — re-enable the directional metric term (nonzero `min_metric_alpha`, reduce `metric_alpha_length_scale`).
   - **axis_target_rmp** — orientation alignment (with position-distance priority boosting).
   - **joint_limit_rmp**, then **damping_rmp** (with `target_rmp/inertia`) to reduce jerk.

See [RMPflow theory](rmpflow.md) and [Configuring RMPflow for a New Manipulator](../07_configure_rmpflow_denso.md).
