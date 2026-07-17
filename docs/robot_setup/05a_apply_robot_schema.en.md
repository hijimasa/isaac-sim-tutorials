---
title: Applying the Robot Schema
---

# Applying the Robot Schema

## Learning Objectives

After completing this tutorial, you will have learned:

- What the **Robot Schema** is and why it is needed
- The roles of the main APIs (**RobotAPI / LinkAPI / JointAPI / SiteAPI**, among others)
- How to apply the Robot Schema to a manually rigged robot (both via GUI and Python)
- The best practice of isolating schema application into a dedicated layer for non-destructive editing
- How to verify that the robot is recognized by Asset Editor tools such as the Gain Tuner

## Getting Started

### Prerequisites

- Complete [Tutorial 5: Rig a Mobile Robot](05_rig_mobile_robot.md) before starting this tutorial.
- Have a rigged USD asset ready (e.g., `SMV_Forklift_B01_01`).

### Estimated Time

Approximately 20 minutes.

### Overview

In [Tutorial 5](05_rig_mobile_robot.md), you applied an **Articulation Root** to the forklift so that it could be driven as an articulation. While that is enough for the physics simulation itself to work, the higher-level tools in Isaac Sim — such as the **Gain Tuner** ([Tutorial 11](11_joint_tuning.md)), **Grasp Editor**, **Robot Description Editor (XRDF Editor)**, **Robot Wizard**, and the **Robot Inspector** and **Robot Poser** added in Isaac Sim 6.0 — require an additional schema, the **Robot Schema**, to be applied so that the asset is recognized as a "robot."

In this tutorial, you will learn how to apply the Robot Schema to a manually rigged robot so that it integrates with the rest of the tooling. The flow is:

1. **Understand what the Robot Schema is**
2. **Set up a dedicated layer** for non-destructive schema application
3. **Apply the schema in bulk via Python** (the officially recommended approach)
4. **Apply the schema via GUI** for individual prims or fine-tuning
5. **Verify the result** in the Properties panel and the Gain Tuner

!!! note "Not needed for robots imported via URDF / MJCF"
    When you load a robot through the [URDF Importer](06_setup_manipulator.md) or the MJCF Importer, those importers **automatically apply the Robot Schema**. The UR10e in [Tutorials 6 / 7](06_setup_manipulator.md) is one such example. This tutorial is for cases where you have **manually rigged a robot without going through URDF** — for instance, the deliverable from Tutorial 5.

## Step 1: What the Robot Schema Is

