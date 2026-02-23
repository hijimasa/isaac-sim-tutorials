---
title: Import URDF
---

# Import URDF

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import URDF files into Isaac Sim
- How to configure import settings (base type, density, collision properties)
- How to visualize and inspect collision meshes
- How to import URDF programmatically using Python scripts
- How to import URDF from ROS 2 nodes

## Getting Started

### Prerequisites

- Complete the Quick Tutorials in Isaac Sim.
- Familiarity with the URDF Importer Extension basics.

### Estimated Time

Approximately 10-15 minutes.

### Overview

In this tutorial, you will learn how to import URDF (Unified Robot Description Format) files into Isaac Sim and convert them to USD format. Three methods are covered: direct GUI import, Python scripting, and ROS 2 node import.

## Direct Import via GUI

1. Enable the `isaacsim.asset.importer.urdf` extension.

    ![Enable extension](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_import_urdf_enable_extension.png)

2. Navigate to **File > Import** and select a URDF file.

    ![Select robot](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_import_urdf_select_robot.png)

3. Configure import settings (output location, base type, density, collision properties) and click Import.

    ![Import result](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_franka.png)

### Key Settings

| Setting | Description |
|---------|-------------|
| Static Base / Moveable Base | Whether the robot base is fixed or mobile |
| Natural Frequency | Natural frequency for joint stability |
| Self-Collision | Enable/disable self-collision detection |

## Visualizing Collision Meshes

To view collision meshes, click the eye icon in the viewport → **Show by type > Physics > Colliders > All**.

![Collision meshes](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_visualize_franka_colliders.png)

## UI Integration Examples

The Robotics Examples tab provides pre-configured examples:

- Nova Carter URDF
- Franka URDF
- Kaya URDF
- UR10 URDF

![UI integration examples](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.asset.importer.urdf-2.3.0_gui_example_import_franka.png)

## Python Scripting Import

You can import URDF programmatically using `_urdf.acquire_urdf_interface()` and `ImportConfig()`.

![Python import](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_sim_import_urdf.gif)

### Mobile Robot Configuration

- Use Moveable Base setting
- Set velocity drive for wheels, position drive for steering
- Adjust Joint Drive Strength for damping

### Torque-Controlled Robots (Quadrupeds)

- Enable Moveable Base
- Set joint drive type to "None" for torque control
- Configure stiffness/damping parameters

## ROS 2 Node Import

On Linux environments, you can import URDF directly from ROS 2 nodes:

1. Terminal 1: Launch Transform Publisher
2. Terminal 2: Identify node name
3. Isaac Sim → **File > Import from ROS 2 URDF Node**

## Summary

This tutorial covered the following topics:

1. **Direct URDF import** via GUI
2. Configuring **import settings** (base type, collision, drives)
3. **Collision mesh** visualization
4. **Python scripting** for programmatic import
5. Import from **ROS 2 nodes**

## Next Steps

- [Tutorial 2: Export URDF](02_export_urdf.md) - Learn how to convert USD to URDF format.
