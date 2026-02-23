---
title: Assemble a Simple Robot
---

# Assemble a Simple Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to create a robot body and wheels using primitive shapes
- How to configure Rigid Body and Collider physics properties
- How to examine collision meshes
- How to set friction and restitution parameters
- How to apply materials for visual appearance

## Getting Started

### Prerequisites

- Complete [Tutorial 1: Stage Setup](01_stage_setup.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will use GUI operations to build the basic structure of a two-wheeled robot using primitive shapes (cubes, cylinders). You will learn how to configure physics properties, examine collision meshes, and apply materials.

## Adding Objects to the Scene

1. Create an Xform for the body and add a Cube geometry.

2. Create two Xforms for the wheels and add Cylinder geometry to each.

3. Adjust the position and scale of each component.

    ![Robot body](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_simple_objs_body.png)

## Adding Physics Properties

1. Apply **Rigid Body with Colliders Preset** to each object.

2. Verify that gravity simulation is enabled.

    ![Physics properties](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_simple_objs_physics.webp)

## Examining Collision Meshes

1. Enable collision outline display in the viewport settings.

2. Verify the collision shapes on all objects.

    ![Collision](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_collision.png)

## Adding Contact and Friction Parameters

1. Create a Physics Material.

2. Adjust friction coefficients and restitution.

3. Assign the material to rigid bodies.

    ![Materials](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_materials.png)

## Setting Material Properties

1. Create OmniPBR materials for visual appearance.

2. Assign distinct colors to the body and wheels.

    ![New materials](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_new_materials.png)

## Summary

This tutorial covered the following topics:

1. Building a robot structure using **primitive shapes**
2. Configuring **Rigid Body and Collider** physics properties
3. Visualizing and examining **collision meshes**
4. Setting **friction and restitution** parameters
5. Applying **visual materials**

## Next Steps

Proceed to the next tutorial, "[Articulate a Basic Robot](03_articulate_robot.md)", to learn how to configure joints and articulations.