The **Robot Schema** is an extension schema defined by NVIDIA to describe robots, complementing the OpenUSD [Physics Schema](https://openusd.org/release/api/physics_8h_source.html). While the Physics Schema defines the **physical framework** ("rigid bodies, joints, articulations"), the Robot Schema adds **semantic meaning** ("which prim is the robot's core, and which are its links / joints / sites").

### 1-1. Why the Physics Schema Alone Is Not Enough

The Physics Schema is an open USD standard and is broadly applicable, but it has **no mechanism for declaring "this is a robot."** For example:

- Enumerate an articulation as a single robot
- Convey a namespace (such as `/robot1`, `/robot2`) to ROS or OmniGraph
- Describe robot-specific metadata such as DOF reporting order
- Define attachment points for grippers and sites (reference points) for tools

These fall outside the scope of the Physics Schema. The **Robot Schema fills this gap** and provides a common foundation for the various Asset Editor tools to consistently understand robot structure.

### 1-2. The Four Main APIs

The Robot Schema consists of five applied API schemas (IsaacRobotAPI / IsaacLinkAPI / IsaacJointAPI / IsaacSiteAPI / IsaacAttachmentPointAPI) and two typed schemas (IsaacNamedPose / IsaacSurfaceGripper). This tutorial focuses on the four most important ones:

| API Schema | Applied To | Role | Key Attributes / Relationships |
|---|---|---|---|
| **IsaacRobotAPI** | The robot's root prim | Declares "this is the robot." Tools use it as the entry point to recognize a robot | `isaac:description`, `isaac:namespace`, `isaac:robotType`, `isaac:license`, `isaac:source`, `isaac:version`, `isaac:changelog`, `robotLinks` (relationship), `robotJoints` (relationship), `namedPoses` (relationship) |
| **IsaacLinkAPI** | Each link (rigid body) prim | Marks the prim as a robot link, enables name overriding | `nameOverride` |
| **IsaacJointAPI** | Each joint prim | Marks the prim as a robot joint, carries DOF ordering information | `nameOverride`, `isaac:physics:DofOffsetOpOrder` (Token array) |
| **IsaacSiteAPI** | Reference prims such as end-effectors or tool mount points | Represents "meaningful points (sites) on the robot" such as tool mounts, sensor locations, and end-effector frames | `isaac:Description`, `isaac:forwardAxis` |

In addition, the schema defines `IsaacAttachmentPointAPI` (for gripper attachment points), the `IsaacSurfaceGripper` prim type (for surface grippers as a whole), and the `IsaacNamedPose` prim type (stores named joint configurations, used by the Robot Poser). Apply these as needed.

!!! note "Schema changes in Isaac Sim 6.0"
    - **`IsaacSiteAPI` is the successor of the old `IsaacReferencePointAPI`.** Robots still carrying the old schema will function but emit deprecation warnings.
    - The DOF offsets in IsaacJointAPI changed from the old per-axis attributes (`isaac:physics:Tr_X:DoFOffset`, etc.) to the **`isaac:physics:DofOffsetOpOrder` Token array**. Single-DOF joints (Revolute / Prismatic) and fixed joints do not require this attribute.
    - To migrate existing assets, use **`UpdateDeprecatedSchemas(robot_prim)`** from `usd.schema.isaac.robot_schema.utils` (migrates ReferencePoint → Site and the old DOF offset attributes in one pass).

### 1-3. How Tools Use the Robot Schema

As a concrete example, look at how the Gain Tuner works. It traverses the entire stage and lists **only prims with `IsaacRobotAPI` applied** in its dropdown menu (per the implementation of the `isaacsim.robot_setup.gain_tuner` extension). If the Robot Schema is not applied, the robot will be invisible to the Gain Tuner even when the Articulation Root is enabled.

By the same mechanism, the Grasp Editor consults `IsaacAttachmentPointAPI`, the Robot Description Editor (XRDF Editor) consults the DOF ordering information in `IsaacJointAPI`, and the Isaac Sim 6.0 **Robot Inspector** (`isaacsim.robot.schema.ui`) and **Robot Poser** consult the link/joint lists of `IsaacRobotAPI` and `IsaacNamedPose`, respectively.

## Step 2: Preparing the Layer Structure

Isaac Sim's [Asset Structure Guideline](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/asset_structure.html) recommends **storing the Robot Schema application in a dedicated layer**. The benefits are:

- You can add the Robot Schema without modifying the base asset (mesh and rigging)
- You can adapt to future schema updates without regenerating the base
- You can revert to the original by simply detaching the layer

### 2-1. Layer Layout

USD has a built-in mechanism for stacking files as **layers**, allowing you to override or add properties from a separate file without touching the base asset. The Robot Schema is best applied through this mechanism into a dedicated layer:

| File | Role |
|---|---|
| `<robot>.usd` | The rigged base asset (the deliverable from Tutorial 5) |
| `configuration/<robot>_robot_schema.usda` | The layer that contains **only the Robot Schema application** (created in this tutorial) |

Placing the file under a `configuration/` subdirectory with a `*_robot_schema.usda` suffix is the naming convention recommended by Isaac Sim.

!!! note "How USD Layers Work"
    USD layers work much like Photoshop layers. **Stacking another layer on top of the base file** lets you add or change properties without touching the original file. In this tutorial, you will stack the Robot Schema layer on top of the base asset (the rigged forklift).

    The Python script in Step 3 builds this layer structure for you automatically.

### 2-2. Verify the Working Directory

Open the directory where you saved your USD file from Tutorial 5 (e.g., `forklift.usd`). Create a `configuration/` subdirectory next to it if one does not already exist:

```
my_forklift/
├── forklift.usd                              ← Base asset
└── configuration/                            ← Create this
    └── forklift_robot_schema.usda            ← Will be created in this tutorial
```

## Step 3: Bulk Application via Python

Bulk application via Python is by far the most efficient approach when the robot has many links and joints. We use the script provided in the Isaac Sim official documentation as-is.

### 3-1. Open the Base Asset

1. Launch Isaac Sim and open `forklift.usd` from Tutorial 5.
2. Verify that the stage's default prim is set correctly (e.g., `/SMV_Forklift_B01_01`, the robot's root Xform).

