---
title: Importing General 3D Models
---

# Importing General 3D Models

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import general 3D model files (OBJ / FBX, etc.) into Isaac Sim and convert them to USD
- How units, scale, and up-axis are handled during import
- How to add physics properties (Rigid Body / Collider) to imported models for simulation

## Getting Started

### Prerequisites

- Familiarity with basic Isaac Sim operations
- Experience with **File > Import** (e.g. from [Tutorial 1: Import URDF](01_import_urdf.md))

### Estimated Time

Approximately 5-10 minutes.

### Overview

Besides robot description formats (URDF / MJCF), Isaac Sim can import common 3D model formats such as OBJ, FBX, and glTF. This is the most general import path for placing obstacles, furniture, and props in a scene.

!!! note "About ShapeNet and other 3D model datasets"
    The dedicated ShapeNet importer extension (`omni.isaac.shapenet`) has been **deprecated and removed**. Models from ShapeNet and other datasets can be imported with the standard file import procedure described on this page.

## Step 1: Prepare a Model File

Prepare the 3D model file you want to import (`.obj`, `.fbx`, ...). For OBJ, keep the `.obj`, `.mtl`, and texture files together in the same folder.

## Step 2: Import via File > Import

1. Open **File > Import** and select the model file.
2. The **Options** pane on the right shows the **Asset Importer** conversion options:

    ![OBJ import options](images/04_obj_import_options.png)

    | Key option | Description |
    |---|---|
    | **Import Materials** | Import materials (.mtl / textures) |
    | **Use Meter as World Unit** | Treat model units as meters |
    | **Create '/World' Default Prim** | Create `/World` as the default prim |
    | **Up-axis** | Up axis of the model (defaults to the file setting) |
    | **Destination (Path)** | Output location of the converted USD; same folder as the model if empty |

3. Click **Import**. The model is converted to USD and added to the stage.

!!! note "How the import works"
    A converted USD file is generated next to the original model (or at the Destination path), and a prim referencing it (as a payload) is added to the current stage. The original model file is not modified.

!!! tip "Watch out for units and scale"
    If the stage and model units differ, a "Mismatched units found ..." notification appears and `unitsResolve` corrections (scale/rotation) are added to the prim automatically. Dataset models are often normalized to a size around 1 unit; adjust **Transform > Scale** in the Property panel to match the real-world size.

## Step 3: Add Physics Properties

A freshly imported model is visual-only. To use it in simulation:

1. Select the model prim and apply **+Add > Physics > Rigid Body with Colliders Preset** in the Property panel (the model becomes a dynamic rigid body).
2. For a static obstacle, apply **Physics > Colliders Preset** only.
3. Confirm that **Rigid Body** / **Collider** sections appear in the Property panel. Set mass and physics materials (friction, etc.) as needed.

## Step 4: Verify in Simulation

1. Add a ground with **Create > Physics > Ground Plane** if the scene has none.
2. Press **PLAY** and confirm the model lands and rests on the ground.

See [Core API Tutorial 7: Adding Props](../core_api/07_adding_props.md) for details on physics properties.

## Summary

This tutorial covered:

1. Importing general 3D models via **File > Import** and the Asset Importer options
2. Automatic **unit/scale** resolution and real-size adjustment
3. Adding physics with **Rigid Body with Colliders Preset / Colliders Preset**
4. Verifying with a **Ground Plane** in simulation

This completes the Importer/Exporter tutorial series.

## Next Steps

- Return to the [Importer/Exporter tutorial index](index.md)
- Learn robot rigging and tuning in the [Robot Setup tutorials](../robot_setup/index.md)
