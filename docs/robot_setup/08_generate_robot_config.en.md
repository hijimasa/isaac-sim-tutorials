---
title: Generate Robot Configuration File
---

# Generate Robot Configuration File

## Learning Objectives

After completing this tutorial, you will have learned:

- How to generate URDF files using the USD to URDF Exporter
- How to generate robot description files using the Lula Robot Description Editor
- How to generate and edit collision spheres
- How to export XRDF files

## Getting Started

### Prerequisites

- Complete [Tutorial 7: Configure a Manipulator](07_configure_manipulator.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will generate robot configuration files for the UR10e robot and 2F-140 gripper using the Lula Robot Description Editor and USD to URDF Exporter. These files provide essential data for kinematics solvers.

## Generating the Robot URDF

1. Enable the Isaac Sim USD to URDF Exporter Extension.

2. Export the URDF file.

    ![URDF export](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_export_urdf.png)

## Generating Lula Robot Description Files and Collision Spheres

1. Enable the Isaac Sim Lula Extension.

2. Prepare the robot asset for Lula.

3. Configure joints in the Lula Robot Description Editor.

    ![Lula Robot Description Editor](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_lula_robot_description_editor.png)

4. Generate collision spheres.

    ![Collision spheres](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_lula_link_sphere_editor_add_spheres.png)

5. Export the Lula robot description file.

    ![Export](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_lula_export_robot_description_file.png)

## Summary

This tutorial covered the following topics:

1. Generating URDF files with the **USD to URDF Exporter**
2. Generating robot description files with the **Lula Robot Description Editor**
3. Generating and editing **collision spheres**
4. **Exporting** configuration files

## Next Steps

Proceed to the next tutorial, "[Pick and Place Example](09_pick_and_place.md)", to learn how to perform manipulation tasks using kinematics solvers and RMPFlow.