!!! note "Checking the Default Prim"
    Select the robot's root Xform in the Stage panel and check the **Metadata** section of the **Properties** panel for `defaultPrim`. If it is not set, right-click the root Xform and select **Set as Default Prim**.

### 3-2. Open the Script Editor

1. From the menu, select **Window > Script Editor**.

### 3-3. Run the Bulk Application Script

Paste the following script into the Script Editor and click **Run** (the ▶ button):

```python
import omni.usd
import pxr
import usd.schema.isaac.robot_schema as rs
from pxr import Sdf, Usd, UsdGeom

stage = omni.usd.get_context().get_stage()

# Create a configuration/ sublayer in the same directory as the base asset
robot_asset_path = "/".join(stage.GetRootLayer().identifier.split("/")[:-1])
robot_asset = ".".join(stage.GetRootLayer().identifier.split("/")[-1].split(".")[:-1])
schema_asset = f"configuration/{robot_asset}_robot_schema.usda"
edit_layer = Sdf.Layer.FindOrOpen(f"{robot_asset_path}/{schema_asset}")
if not edit_layer:
    edit_layer = Sdf.Layer.CreateNew(f"{robot_asset_path}/{schema_asset}")

# Add sublayer to the stage (relative path), only if not already present
if schema_asset not in stage.GetRootLayer().subLayerPaths:
    stage.GetRootLayer().subLayerPaths.append(schema_asset)

# Make all edits in the edit layer
with pxr.Usd.EditContext(stage, edit_layer):
    default_prim = stage.GetDefaultPrim()

    # Apply the Robot API to the default prim.
    # This auto-populates the Links and Joints lists from the physics articulation.
    rs.ApplyRobotAPI(default_prim)

# Save the Robot Schema layer and the stage
edit_layer.Save()
stage.Save()

print(f"Robot Schema saved to {schema_asset}")
```

The script does the following:

1. Creates a new layer `configuration/<asset_name>_robot_schema.usda` next to the base asset and attaches it as a sublayer (skipped if already attached)
2. Applies **RobotAPI** to the default prim
3. `ApplyRobotAPI` automatically traverses the physics articulation, applies **LinkAPI to discovered rigid bodies** and **JointAPI to discovered joints**, and registers them in order in the `robotLinks` / `robotJoints` relationships
4. Writes all the changes to the Robot Schema layer and saves

!!! note "What changed in Isaac Sim 6.0"
    Previously, you had to walk every prim with `Usd.PrimRange` and manually call `ApplyLinkAPI` / `ApplyJointAPI`. In Isaac Sim 6.0, **`ApplyRobotAPI` handles the discovery, API application, and list registration automatically**. Auto-population requires the physics (articulation) to be authored on the stage. For assets that keep physics in a separate layer, temporarily add the physics layer as a sublayer during schema application and remove it before saving.

### 3-4. Verify the Result

If the Script Editor prints `Robot Schema saved to configuration/<...>_robot_schema.usda`, the script ran successfully.

Open the `configuration/` folder in your file manager and confirm that the new `*_robot_schema.usda` file exists.

