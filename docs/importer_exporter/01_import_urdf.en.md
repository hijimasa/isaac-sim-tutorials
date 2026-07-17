---
title: Import URDF
---

# Import URDF

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import URDF files into Isaac Sim and convert them to USD
- How to configure import settings (Robot Type / Base Type, mesh merging, colliders)
- How to visualize and inspect collision meshes
- The import workflow using the built-in samples (Robotics Examples)
- How to import URDF programmatically with the Python API (`URDFImporter`)
- How to batch-convert URDF files with the standalone script

## Getting Started

### Prerequisites

- Complete the Quick Tutorials (basic operations) in Isaac Sim.

### Estimated Time

Approximately 10-15 minutes.

### Overview

In this tutorial, you will learn how to import URDF files into Isaac Sim and convert them to USD. Four methods are covered in order:

1. **Direct import via the GUI** — the basic, menu-only way to load a URDF
2. **Import from built-in samples** — experience the workflow with the Robotics Examples
3. **Import with the Python API** — a programmatic method using the `URDFImporter` class from the Script Editor
4. **Import with the standalone script** — batch conversion from a terminal

Importing URDF (XACRO) directly from a ROS 2 node requires a ROS 2 installation, so it is covered separately in [Tutorial 1a: Import URDF from a ROS 2 Node](01a_import_urdf_from_ros2.md).

!!! note "What is URDF / why conversion is needed"
    URDF (Unified Robot Description Format) is the standard robot description format used in ROS. It describes a robot's links (rigid bodies), joints, masses, and collision shapes in XML.

    Isaac Sim, on the other hand, handles scenes and robots in **USD (Universal Scene Description)**. To use a URDF robot in Isaac Sim, a one-way **conversion (import)** from URDF to USD is required. The original URDF file is never modified.

    The reverse conversion (USD → URDF) is covered in [Tutorial 2](02_export_urdf.md).

