---
title: Import MJCF
---

# Import MJCF

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import MJCF (MuJoCo XML) models into Isaac Sim and convert them to USD
- The interactive import procedure via the GUI
- The programmatic import procedure with the Python API (`MJCFImporter`)
- Batch conversion with the standalone script
- Guidelines for post-import articulation tuning and known issues

## Getting Started

### Prerequisites

- Complete the Quick Tutorials (basic operations) in Isaac Sim.

### Estimated Time

Approximately 5-10 minutes.

### Overview

In this tutorial, you will learn how to import MJCF model files into Isaac Sim and convert them to USD. Three methods are covered: interactive import from the GUI, import with the Python API from the Script Editor, and batch conversion with the standalone script from a terminal.

!!! note "What is MJCF"
    MJCF (MuJoCo XML Format) is the model description format used by the **MuJoCo** physics simulator. Like URDF, it describes a robot's bodies (rigid bodies) and joints in XML, but it is more expressive than URDF, supporting closed-loop structures and actuator/sensor definitions. Since a lot of model assets in reinforcement learning research are built for MuJoCo, importing MJCF directly lets you bring those assets straight into Isaac Sim.

!!! note "What changed in the MJCF importer in Isaac Sim 6.0"
    Like the URDF importer, the MJCF importer received a major update in 6.0. Imported assets now carry the Isaac Sim Robot Schema and schemas compatible with the Newton physics engine, and a **Robot Type / Base Type** selection was added to the import options. For Python, the `MJCFImporter` class replaces the Kit commands (`MJCFCreateImportConfig` / `MJCFCreateAsset`) as the standard method.

## Step 1: Import via the GUI

Here we import the Ant model (`nv_ant.xml`) that ships with the MJCF importer extension.

### 1-1. Check the Extension

The MJCF importer (`isaacsim.asset.importer.mjcf`) is normally loaded automatically when Isaac Sim starts and is available from the **File > Import** menu. If MJCF files are not listed in the import formats of the file selection dialog, open **Window > Extensions** and enable both the `isaacsim.asset.importer.mjcf` and `isaacsim.asset.importer.mjcf.ui` extensions.

### 1-2. Locate the Sample MJCF

`nv_ant.xml` ships with the MJCF importer extension itself. You can find it as follows:

1. Search for `isaacsim.asset.importer.mjcf` in **Window > Extensions**.
2. Click the folder icon next to **AUTOLOAD** to open the extension's installation folder.
3. Inside, `nv_ant.xml` is located at `/data/mjcf`.

### 1-3. Select the File and Import

1. Open the file selection dialog via **File > Import** and select `nv_ant.xml`.
2. Once you select the file, the **Options** pane appears on the right side of the dialog. Change the options as needed (the defaults are fine). The main items are **USD Output** (save location), **Robot Type** / **Base Type** (robot schema and base anchoring), **Import Scene** (whether to import the MJCF simulation settings as well), **Merge Mesh**, **Collision From Visuals** / **Collision Type**, and **Allow Self-Collision**. See Import Options in the official [MJCF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_mjcf.html) documentation for details on each option.

    ![MJCF import options](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.mjcf-3.0.0_user_interface.png)

3. Click the **Import** button. As with URDF, a **dialog confirming where the converted USD will be saved** appears. Click **Yes** and the robot is added to the stage.

!!! warning "The confirmation dialog can hide behind other windows"
    As with [Import URDF](01_import_urdf.md), this confirmation dialog can hide behind other windows and make the app look frozen. If you cannot interact with Isaac Sim after clicking Import, move the windows in front and answer the hidden dialog.

    ![Imported ant robot](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.mjcf-3.0.0_user_interface_ant.png)

## Step 2: Import with the Python API

You can do the same thing from Python. Isaac Sim 6.0 uses the `MJCFImporter` / `MJCFImporterConfig` classes.

1. Open the Script Editor via **Window > Script Editor**.
2. Copy the following code into the Script Editor:

```python
import isaacsim.core.experimental.utils.stage as stage_utils
import omni.usd
from isaacsim.asset.importer.mjcf import MJCFImporter, MJCFImporterConfig
from pxr import Gf, PhysicsSchemaTools, Sdf, UsdLux, UsdPhysics

# create new stage
omni.usd.get_context().new_stage()

# Get path to extension data:
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.importer.mjcf")
extension_path = ext_manager.get_extension_path(ext_id)

# setting up import configuration:
import_config = MJCFImporterConfig(mjcf_path=extension_path + "/data/mjcf/nv_ant.xml")

# import MJCF
importer = MJCFImporter(import_config)
output_usd_path = importer.import_mjcf()

# open the imported USD file into the current stage
result, stage = stage_utils.open_stage(output_usd_path)

# enable physics
scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))

# set gravity
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
scene.CreateGravityMagnitudeAttr().Set(9.81)

# add lighting
distantLight = UsdLux.DistantLight.Define(stage, Sdf.Path("/DistantLight"))
distantLight.CreateIntensityAttr(500)
```

3. Click **Run** (Ctrl + Enter) to import the ant robot.

### Key Points in the Code