!!! tip "Re-running the Script / Updating the Robot Structure"
    If the robot structure changes later (links or joints are added), either **reapply RobotAPI** to the root prim to re-run auto-population, or use **`RecalculateRobotSchema`** from `usd.schema.isaac.robot_schema.utils` (appends new links/joints while preserving the existing order, and removes invalid targets). In the GUI, the **Re-Calculate Robot Tree** button in the Properties panel (with the root prim selected) performs the same operation.

## Step 4: GUI Application (Supplementary)

You can also apply the Robot Schema through the GUI. This is convenient when you want to add APIs to a small number of prims or edit individual attributes.

### 4-1. Apply RobotAPI

1. In the Stage panel, select the robot's root Xform (e.g., `/SMV_Forklift_B01_01`).
2. Click the **+ Add** button in the Properties panel.
3. From the menu, select **Isaac > Robot Schema > Robot API**.
4. Confirm that a purple **Robot** section now appears in the Properties panel.

Just like the Python path, applying from the GUI automatically traverses the physics articulation, applies **IsaacLinkAPI / IsaacJointAPI** to the discovered rigid bodies and joints, and auto-registers them in the `robotLinks` / `robotJoints` lists.

!!! warning "Mind the authoring layer"
    If your asset follows the [Asset Structure Guideline](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/asset_structure.html), apply the Robot Schema either **in the base layer or in a dedicated Robot Schema layer** — not directly in the interface layer. Because auto-population requires authored physics, temporarily add the physics layer as a sublayer during schema application, then remove it before saving.

### 4-2. Edit Attributes

The newly added Robot section lets you set the following:

| Attribute | Example | Purpose |
|---|---|---|
| **Description** | `Custom forklift mobile robot rig` | Description of the robot |
| **Namespace** | `forklift` | Namespace for ROS / OmniGraph |
| **Robot Type** | `Mobile Base` | Robot category (dropdown; select `(Other)` to type a custom Token) |
| **License / Source / Version / Changelog** | `Apache-2.0`, etc. | Asset license, origin, version, and change history (metadata added in Isaac Sim 6.0) |
| **Robot Links** (relationship) | Each link prim's path | Ordered list of links that constitute the robot (drag to reorder) |
| **Robot Joints** (relationship) | Each joint prim's path | Ordered list of joints with DOF (drag to reorder) |

!!! note "What Robot Links / Robot Joints Mean"
    These relationships specify the order of links / joints "to be included in state reporting." Links and joints not registered in these relationships are still part of the articulation, but they will not be emitted in artifacts such as ROS joint state messages.

!!! tip "The Robot Schema widget in Isaac Sim 6.0"
    In Isaac Sim 6.0, selecting a prim with `IsaacRobotAPI` shows a dedicated **Robot Schema widget** in the Properties panel. From here you can edit metadata, add entries with the **Add Joint / Add Link** buttons (the picker is pre-filtered to compatible prims), reorder rows by dragging, run **Re-Calculate Robot Tree** (rescans the articulation), and use **Save to Robot Layer** (saves to the layer that authors `IsaacRobotAPI`).

### 4-3. Apply LinkAPI / JointAPI Individually

- For a link: select the rigid body prim → **+ Add > Isaac > Robot Schema > Robot Link**
- For a joint: select the joint prim → **+ Add > Isaac > Robot Schema > Robot Joint**

If you have already run the script in Step 3 (or applied the Robot API in 4-1), every link and joint will already have the corresponding API, so this step is normally unnecessary.

## Step 5: Verifying the Application

### 5-1. Verify in the Properties Panel

1. Select the robot's root prim in the Stage panel.
2. Scroll the Properties panel and confirm the **purple Robot section** is shown.
3. Select each link / joint and confirm the corresponding **Link** / **Joint** sections appear.

!!! tip "If the Sections Do Not Show"
    Type `Robot` in the search field at the top of the Properties panel, or switch the filter to **All**. The Raw USD Properties view will show entries such as `apiSchemas = ["IsaacRobotAPI", ...]`, which lets you confirm directly.

