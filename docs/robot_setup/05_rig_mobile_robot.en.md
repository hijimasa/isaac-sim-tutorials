---
title: Rig a Mobile Robot
---

# Rig a Mobile Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to analyze the joint configuration of a robot asset
- How to organize a USD hierarchy and group with XForms
- How to assign collision approximations (Convex Decomposition, cylinders, etc.)
- How to add prismatic/revolute joints and configure drives
- How to add articulations
- How to handle asset unit conversion

## Getting Started

### Prerequisites

- Complete [Tutorial 3: Articulate a Basic Robot](03_articulate_robot.md) before starting this tutorial.

### Estimated Time

Approximately 30 minutes.

### Overview

In this tutorial, you will convert an unrigged forklift USD asset into a fully articulated mobile robot. You will organize the hierarchy, assign collision meshes, define joints and drives, and add articulation components.

## Identifying the Joints

Analyze the seven degrees of freedom in the forklift:

- Four unactuated roller wheels
- One prismatic (linear) fork joint
- One wheel rotation joint
- One pivot joint

## Organizing the Hierarchy

1. Create XForms and group meshes logically (body, lift, wheels).

2. Set up proper parent-child relationships and transform alignment.

    ![Forklift (no transform)](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rig_forklift_1.png)

    ![Forklift (with transform)](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rig_forklift_2.png)

## Assigning Collision Meshes

1. Apply Convex Decomposition to body parts.

2. Apply cylinder approximation to wheels.

3. Configure collisions to prevent self-penetration.

    ![Convex Decomposition](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rig_forklift_3.png)

    ![Cylinder collision approximation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rig_forklift_5.png)

## Adding Joints and Drives

1. Create a prismatic joint for fork movement.

2. Create revolute joints for wheels.

3. Set appropriate damping and stiffness parameters.

    ![Prismatic joints](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rig_forklift_6.png)

    ![Revolute joints](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rig_forklift_7.png)

## Adding Articulations

Apply an articulation root to link all joints into a single physics-solved chain.

## Converting Asset Units

Handle unit conversion when integrating centimeter-based assets into meter-based scenes.

## Summary

This tutorial covered the following topics:

1. Analyzing the **joint configuration** of a robot asset
2. **Organizing the USD hierarchy** and grouping with XForms
3. Assigning **collision meshes**
4. Adding and configuring **joints and drives**
5. Adding **articulations**
6. Handling **unit conversion**

## Next Steps

Proceed to the next tutorial, "[Setup a Manipulator](06_setup_manipulator.md)", to learn how to import a robot arm from URDF and connect a gripper.
