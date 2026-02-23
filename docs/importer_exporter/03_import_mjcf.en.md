---
title: Import MJCF
---

# Import MJCF

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import MJCF (MuJoCo) model files into Isaac Sim
- How to import using both GUI and Python scripting
- How to configure articulations after import

## Getting Started

### Prerequisites

- Complete the Quick Tutorials in Isaac Sim.

### Estimated Time

Approximately 5-10 minutes.

### Overview

In this tutorial, you will learn how to import MJCF (MuJoCo XML) model files into Isaac Sim and convert them to USD format. Two methods are covered: interactive GUI import and programmatic Python scripting.

## GUI Import

1. Enable the MJCF Importer extension from **Window > Extensions**.

    ![MJCF import dialog](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ext-isaacsim.asset.importer.mjcf-2.3.0_gui_0.png)

2. Open the file selection dialog via **File > Import**.

3. Navigate to the extension assets folder (`/data/mjcf`) and select a file such as `nv_humanoid.xml`.

4. Configure import settings and click Import.

    ![Imported humanoid](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ext-isaacsim.asset.importer.mjcf-2.3.0_gui_humanoid.png)

## Python Scripting Import

You can also import programmatically using the Script Editor (**Window > Script Editor**):

1. Create import configuration with `MJCFCreateImportConfig` command
2. Set options such as `fix_base()` and `make_default_prim()`
3. Create the asset with `MJCFCreateAsset` command
4. Initialize the physics scene (gravity settings)
5. Add lighting

### Key Configuration Options

| Option | Description |
|--------|-------------|
| `fix_base` | Whether to fix the robot base |
| `make_default_prim` | Whether to set as default prim |

## Post-Import Configuration

- Imported robots are converted to articulations within the simulation
- Sensors, materials, and joint configurations can be modified after import
- Articulation stability can be tuned by referring to the stability guide

## Summary

This tutorial covered the following topics:

1. **GUI** import of MJCF files
2. **Python scripting** for programmatic import
3. Post-import **articulation configuration**

## Next Steps

- [Tutorial 4: ShapeNet Importer](04_shapenet_importer.md) - Learn how to import 3D models from the ShapeNet database.