### 5-2. Verify with the Gain Tuner

If the Robot Schema is correctly applied, the Gain Tuner should recognize the robot:

1. Open **Tools > Robotics > Asset Editors > Gain Tuner** from the menu.
2. Open the **Select Robot** dropdown.
3. Confirm that your robot (e.g., `/SMV_Forklift_B01_01`) is listed.

If the dropdown does not show your robot, check whether the script in Step 3 produced an error and whether you reloaded the stage after saving.

### 5-3. Programmatic Verification with Python

You can also verify by running the following in the Script Editor:

```python
import omni.usd
import usd.schema.isaac.robot_schema as rs

stage = omni.usd.get_context().get_stage()
default_prim = stage.GetDefaultPrim()

print("Applied schemas:", default_prim.GetAppliedSchemas())
print("Has RobotAPI:", default_prim.HasAPI(rs.Classes.ROBOT_API.value))

# Inspect the targets of robotLinks / robotJoints
for rel_name in [rs.Relations.ROBOT_LINKS.name, rs.Relations.ROBOT_JOINTS.name]:
    rel = default_prim.GetRelationship(rel_name)
    targets = rel.GetTargets()
    print(f"{rel_name} target count: {len(targets)}")
```

If `Has RobotAPI: True` is printed and the link / joint counts match what you expect, the application succeeded.

## Step 6 (Optional): Adding a Site (Reference Point)

For meaningful points on the robot — such as the end-effector of an arm or the tip of a forklift's fork — applying `IsaacSiteAPI` makes them easier to consume by downstream tools (Pick & Place, Grasp Editor, etc.).

!!! note "Renamed from IsaacReferencePointAPI"
    In Isaac Sim 6.0, the schema for reference points was replaced: `IsaacReferencePointAPI` became **`IsaacSiteAPI`**. Assets carrying the old schema still work but emit deprecation warnings; migrate them in one pass with `UpdateDeprecatedSchemas(robot_prim)`. Sites can also be registered in the `robotLinks` relationship (immediately after their parent link, or at the end of the list).

!!! warning "The Site Prim Must Exist Beforehand"
    `IsaacSiteAPI` is a mechanism that **adds an API to an existing prim** — it does not create a prim for you. Applying the API to a path where no prim exists will produce a runtime error like `RuntimeError: Accessed invalid null prim`. Therefore, **create the site Xform prim first** and place it appropriately before applying the API.

### 6-1. GUI Example

1. In the Stage panel, right-click the parent prim (e.g., `/SMV_Forklift_B01_01/lift`).
2. Select **Create > Xform** to create a new Xform.
3. Rename the new Xform to `fork_tip`.
4. In the Properties panel's **Transform** section, set the position / orientation where the site should be (e.g., the fork tip coordinates).
5. With `fork_tip` selected, choose **+ Add > Isaac > Robot Schema > Robot Site**.
6. Enter a description (e.g., `Fork tip for object insertion`) in **Description**.
7. Set the reference axis (`X`, `Y`, or `Z`) in **Forward Axis**.

### 6-2. Python Example

A self-contained example that creates the site prim if it does not yet exist, places it, and then applies the API:

```python
from pxr import Usd, UsdGeom, Gf
import omni.usd

stage = omni.usd.get_context().get_stage()

# Create the site prim if it does not exist
site_path = "/SMV_Forklift_B01_01/lift/fork_tip"
site_prim = stage.GetPrimAtPath(site_path)
if not site_prim.IsValid():
    site_xform = UsdGeom.Xform.Define(stage, site_path)
    # Set the local transform (adjust to the actual fork tip position in your asset)
    site_xform.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, 0.5))
    site_prim = site_xform.GetPrim()

# Apply IsaacSiteAPI (by schema identifier)
site_prim.ApplyAPI("IsaacSiteAPI")

# Set attributes
site_prim.GetAttribute("isaac:Description").Set("Fork tip for object insertion")
site_prim.GetAttribute("isaac:forwardAxis").Set("Z")

print(f"IsaacSiteAPI applied to {site_path}")
```