| Class / method | Description |
|---|---|
| `MJCFImporterConfig` | Import configuration. Besides `mjcf_path` (input), you can specify `usd_path` (output), `fix_base` (`None` = Source / `True` = Fixed / `False` = Mobile), `merge_mesh`, `robot_type`, and more |
| `MJCFImporter` | The class that takes the configuration and runs the import |
| `importer.import_mjcf()` | Runs the conversion and returns the path of the generated USD file |
| `stage_utils.open_stage()` | Opens the generated USD as the current stage (`isaacsim.core.experimental.utils.stage`) |

!!! note "Migrating from the old API (MJCFCreateImportConfig / MJCFCreateAsset commands)"
    The Kit-command-based approach used in tutorials up to Isaac Sim 5.x — `omni.kit.commands.execute("MJCFCreateImportConfig")` and `MJCFCreateAsset` — has been superseded in 6.0 by the `MJCFImporter` class shown above. The gravity value `981.0` in the old sample (which assumed a centimeter stage unit) has also been corrected to `9.81` in meters in the current official sample.

!!! note "There is no ground, so the robot falls"
    This sample code sets up a physics scene and gravity but **does not create a ground plane**. If you play the simulation as-is, the robot keeps falling. To check the behavior, add a ground via **Create > Physics > Ground Plane** before playing.

## Step 3: Import with the Standalone Script

You can also batch-convert MJCF to USD from a terminal, without opening the Isaac Sim GUI. Run the following from the Isaac Sim installation root:

```bash
./python.sh standalone_examples/api/isaacsim.asset.importer.mjcf/mjcf_import.py --mjcf /path/to/nv_ant.xml --usd-path /path/to/output --merge-mesh
```

The main arguments are as follows (see the script's `--help` for the full list):

| Argument | Description |
|---|---|
| `--mjcf` | Path to an MJCF file (`.xml`) or a directory. Passing a directory converts all MJCF files inside |
| `--usd-path` | Directory to write the converted USD assets |
| `--robot-type` | Robot Type for the robot schema (Default / End Effector / Manipulator / Humanoid / Wheeled / Holonomic / Quadruped / Mobile Manipulators / Aerial; default: Default) |
| `--import-scene` | Import the MJCF simulation settings along with the model (default: True) |
| `--merge-mesh` | Merge meshes to optimize the model |
| `--collision-from-visuals` / `--collision-type` | Generate collision geometry from visuals, and the geometry type to use |
| `--allow-self-collision` | Allow self-collision for the imported asset |
| `--fix-base` / `--no-fix-base` | Tri-state base anchoring (omit to keep the MJCF authoring untouched) |
| `--link-density` | Default density (kg/m³) applied to links without explicit mass |
| `--override-gain-type` / `--override-bias-type` | Override the MuJoCo actuator gain / bias type (e.g. `"fixed"` / `"affine"`) |
| `--override-gain-prm` / `--override-bias-prm` | Override the MuJoCo actuator gain / bias parameter arrays (up to 10 floats) |
| `--test` | Converts the bundled `nv_ant.xml` into a temp directory as a smoke test |

## Post-Import Adjustments

The robot is ready for simulation as soon as it is imported into the stage. You can make further changes to the asset after import, such as adding sensors, changing materials, and updating joint drives and other settings for a more stable simulation.

In simulation, robots are treated as **articulations**. For articulation tuning, see the official Articulation Stability Guide as well as [Robot Setup Tutorial 11: Tuning Joint Drive Gains](../robot_setup/11_joint_tuning.md).

## Known Issue: Multi-DOF Joint Conversion

In USD, a joint is defined as a **kinematic constraint** between two rigid bodies; creating a joint limits the degrees of freedom (DOF) to the joint's axis (e.g. a revolute joint has one DOF).

In MuJoCo, on the other hand, a joint is defined as a **degree of freedom itself**, and multiple joints can be combined to express multiple DOFs (e.g. an X-axis revolute plus a Y-axis revolute for a 2-DOF joint). Expressing this directly in USD would define multiple joints between the same two bodies, forming a kinematic loop and becoming overconstrained.

For this reason, the MJCF importer **automatically converts multi-DOF joints between the same body pair into a single D6 joint in the PhysX variant**, while the physics and mujoco / newton variants keep the original per-DOF joints. Because of this difference, **mujoco and physx assets cannot be transferred directly between each other**.

If you want to retain every DOF and avoid this conversion, edit the MJCF to insert a **zero-mass dummy link** between the parent and child bodies and split the multi-DOF joint into one single-DOF joint per intermediate edge (e.g. two revolute joints between body A and body B become one revolute between A and the dummy link plus one revolute between the dummy link and B).

## Summary

This tutorial covered the following topics:

1. Importing an MJCF file via the **GUI** (ant robot example)
2. Importing with the **Python API** (`MJCFImporter` / `MJCFImporterConfig`) and setting up a physics scene
3. Batch conversion with the **standalone script** (`mjcf_import.py`)
4. Guidelines for **post-import articulation tuning** and the known issue with **multi-DOF joints**

### Further Learning

For details on the import options, refer to the official [MJCF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_mjcf.html) documentation. The Gain Tuner extension is also available for tuning joint gains.

## Next Steps

- [Tutorial 4: Importing General 3D Models](04_general_3d_model_importer.md) - Learn how to import general 3D models such as OBJ / FBX and set up physics properties.
