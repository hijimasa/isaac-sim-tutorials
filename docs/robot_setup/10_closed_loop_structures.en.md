---
title: Rig Closed-Loop Structures
---

# Rig Closed-Loop Structures

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import a gripper from Onshape
- How to configure closed-loop articulation structures
- How to break articulation loops
- How to add joint drives and mimic joints
- How to configure self-collision
- How to control a gripper with OmniGraph

## Getting Started

### Prerequisites

- Complete [Tutorial 5: Rig a Mobile Robot](05_rig_mobile_robot.md) before starting this tutorial.

### Estimated Time

Approximately 20-30 minutes.

### Overview

In this tutorial, you will import a Robotiq gripper from Onshape, configure its closed-loop articulation structure, add joint drives with mimic joints, and control the gripper using OmniGraph.

## Rigging the Robot

Adjust joints after importing from Onshape.

![Joint structure](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_robotiq_joints.png)

## Breaking the Articulation Loop

Convert the closed-loop structure into a form the simulator can process.

![Loop error](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_robotiq_loop_error.png)

![Loop resolved](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_robotiq_loop.png)

## Adding Joint Drives

Configure joint drives for actuation.

## Adding Mimic Joints

Set up dependent joints as mimic joints.

## Collision Meshes and Self-Collision

Configure collision meshes and enable self-collision.

## Controlling the Gripper with OmniGraph

Use OmniGraph to control gripper open/close operations.

## Summary

This tutorial covered the following topics:

1. Importing and configuring **closed-loop structures**
2. **Breaking articulation loops**
3. Adding **joint drives** and **mimic joints**
4. Configuring **self-collision**
5. Controlling the gripper with **OmniGraph**

## Next Steps

Proceed to the next tutorial, "[Tuning Joint Drive Gains](11_joint_tuning.md)", to learn how to optimize joint drive parameters.