!!! tip "Reusing an Existing Prim as the Site / Auto-detection"
    If a suitable Xform or link already exists where you want the site, you can simply apply `IsaacSiteAPI` to it without creating a new prim. In that case, remove the entire `if not site_prim.IsValid():` block from the script above.

    You can also use **`DetectAndApplySites(stage, robot_prim)`** from `usd.schema.isaac.robot_schema.utils`, which automatically detects leaf Xforms (with no children) under each link as site candidates and applies `IsaacSiteAPI` in bulk.

## Troubleshooting

| Symptom | Cause | Resolution |
|---|---|---|
| The robot does not show up in the Gain Tuner | RobotAPI is not applied | Run the script from Step 3 or apply **IsaacRobotAPI** to the root prim from the GUI |
| Import error for `usd.schema.isaac.robot_schema` | The `isaacsim.robot.schema` extension is disabled | Search for `isaacsim.robot.schema` in **Window > Extensions** and enable it |
| `default_prim` is `None` | The default prim is not set | Right-click the root Xform and select **Set as Default Prim** |
| `robotLinks` / `robotJoints` are empty | No rigid bodies or joints exist under the Default Prim when the script runs | Check the prim hierarchy or change `default_prim` to the correct root |
| Relationship lists are stale / contain invalid targets | The lists were not updated after the robot structure changed | Run **Re-Calculate Robot Tree** in the Properties panel (or `RecalculateRobotSchema`). Check **Force Update** first if you want to rebuild the ordering from scratch |
| The Robot section does not appear in the Properties panel | Extension load failure / wrong prim selected | Restart Isaac Sim, reload the stage, and re-select the root prim |
| `RuntimeError: Accessed invalid null prim` when applying an API | The target path does not exist as a prim | Verify the result of `stage.GetPrimAtPath(...)` with `prim.IsValid()`. If absent, create the prim first with `UsdGeom.Xform.Define` and then apply the API (see Step 6-2) |
| Deprecation warnings on old assets (ReferencePointAPI / per-axis DoFOffset) | The schema changed in Isaac Sim 6.0 | Migrate in one pass to IsaacSiteAPI / `DofOffsetOpOrder` with `UpdateDeprecatedSchemas(robot_prim)` |

## Summary

This tutorial covered the following topics:

1. **The Robot Schema concept** — an extension schema that complements the Physics Schema with robot-specific semantics
2. **Roles and attributes of the four main APIs** (RobotAPI / LinkAPI / JointAPI / SiteAPI)
3. **Non-destructive application via a dedicated layer** (`configuration/<robot>_robot_schema.usda`)
4. **Bulk application via Python** — automatic link/joint discovery and registration with `ApplyRobotAPI`
5. **Supplementary GUI application** — adding APIs to individual prims and editing attributes
6. **Verifying the result** — Properties panel and Gain Tuner dropdown
7. **Adding a site (reference point)** — registering meaningful points such as end-effectors

This brings a manually rigged robot to parity with one imported from URDF, and makes it usable from Asset Editor tools such as the Gain Tuner and Grasp Editor.

!!! tip "Official Documentation"
    For more detailed Robot Schema specifications (Surface Gripper, AttachmentPointAPI, Named Pose, robot composition, the utility function suite, IK solvers, and so on), refer to the Isaac Sim official documentation: [Robot Schema](https://docs.isaacsim.omniverse.nvidia.com/latest/omniverse_usd/robot_schema.html). For interactively inspecting and editing the Robot Schema, Isaac Sim 6.0 also offers the **Robot Inspector** (formerly Robot Hierarchy) and the **Robot Poser**.

## Next Steps

Proceed to the next tutorial, "[Setup a Manipulator](06_setup_manipulator.md)," to enter the intermediate section by importing a robot arm from URDF. The Robot Schema is automatically applied during URDF import, so the concepts you learned in this tutorial will continue to apply.
