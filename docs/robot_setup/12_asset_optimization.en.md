---
title: Asset Optimization
---

# Asset Optimization

## Learning Objectives

After completing this tutorial, you will have learned:

- Asset structure optimization techniques
- Mesh merging (Merge Mesh)
- Performance improvement through scenegraph instancing
- Comparing performance before and after optimization

## Getting Started

### Prerequisites

- Complete [Tutorial 3: Articulate a Basic Robot](03_articulate_robot.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will learn techniques for improving robot asset performance in Isaac Sim using the Jetbot robot as an example. Through asset structure optimization, mesh merging, and scenegraph instancing, you will achieve performance improvements from 40 FPS to 64 FPS.

## Loading the Robot

Load the Jetbot robot asset.

![Initial state](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_1.webp)

## Asset Structure Optimization

### Setting Up Reparenting and Layers

Prepare for reorganizing the asset structure.

### Creating Asset Structure

Reorganize into an optimal structure.

### Merging Meshes

Use the Merge Mesh tool to consolidate unnecessary mesh nodes.

![Mesh merging](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_5.png)

## Scenegraph Instancing

Reduce memory usage and rendering load by reusing identical meshes.

![Instancing](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_12.png)

## Other Considerations

Additional tips and best practices for performance optimization.

## Summary

This tutorial covered the following topics:

1. **Asset structure** optimization
2. **Mesh merging** (Merge Mesh)
3. **Scenegraph instancing**
4. **Measuring and improving** performance

## Next Steps

Proceed to the next tutorial, "[Rig a Legged Robot](13_rig_legged_robot.md)", to learn how to rig a legged robot for a locomotion policy.
