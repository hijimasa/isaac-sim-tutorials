---
title: cuRobo and cuMotion
---

# cuRobo and cuMotion

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

**cuRobo** (NVIDIA Research) is a high-performance, GPU-accelerated motion generation library for manipulators — a standalone Python library interfacing directly with Isaac Sim. **NVIDIA cuMotion** (Developer Preview in Isaac 3.0) is a production motion-generation package using cuRobo as its backend, providing collision-free planning via a MoveIt 2 plugin and ROS 2 packages.

!!! warning
    NvBlox-in-cuRobo examples have known issues; the cuRobo tutorial is not supported on aarch64.

## Getting started

Follow the cuRobo installation instructions (supports Isaac Sim 2022.2.1+). In the cuRobo docs, see **"Using Isaac Sim"** for standalone examples (collision checking, motion generation, IK, MPPI, multi-arm reaching) and **"Using with Depth Camera"** for obstacle-aware generation with pre-generated nvblox SDFs or online mapping with a physical RealSense. For cuMotion via the ROS 2 bridge, see the Isaac ROS documentation.
