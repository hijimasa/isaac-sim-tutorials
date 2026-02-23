---
title: Robot Setup Tutorials
---

# Robot Setup Tutorials

## Overview

These GUI tutorials walk you through setting up your virtual world and building robot digital twins with various NVIDIA Isaac Sim features. In the process, you will learn where to find frequently used properties, settings, and tools, and familiarize yourself with the toolbars, icons, and OpenUSD standards.

The tutorials are organized into **Beginner, Intermediate, and Advanced** levels, providing a progressive learning path. We recommend starting with the wheeled robot section to learn essential beginner concepts.

## Beginner: Setup a Wheeled Robot

<span class="badge badge-beginner">Beginner</span>

Learn fundamental concepts that apply to all robot types. Starting from stage setup, you will build a robot from primitive shapes, connect them with joints and articulations, attach cameras, and rig a real robot asset into a fully functional mobile robot.

![Wheeled robot setup](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_interaction.webp)

!!! example "[Tutorial 1: Stage Setup](01_stage_setup.md)"
    Learn how to configure stage properties, create a Physics Scene, and add a ground plane and lighting.

!!! example "[Tutorial 2: Assemble a Simple Robot](02_assemble_robot.md)"
    Learn how to build a robot structure using primitive shapes, configure physics properties, and apply materials.

!!! example "[Tutorial 3: Articulate a Basic Robot](03_articulate_robot.md)"
    Learn how to add revolute joints, configure joint drives, add an articulation root, and implement a velocity controller.

!!! example "[Tutorial 4: Add Camera and Sensors](04_camera_sensors.md)"
    Learn how to create camera sensors, inspect output with Camera Inspector, and attach cameras to a robot.

!!! example "[Tutorial 5: Rig a Mobile Robot](05_rig_mobile_robot.md)"
    Learn how to convert a forklift USD asset into a fully articulated mobile robot.

## Intermediate: Setup a Manipulator

<span class="badge badge-intermediate">Intermediate</span>

Build upon foundational knowledge to work with more complex robot structures. You will import a robot arm from URDF, connect a gripper, tune physics properties, generate configuration files, and implement pick and place tasks.

![Manipulator setup](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10e_pick_place_rmp.webp)

!!! example "[Tutorial 6: Setup a Manipulator](06_setup_manipulator.md)"
    Learn how to import the UR10e robot and Robotiq 2F-140 gripper from URDF and connect them as a single articulation.

!!! example "[Tutorial 7: Configure a Manipulator](07_configure_manipulator.md)"
    Learn how to adjust articulation solver settings, physics materials, joint effort limits, and drive gains.

!!! example "[Tutorial 8: Generate Robot Configuration File](08_generate_robot_config.md)"
    Learn how to generate configuration files for kinematics solvers using the Lula Robot Description Editor and USD to URDF Exporter.

!!! example "[Tutorial 9: Pick and Place Example](09_pick_and_place.md)"
    Implement pick and place tasks combining target following with Lula Kinematics Solver and motion control with RMPFlow.

## Advanced: Asset Tuning and Optimization

<span class="badge badge-advanced">Advanced</span>

Master advanced techniques for complex robot configurations. You will learn to rig closed-loop mechanisms, systematically tune joint drive gains, optimize asset performance, and rig legged robots for locomotion policies.

![Legged robot rigging](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_2.webp)

!!! example "[Tutorial 10: Rig Closed-Loop Structures](10_closed_loop_structures.md)"
    Learn how to configure closed-loop articulation structures, mimic joints, and OmniGraph control for a Robotiq gripper.

!!! example "[Tutorial 11: Tuning Joint Drive Gains](11_joint_tuning.md)"
    Learn how to optimize position and velocity drive gains using the Gain Tuner extension.

!!! example "[Tutorial 12: Asset Optimization](12_asset_optimization.md)"
    Learn performance optimization techniques for robot assets through mesh merging and scenegraph instancing.

!!! example "[Tutorial 13: Rig a Legged Robot](13_rig_legged_robot.md)"
    Learn how to rig and verify an H1 humanoid robot to match a locomotion policy's configuration specifications.
