---
title: Articulate a Basic Robot
---

# Articulate a Basic Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add revolute joints and configure rotation axes
- How to configure joint drives (angular velocity control)
- How to add an articulation root
- How to implement a velocity controller using ActionGraph

## Getting Started

### Prerequisites

- Complete [Tutorial 2: Assemble a Simple Robot](02_assemble_robot.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will connect the robot body and wheels from the previous tutorial using joints, configure articulations to create a functioning robot, and add a velocity controller to control the robot during simulation.

## Adding Joints

1. Create a Scope to organize joints.

2. Select the body and wheel objects, then add revolute joints.

3. Configure the rotation axes and organize joints within the Scope.

    ![Joint configuration](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_joints.png)

## Adding a Joint Drive

1. Apply angular drive properties with velocity control settings.

2. Configure damping and target velocity parameters.

    ![Joint drives](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_joint_drives.webp)

## Adding Articulation

1. Set an articulation root on the mock_robot.

2. Verify that simulation performance and physics fidelity are improved.

    ![Interaction](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_interaction.webp)

## Adding a Controller

1. Create an ActionGraph scope.

2. Implement a Joint Velocity controller to command robot movement during simulation.

    ![Controller](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_controller.png)

## Summary

This tutorial covered the following topics:

1. Adding **revolute joints** and configuring rotation axes
2. Configuring **joint drives** (angular velocity control)
3. Adding an **articulation root**
4. Implementing a velocity controller using **ActionGraph**

## Next Steps

Proceed to the next tutorial, "[Add Camera and Sensors](04_camera_sensors.md)", to learn how to attach camera sensors to a robot.
