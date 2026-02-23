---
title: Export URDF
---

# Export URDF

## Learning Objectives

After completing this tutorial, you will have learned:

- How to export USD files to URDF format
- How to configure export options (mesh path, root prim path)
- How collision objects and visibility map to URDF
- The limitations of the exporter
- How to verify export results

## Getting Started

### Prerequisites

- Complete the Quick Tutorials in Isaac Sim.

### Estimated Time

Approximately 10-20 minutes.

### Overview

In this tutorial, you will learn how to use the USD to URDF Exporter in Isaac Sim to convert USD robot files to URDF format. You will also learn about collision object handling and exporter limitations.

## Enabling the Exporter

1. Navigate to **Windows > Extensions**, search for "urdf", and enable the USD to URDF Exporter.

2. This adds a **File > Export to URDF** menu option.

3. Load the Franka robot (`/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd`) and export it.

    ![URDF export](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_ext-usd_to_urdf_exporter-1.3.3_gui_urdf_export.png)

4. Verify that both a `.urdf` file and a `meshes` directory are generated.

## Export Options

### Mesh Folder Name

Specifies the directory name for `.obj` files (default: "meshes").

### Mesh Path Prefix

| Prefix | Description |
|--------|-------------|
| `file://` | Absolute paths |
| `package://` | Package paths (ROS-compatible) |
| `./` | Relative paths |

### Root Prim Path

When a scene contains multiple robots, you can specify the prim for the target robot to export.

## Collision Object Handling

USD geometry prims map to URDF visual and collision meshes:

- Prims with `PhysicsCollisionAPI` → collision meshes
- Visible prims → visual meshes

![USD model with sphere](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/franka_usd_sphere_mesh_no_collision_visible.png)

You can observe how the URDF output changes by applying collision APIs and toggling visibility.

![URDF viewer](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/urdf_viewer_franka.png)

## Limitations

The exporter has the following constraints:

- Kinematic structures must form tree hierarchies
- Joint types are limited to `prismatic`, `revolute`, and `fixed`
- Link types are limited to `Xform`
- Sensors must be cameras or IMU sensors
- Geometry must be cubes, spheres, cylinders, or meshes
- Geometry prims must be leaf nodes

## Verifying Export Results

You can verify exports by:

1. Re-importing the exported URDF into Isaac Sim
2. Using an online URDF Viewer to visualize joint structures and collision geometry

## Summary

This tutorial covered the following topics:

1. Enabling and using the **USD to URDF Exporter**
2. Configuring **export options** (mesh path, root prim path)
3. Mapping **collision objects** and visibility to URDF
4. Understanding exporter **limitations**
5. **Verifying** export results

## Next Steps

- [Tutorial 3: Import MJCF](03_import_mjcf.md) - Learn how to import MuJoCo format files.
