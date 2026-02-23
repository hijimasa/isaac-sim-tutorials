---
title: Configure a Manipulator
---

# Configure a Manipulator

## Learning Objectives

After completing this tutorial, you will have learned:

- How to adjust articulation solver settings
- How to configure physics materials (friction)
- How to set joint effort limits
- How to inspect articulations using Physics Inspector
- How to tune joint drive gains using Gain Tuner

## Getting Started

### Prerequisites

- Complete [Tutorial 6: Setup a Manipulator](06_setup_manipulator.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will configure physics properties, joint effort limits, and drive gains for the UR10e robot and Robotiq 2F-140 gripper to improve stability and accuracy for manipulation tasks.

## Adjusting the Articulation

1. Select the `ur/root_joint` prim and enable Articulation.

2. Increase the **Solver Position Iterations Count**.

3. Increase the **Solver Velocity Iterations Count**.

4. Decrease the **Sleep Threshold**.

5. Decrease the **Stabilization Threshold**.

    ![Articulation properties](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_articulation_properties.png)

## Adding Physics Materials

1. Create a Physics Material (Rigid Body Material).

2. Configure static and dynamic friction.

3. Apply the material to the gripper finger tips.

## Configuring Joint Effort Limits

1. Select the `finger_joint` prim.

2. Set the **Max Force** value.

## Inspecting the Robot Articulation

1. Open the **Physics Inspector**.

2. Refresh the articulation and test joint positioning.

    ![Physics Inspector](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_physics_inspector.png)

## Tuning Gains with Gain Tuner

1. Access the **Gain Tuner** tool.

2. Select the robot articulation and adjust joint gains.

    ![Gain Tuner](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_gain_tuner_ur10e.png)

## Summary

This tutorial covered the following topics:

1. Adjusting **articulation** solver settings
2. Configuring **physics materials** (friction)
3. Setting **joint effort limits**
4. Inspecting articulations with **Physics Inspector**
5. Tuning joint gains with **Gain Tuner**

## Next Steps

Proceed to the next tutorial, "[Generate Robot Configuration File](08_generate_robot_config.md)", to learn how to generate configuration files for kinematics solvers.