!!! note "What changed in the URDF importer in Isaac Sim 6.0"
    The URDF importer received a major update in Isaac Sim 6.0. Imported assets now carry the [Isaac Sim Robot Schema](https://docs.isaacsim.omniverse.nvidia.com/latest/omniverse_usd/robot_schema.html) and schemas compatible with the Newton physics engine. The import options were also reorganized: a **Robot Type / Base Type** selection was added, while the joint drive settings at import time (such as Natural Frequency) that existed in older versions were removed — gain tuning is now done after import.

## Step 1: Direct Import via the GUI

Here we import the UR10 URDF (`ur10.urdf`) that ships with the URDF importer extension.

### 1-1. Enable the Extension

The URDF importer (`isaacsim.asset.importer.urdf`) is normally loaded automatically when Isaac Sim starts. If it is not loaded, open **Window > Extensions**, search for `isaacsim.asset.importer.urdf`, and enable it.

### 1-2. Locate the Sample URDF

`ur10.urdf` ships with the URDF importer extension itself. You can find it as follows:

1. Search for `isaacsim.asset.importer.urdf` in **Window > Extensions**.
2. Click the folder icon next to **AUTOLOAD** to open the extension's installation folder.
3. Inside, `ur10.urdf` is located at `/data/urdf/robots/ur10/urdf`. Copy this path.

### 1-3. Select the File

Open **File > Import**, paste the path you copied into the navigation bar of the file selection dialog, and select `ur10.urdf`.

![Select robot](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_0.png)

### 1-4. Configure the Import Settings

Once you select a URDF file, the **Options** pane (import settings) appears on the right side of the file selection dialog. For the UR10, configure it as follows:

| Setting | Value for this tutorial | Description |
|---|---|---|
| **USD Output** | Leave at default | Where the converted USD file is saved. By default it is the same directory as the URDF; click the folder icon to change it |
| **Robot Type** | Leave at default (`Default`) | Sets the `isaac:robotType` attribute of the robot schema. Choose from Default / End Effector / Manipulator / Humanoid / Wheeled / Holonomic / Quadruped / Mobile Manipulators / Aerial |
| **Base Type** | Leave at default (`Source`) | How the root link is anchored. Three choices: **Source** (follow the URDF authoring, default) / **Fixed** (add a world-to-root fixed joint = fixed base) / **Mobile** (remove any fixed joint = floating base) |
| **Merge Mesh** | On | Merges the meshes under each rigid body into a single mesh, reducing the number of prims in the USD and improving performance |
| **Allow Self-Collision** | On | Whether collisions between the robot's own links are enabled |

All other settings (Collision From Visuals, Collision Type, ROS Package List, Debug Mode, etc.) can be left at their defaults. See the official [URDF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_urdf.html) documentation for details on each option.

![Import options](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_1.png)

!!! warning "Write access to the output directory"
    The output directory used at import time **must be writable**. Since the default output location is the same directory as the URDF file, change **USD Output** to a writable location when importing a URDF that lives in a read-only place, such as the extension's bundled samples.

!!! note "Joint drives are now configured after import"
    Up to Isaac Sim 5.x, the URDF importer had a **Joints & Drives** section for configuring joint drives (Stiffness / Natural Frequency) at import time; this was **removed in 6.0**. In 6.0 the joint drives are configured automatically from the URDF, and gains are tuned after import via the Property panel or the **Gain Tuner** extension.

    Joint drives in Isaac Sim are driven by PD control (Stiffness / Damping). Larger values make the joint track its target more quickly and suppress oscillation during motion. However, setting the values too high can cause the simulation to become **numerically unstable**, causing joints or rigid bodies to jitter or fly off unexpectedly. If this occurs, try reducing the simulation timestep in the Physics Scene settings or lowering the values. See [Robot Setup Tutorial 11: Tuning Joint Drive Gains](../robot_setup/11_joint_tuning.md) for details.

### 1-5. Run the Import

Click the **Import** button. A **URDF Confirm Path** dialog appears where you can confirm where the converted USD file will be saved. Click **Yes** to run the import and add the robot to the stage.

![URDF Confirm Path dialog](images/01_urdf_confirm_path.png)

If you have imported to the same location before, a **URDF Confirm Overwrite** dialog appears next. Click **Yes** if overwriting is fine.

![URDF Confirm Overwrite dialog](images/01_urdf_confirm_overwrite.png)

!!! warning "The confirmation dialog can hide behind other windows"
    Depending on your environment, this confirmation dialog can appear **hidden behind the file selection window or the Extensions window**. While it is open, the entire main window stops responding to clicks, which can look like a freeze. If you cannot interact with Isaac Sim after clicking Import, drag away (or close) the windows in front and answer **Yes / No** in the hidden dialog.

![Import result](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_2.png)

!!! note "Importing a mobile (wheeled) robot"
    For robots that move on wheels, check and adjust the following:

    - Set **Base Type** to **Mobile** (or **Source** if the base is not fixed in the URDF)
    - After import, set the drive of velocity-controlled joints (wheels) to **Velocity** and position-controlled joints (steering) to **Position**
    - Adjust the drive strength through the joint's **Damping** (in velocity drive mode, Stiffness is always set to zero)

!!! note "Importing a torque-controlled robot (such as a quadruped)"
    For robots whose legs are driven directly by torque:

    - Set **Base Type** to **Mobile** (or **Source**)
    - After import, set the drive type of torque-controlled joints (legs) to **None**, and other joints to **Position** or **Velocity**
    - For **None** drives, Stiffness / Damping have no effect, so set them to zero

## Step 2: Visualize the Collision Meshes

Not all rigid bodies necessarily have collision properties, and collision meshes are usually simplified compared to the visual meshes. It is a good idea to visually confirm after import that collisions are set up as intended.

To visualize collision meshes in the viewport:

1. Click the **eye icon** in the upper left of the viewport.
2. Hover over **Show By Type**.
3. Hover over **Physics**.
4. Hover over **Colliders**.
5. Select **All** (the three choices are None / Selected / All).

Collision meshes are overlaid as wireframes (pink to green lines).

!!! note "If the wireframes do not appear"
    Depending on your environment and assets, the wireframes may not appear immediately after selecting **All**. In that case, try moving the viewport camera, zooming in on the prim, or playing the simulation once to refresh the display.

![Collision meshes](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_3.png)

## Step 3: Import from the Built-in Samples

!!! warning "Site note: this section is based on Isaac Sim 5.1.0"
    This "built-in samples" section was removed from the official Isaac Sim 6.0 tutorial. It is this site's own walkthrough based on the content and verification as of 5.1.0. The structure and labels of the examples may differ depending on your version.

Isaac Sim ships with samples that walk you through the whole workflow, from import to drive configuration and simulation.

Enable **Window > Examples > Robotics Examples** and a **Robotics Examples** tab appears in the bottom dock. The **IMPORT ROBOTS** section in the sidebar offers four examples:

- Carter URDF (mobile robot; the official documentation calls it Nova Carter URDF, but the actual UI label is Carter URDF)
- Franka URDF (manipulator)
- Kaya URDF (mobile robot)
- UR10 URDF (manipulator)

!!! note "Wait for materials to load"
    Materials in these samples can take a while to load. Check the progress indicator at the bottom right of the UI.

![Robotics Examples](./images/01_robotics_examples_window.png)

The import settings and post-import setup differ per sample, but the usage is common to all:

1. In the **Robotics Examples** tab, click **IMPORT ROBOTS > (robot name) URDF** to open the example panel on the right.
2. The **LOAD** button in the **Load Robot** row of the **Command Panel** — imports the URDF into the stage and adds a ground plane, a light, and a physics scene.
3. The **CONFIGURE** button in the **Configure Drives** row — sets the stiffness and damping of each joint drive.
4. The **pencil icon (Open Source Code)** at the top right of the panel — shows the source code that implements this whole flow with the Python API.
5. The **PLAY** button in the left toolbar — starts the simulation.
6. The **MOVE** button in the **Move to Pose** row — moves the robot to its home (rest) pose.

## Step 4: Import with the Python API

Everything you did in the Import window can also be done from Python. Isaac Sim 6.0 introduces a new API based on the `URDFImporter` / `URDFImporterConfig` classes.

1. Open the Script Editor via **Window > Script Editor**.
2. Copy the following code into the Script Editor:

```python
import os

import isaacsim.core.experimental.utils.stage as stage_utils
import omni
from isaacsim.asset.importer.urdf import URDFImporter, URDFImporterConfig

# Get the extension's installation path
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.importer.urdf")
extension_path = ext_manager.get_extension_path(ext_id)

# Import the URDF
importer = URDFImporter(
    URDFImporterConfig(
        urdf_path=os.path.normpath(os.path.join(extension_path, "data", "urdf", "robots", "ur10", "urdf", "ur10.urdf")),
        usd_path=os.path.normpath(os.path.join(extension_path, "data", "urdf", "robots", "ur10", "urdf", "ur10.usd")),
        merge_mesh=True,             # merge meshes (equivalent to Merge Mesh in the GUI)
        allow_self_collision=True,   # allow self-collision (equivalent to Allow Self-Collision in the GUI)
    )
)
output_path = importer.import_urdf()

# Open the converted USD
print(output_path)
result, stage = stage_utils.open_stage(output_path)
```

3. Click **Run** (Ctrl + Enter) and the UR10 is converted and loaded into the stage.

### Key Points in the Code

| Class / method | Description |
|---|---|
| `URDFImporterConfig` | Import configuration. Besides `urdf_path` (input) and `usd_path` (output), you can specify `merge_mesh`, `allow_self_collision`, `fix_base` (`None` = Source / `True` = Fixed / `False` = Mobile), `robot_type`, and more |
| `URDFImporter` | The class that takes the configuration and runs the import |
| `importer.import_urdf()` | Runs the conversion and returns the path of the generated USD file |
| `stage_utils.open_stage()` | Opens the generated USD as the current stage (`isaacsim.core.experimental.utils.stage`) |

!!! warning "Use a writable output location for the sample"
    The code above writes `ur10.usd` into the extension's bundled folder. Depending on your installation, this folder may be read-only; in that case, change `usd_path` to a writable location such as your own working directory.

!!! note "Migrating from the old API (URDFParseFile / URDFImportRobot commands)"
    The Kit-command-based approach used in tutorials up to Isaac Sim 5.x — `omni.kit.commands.execute("URDFParseFile", ...)`, `URDFImportRobot`, and `URDFParseAndImportFile` — has been superseded in 6.0 by the `URDFImporter` class shown above.

## Step 5: Import with the Standalone Script

You can also batch-convert URDF to USD from a terminal, without opening the Isaac Sim GUI. Run the following from the Isaac Sim installation root:

```bash
./python.sh standalone_examples/api/isaacsim.asset.importer.urdf/urdf_import.py --urdf /path/to/ur10.urdf --usd-path /path/to/output --merge-mesh
```

The main arguments are as follows (see the script's `--help` for the full list):

| Argument | Description |
|---|---|
| `--urdf` | Path to a URDF file (`.urdf`) or a directory. Passing a directory converts all URDF files inside |
| `--usd-path` | Directory to write the converted USD assets |
| `--robot-type` | Robot Type for the robot schema (Default / End Effector / Manipulator / Humanoid / Wheeled / Holonomic / Quadruped / Mobile Manipulators / Aerial; default: Default) |
| `--merge-mesh` | Merge meshes to optimize the model |
| `--merge-fixed-joints` | Merge fixed joints where possible to optimize the model |
| `--collision-from-visuals` | Generate collision geometry from the visual meshes |
| `--collision-type` | Collision geometry type (`"Convex Hull"`, `"Convex Decomposition"`, `"Bounding Sphere"`, `"Bounding Cube"`) |
| `--allow-self-collision` | Allow self-collision for the imported asset |
| `--fix-base` / `--no-fix-base` | Tri-state base anchoring. `--fix-base` adds a world-to-root fixed joint, `--no-fix-base` strips any existing one, and omitting the flag keeps the URDF authoring untouched (corresponds to Base Type in the GUI) |
| `--link-density` | Default density (kg/m³) applied to links without explicit mass |
| `--joint-drive-type` / `--joint-target-type` | Drive type (force / acceleration) and target type (none / position / velocity) applied to all joints |
| `--override-joint-stiffness` / `--override-joint-damping` | Stiffness / Damping override values applied to all joints |
| `--ros-package` | `name:path` mapping to resolve `package://` URLs (can be specified multiple times) |
| `--test` | Converts the bundled `carter.urdf` into a temp directory as a smoke test |

## Post-Import Adjustments

The robot is ready for simulation as soon as it is imported into the stage, but you can make further changes to the asset, such as:

- Adding sensors (cameras, IMU, LiDAR, etc.)
- Changing materials
- Updating joint drives and other settings to stabilize the simulation

In simulation, robots are treated as **articulations**. For articulation tuning, see the official Articulation Stability Guide as well as [Robot Setup Tutorial 11: Tuning Joint Drive Gains](../robot_setup/11_joint_tuning.md).

## Summary

This tutorial covered the following topics:

1. **Direct URDF import** via the GUI and the meaning of the settings (Robot Type / Base Type / Merge Mesh, etc.)
2. Visualizing and inspecting **collision meshes**
3. The import workflow with the **built-in samples** (Robotics Examples)
4. Importing with the **Python API** (`URDFImporter` / `URDFImporterConfig`)
5. Batch conversion with the **standalone script** (`urdf_import.py`)

### Further Learning

For the full list of import settings, refer to the official [URDF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_urdf.html) documentation.

## Next Steps

- [Tutorial 1a: Import URDF from a ROS 2 Node](01a_import_urdf_from_ros2.md) - Learn how to import URDF (XACRO) directly from a ROS 2 `robot_state_publisher`.
- [Tutorial 2: Export URDF](02_export_urdf.md) - Learn the reverse conversion, from USD to URDF.
