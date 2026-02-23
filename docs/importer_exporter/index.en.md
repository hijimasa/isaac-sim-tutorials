---
title: Import & Export Tutorials
---

# Import & Export Tutorials

## Overview

This tutorial series covers how to import and export assets in Isaac Sim. You will learn how to import URDF (the standard robot description format for ROS) and MJCF (MuJoCo physics simulation format), convert USD to URDF, and import models from external 3D model databases.

These skills are essential for integrating existing robot models into Isaac Sim's simulation environment and for using models created in Isaac Sim with other tools.

![URDF import](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_franka.png)

## Tutorials

!!! example "[Tutorial 1: Import URDF](01_import_urdf.md)"
    Learn how to import URDF files into Isaac Sim. Three methods are covered: direct GUI import, programmatic Python scripting, and import from ROS 2 nodes.

!!! example "[Tutorial 2: Export URDF](02_export_urdf.md)"
    Learn how to use the USD to URDF Exporter to convert USD robot files to URDF format. Covers collision object mapping and exporter limitations.

!!! example "[Tutorial 3: Import MJCF](03_import_mjcf.md)"
    Learn how to import MJCF (MuJoCo XML) model files into Isaac Sim and convert them to USD format. Both GUI and Python scripting methods are covered.

!!! example "[Tutorial 4: ShapeNet Importer](04_shapenet_importer.md)"
    An introduction to importing 3D models from the ShapeNet database. The dedicated extension is deprecated, so the standard OBJ import procedure is used.
