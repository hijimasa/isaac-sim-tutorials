---
title: Setup a Manipulator
---

# Setup a Manipulator

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import the UR10e robot from a URDF file
- How to import the Robotiq 2F-140 gripper from a URDF file
- How to connect the robot arm and gripper via GUI operations
- How to use the Robot Assembler for connection

## Getting Started

### Prerequisites

- Complete [Tutorial 5: Rig a Mobile Robot](05_rig_mobile_robot.md) before starting this tutorial.
- Linux environment (required for the ROS 2 URDF Importer)

### Estimated Time

Approximately 20-30 minutes.

### Overview

In this tutorial, you will import the UR10e robot arm and Robotiq 2F-140 gripper from URDF files and connect them as a single articulation. You will learn two methods: manual connection via GUI and automated connection using the Robot Assembler.

## Build and Install the UR Description Package

1. Clone the UR Description Package.

2. Build using Python 3.11 or system ROS.

## Import the UR10e Robot

1. Enable the ROS 2 URDF Importer Extension.

2. Launch the URDF Publisher Topic.

3. Import UR10e into Isaac Sim.

    ![UR10e import](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10_importer.png)

## Import the Robotiq 2F-140 Gripper

1. Convert XACRO to URDF.

2. Import the gripper into Isaac Sim.

    ![Robotiq import](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_robotiq_importer.png)

## Connect UR10e with Robotiq 2F-140

### Option 1: GUI-based Connection

Manually connect the gripper to the robot arm's end effector.

![Manual connection](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_connect_gripper_manual.png)

### Option 2: Robot Assembler Connection

Use the Robot Assembler tool for automated connection.

![Robot Assembler](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_connect_gripper_assembler.png)

## Summary

This tutorial covered the following topics:

1. Importing robot arm and gripper from **URDF**
2. Manual connection using **GUI**
3. Automated connection using **Robot Assembler**

## Next Steps

Proceed to the next tutorial, "[Configure a Manipulator](07_configure_manipulator.md)", to learn how to tune physics properties and joint drive gains.
