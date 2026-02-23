---
title: Rig a Legged Robot
---

# Rig a Legged Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to set the initial robot position to match a locomotion policy
- How to configure Joint State API and drive APIs
- How to configure joint settings (stiffness, damping, effort limits, armature)
- How to verify the configuration using a validation script

## Getting Started

### Prerequisites

- Complete [Tutorial 3: Articulate a Basic Robot](03_articulate_robot.md) before starting this tutorial.

### Estimated Time

Approximately 20-30 minutes.

### Overview

In this tutorial, you will learn how to rig a legged robot to match a locomotion policy's configuration specifications, using the H1 humanoid robot as an example. You will set the initial position, configure joints, and verify the setup.

## Setting Initial Robot Position

1. Open the H1 USD file.

2. Create the Joint State API.

3. Select and filter joints.

4. Add Physics Joint State Angular and Angular Drive APIs.

    ![Initial position](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_1.png)

5. Set target position and velocity attributes.

6. Convert radians to degrees.

7. Prevent infinite falling with a Fixed Joint.

    ![Simulation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_2.webp)

## Setting Joint Configuration

1. Configure actuator properties from the environment definition.

2. Set stiffness and damping values.

3. Set effort limits.

4. Configure armature and friction.

5. Set maximum joint velocity.

    ![Joint configuration](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_3.png)

## Verifying Joint Configuration

1. Run the verification script in Script Editor.

2. Confirm that output values match the specifications.

    ![Verification results](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_4.png)

## Summary

This tutorial covered the following topics:

1. Setting the **initial robot position**
2. Configuring **Joint State API** and drive APIs
3. Configuring **joint settings** (stiffness, damping, effort limits)
4. Verifying configuration with a **validation script**
