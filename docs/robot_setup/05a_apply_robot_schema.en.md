---
title: Applying the Robot Schema
---

# Applying the Robot Schema

## Learning Objectives

After completing this tutorial, you will have learned:

- What the **Robot Schema** is and why it is needed
- The roles of the four main APIs (**RobotAPI / LinkAPI / JointAPI / ReferencePointAPI**)
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

In [Tutorial 5](05_rig_mobile_robot.md), you applied an **Articulation Root** to the forklift so that it could be driven as an articulation. While that is enough for the physics simulation itself to work, the higher-level tools introduced in Isaac Sim 5.1 — such as the **Gain Tuner** ([Tutorial 11](11_joint_tuning.md)), **Grasp Editor**, **XRDF Editor**, and **Robot Wizard** — require an additional schema, the **Robot Schema**, to be applied so that the asset is recognized as a "robot."

In this tutorial, you will learn how to apply the Robot Schema to a manually rigged robot so that it integrates with the rest of the tooling. The flow is:

1. **Understand what the Robot Schema is**
2. **Set up a dedicated layer** for non-destructive schema application
3. **Apply the schema in bulk via Python** (the officially recommended approach)
4. **Apply the schema via GUI** for individual prims or fine-tuning
5. **Verify the result** in the Properties panel and the Gain Tuner

!!! note "Not needed for robots imported via URDF / MJCF"
    When you load a robot through the [URDF Importer](06_setup_manipulator.md) or the MJCF Importer, those importers **automatically apply the Robot Schema**. The UR10e in [Tutorials 6 / 7](06_setup_manipulator.md) is one such example. This tutorial is for cases where you have **manually rigged a robot without going through URDF** — for instance, the deliverable from Tutorial 5.

## Step 1: What the Robot Schema Is

The **Robot Schema** is an extension schema defined by NVIDIA to describe robots, complementing the OpenUSD [Physics Schema](https://openusd.org/release/api/physics_8h_source.html). While the Physics Schema defines the **physical framework** ("rigid bodies, joints, articulations"), the Robot Schema adds **semantic meaning** ("which prim is the robot's core, and which are its links / joints / reference points").

### 1-1. Why the Physics Schema Alone Is Not Enough

The Physics Schema is an open USD standard and is broadly applicable, but it has **no mechanism for declaring "this is a robot."** For example:

- Enumerate an articulation as a single robot
- Convey a namespace (such as `/robot1`, `/robot2`) to ROS or OmniGraph
- Describe robot-specific metadata such as DOF reporting order, acceleration / jerk limits
- Define attachment points for grippers and reference points for tools

These fall outside the scope of the Physics Schema. The **Robot Schema fills this gap** and provides a common foundation for the various Asset Editor tools to consistently understand robot structure.

### 1-2. The Four Main APIs

The Robot Schema consists of several API schemas. This tutorial focuses on the four most important ones:

| API Schema | Applied To | Role | Key Attributes / Relationships |
|---|---|---|---|
| **IsaacRobotAPI** | The robot's root prim | Declares "this is the robot." Tools use it as the entry point to recognize a robot | `description`, `namespace`, `robotType`, `robotLinks` (relationship), `robotJoints` (relationship) |
| **IsaacLinkAPI** | Each link (rigid body) prim | Marks the prim as a robot link, enables name overriding | `nameOverride` |
| **IsaacJointAPI** | Each joint prim | Marks the prim as a robot joint, holds DOF offsets and acceleration / jerk limits | `nameOverride`, `Rot_X:DofOffset` through `Tr_Z:DofOffset`, `AccelerationLimit`, `JerkLimit` |
| **IsaacReferencePointAPI** | Reference prims such as end-effectors or tool mount points | Represents "meaningful points on the robot" such as tool mounts and sensor locations | `description`, `forwardAxis` |

In addition, the schema defines `IsaacAttachmentPointAPI` (for gripper attachment points) and the `IsaacSurfaceGripper` prim type (for surface grippers as a whole). Apply these as needed.

!!! tip "Corresponding Python Symbols"
    Each API can be accessed via the `usd.schema.isaac.robot_schema` module:

    | Python Symbol | Apply Function |
    |---|---|
    | `Classes.ROBOT_API.value` (= `"IsaacRobotAPI"`) | `ApplyRobotAPI(prim)` |
    | `Classes.LINK_API.value` (= `"IsaacLinkAPI"`) | `ApplyLinkAPI(prim)` |
    | `Classes.JOINT_API.value` (= `"IsaacJointAPI"`) | `ApplyJointAPI(prim)` |
    | `Classes.REFERENCE_POINT_API.value` (= `"IsaacReferencePointAPI"`) | `ApplyReferencePointAPI(prim)` |

### 1-3. How Tools Use the Robot Schema

As a concrete example, look at how the Gain Tuner works. It traverses the entire stage and lists **only prims with `IsaacRobotAPI` applied** in its dropdown menu (per the implementation of the `isaacsim.robot_setup.gain_tuner` extension in Isaac Sim 5.1). If the Robot Schema is not applied, the robot will be invisible to the Gain Tuner even when the Articulation Root is enabled.

By the same mechanism, the Grasp Editor consults `IsaacAttachmentPointAPI`, and the XRDF Editor consults the DOF offset information in `IsaacJointAPI`.

## Step 2: Preparing the Layer Structure

Isaac Sim's [Asset Structure Guideline](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_setup/asset_structure.html) recommends **storing the Robot Schema application in a dedicated layer**. The benefits are:

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
from pxr import Usd, UsdGeom, Sdf
import pxr
import omni.usd
import usd.schema.isaac.robot_schema as rs

stage = omni.usd.get_context().get_stage()

# Create a configuration/ sublayer in the same directory as the base asset
robot_asset_path = "/".join(stage.GetRootLayer().identifier.split("/")[:-1])
robot_asset = ".".join(stage.GetRootLayer().identifier.split("/")[-1].split(".")[:-1])
schema_asset = f"configuration/{robot_asset}_robot_schema.usda"
edit_layer = Sdf.Layer.FindOrOpen(f"{robot_asset_path}/{schema_asset}")
if not edit_layer:
    edit_layer = Sdf.Layer.CreateNew(f"{robot_asset_path}/{schema_asset}")
stage.GetRootLayer().subLayerPaths.append(schema_asset)

# Switch the edit target to the Robot Schema layer and apply APIs in bulk
with pxr.Usd.EditContext(stage, edit_layer):
    default_prim = stage.GetDefaultPrim()

    # (1) Apply RobotAPI to the root prim
    rs.ApplyRobotAPI(default_prim)
    robot_links = default_prim.GetRelationship(rs.Relations.ROBOT_LINKS.name)
    robot_joints = default_prim.GetRelationship(rs.Relations.ROBOT_JOINTS.name)

    # (2) Walk all prims and apply Link / Joint APIs
    for prim in Usd.PrimRange(default_prim):
        # Apply LinkAPI to rigid bodies
        if "PhysicsRigidBodyAPI" in prim.GetAppliedSchemas():
            rs.ApplyLinkAPI(prim)
            robot_links.AddTarget(prim.GetPath())

        # Apply JointAPI to joints
        if prim.IsA(pxr.UsdPhysics.Joint):
            rs.ApplyJointAPI(prim)
            # Fixed joints have no DOF, so exclude them from robot_joints
            if not prim.IsA(pxr.UsdPhysics.FixedJoint):
                robot_joints.AddTarget(prim.GetPath())

# Save the Robot Schema layer and the stage
edit_layer.Save()
stage.Save()

print(f"Robot Schema saved to {schema_asset}")
```

The script does the following:

1. Creates a new layer `configuration/<asset_name>_robot_schema.usda` next to the base asset and attaches it as a sublayer
2. Applies **RobotAPI** to the default prim and creates the `robotLinks` and `robotJoints` relationships
3. Walks every prim in the stage and applies **LinkAPI to rigid bodies** and **JointAPI to joints**
4. Registers the links and joints (excluding fixed joints) in the root prim's `robotLinks` / `robotJoints` relationships
5. Writes all the changes to the Robot Schema layer and saves

### 3-4. Verify the Result

If the Script Editor prints `Robot Schema saved to configuration/<...>_robot_schema.usda`, the script ran successfully.

Open the `configuration/` folder in your file manager and confirm that the new `*_robot_schema.usda` file exists.

!!! tip "Re-running the Script"
    Re-running the script on a stage where the Robot Schema is already applied may produce duplicate `AddTarget` registrations. If you need to re-run, either delete `configuration/*_robot_schema.usda` first or add a guard that checks whether the schema is already applied.

## Step 4: GUI Application (Supplementary)

You can also apply the Robot Schema through the GUI. This is convenient when you want to add APIs to a small number of prims or edit individual attributes.

### 4-1. Apply RobotAPI

1. In the Stage panel, select the robot's root Xform (e.g., `/SMV_Forklift_B01_01`).
2. Click the **+ Add** button in the Properties panel.
3. From the menu, select **Edit API Schema**.
4. In the dialog's search field, type `IsaacRobotAPI`, select it, and apply.
5. Confirm that a purple **Robot** section now appears in the Properties panel.

### 4-2. Edit Attributes

The newly added Robot section lets you set the following:

| Attribute | Example | Purpose |
|---|---|---|
| **Description** | `Custom forklift mobile robot rig` | Description of the robot |
| **Namespace** | `forklift` | Namespace for ROS / OmniGraph |
| **Robot Type** | `mobile_robot` | Robot category (an arbitrary Token) |
| **Robot Links** (relationship) | Each link prim's path | Ordered list of links that constitute the robot |
| **Robot Joints** (relationship) | Each joint prim's path | Ordered list of joints with DOF |

!!! note "What Robot Links / Robot Joints Mean"
    These relationships specify the order of links / joints "to be included in state reporting." Links and joints not registered in these relationships are still part of the articulation, but they will not be emitted in artifacts such as ROS joint state messages.

### 4-3. Apply LinkAPI / JointAPI Individually

- For a link: select the rigid body prim → **+ Add > Edit API Schema > IsaacLinkAPI**
- For a joint: select the joint prim → **+ Add > Edit API Schema > IsaacJointAPI**

If you have already run the script in Step 3, every link and joint will already have the corresponding API, so this step is normally unnecessary.

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

## Step 6 (Optional): Adding a Reference Point

For meaningful points on the robot — such as the end-effector of an arm or the tip of a forklift's fork — applying `IsaacReferencePointAPI` makes them easier to consume by downstream tools (Pick & Place, Grasp Editor, etc.).

!!! warning "The Reference Point Prim Must Exist Beforehand"
    `IsaacReferencePointAPI` is a mechanism that **adds an API to an existing prim** — it does not create a prim for you. Applying the API to a path where no prim exists will produce a runtime error like:

    ```
    RuntimeError: Accessed invalid null prim
      ... in ApplyReferencePointAPI
    ```

    Therefore, **create the reference Xform prim first** and place it appropriately before applying the API.

### 6-1. GUI Example

1. In the Stage panel, right-click the parent prim (e.g., `/SMV_Forklift_B01_01/lift`).
2. Select **Create > Xform** to create a new Xform.
3. Rename the new Xform to `fork_tip`.
4. In the Properties panel's **Transform** section, set the position / orientation where the reference point should be (e.g., the fork tip coordinates).
5. With `fork_tip` selected, choose **+ Add > Edit API Schema > IsaacReferencePointAPI**.
6. Enter a description (e.g., `Fork tip for object insertion`) in **Description**.
7. Set the reference axis (`X`, `Y`, or `Z`) in **Forward Axis**.

### 6-2. Python Example

A self-contained example that creates the reference point prim if it does not yet exist, places it, and then applies the API:

```python
from pxr import Usd, UsdGeom, Gf
import omni.usd
import usd.schema.isaac.robot_schema as rs

stage = omni.usd.get_context().get_stage()

# Create the reference point prim if it does not exist
ref_path = "/SMV_Forklift_B01_01/lift/fork_tip"
ref_prim = stage.GetPrimAtPath(ref_path)
if not ref_prim.IsValid():
    ref_xform = UsdGeom.Xform.Define(stage, ref_path)
    # Set the local transform (adjust to the actual fork tip position in your asset)
    ref_xform.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, 0.5))
    ref_prim = ref_xform.GetPrim()

# Apply ReferencePointAPI
rs.ApplyReferencePointAPI(ref_prim)

# Set attributes
ref_prim.GetAttribute("isaac:Description").Set("Fork tip for object insertion")
ref_prim.GetAttribute("isaac:forwardAxis").Set("Z")

print(f"ReferencePointAPI applied to {ref_path}")
```

!!! tip "Reusing an Existing Prim as the Reference Point"
    If a suitable Xform or link already exists where you want the reference point, you can simply apply `ApplyReferencePointAPI` to it without creating a new prim. In that case, remove the entire `if not ref_prim.IsValid():` block from the script above.

    It is also valid to add ReferencePointAPI to a link (rigid body); in that case the same prim ends up with both LinkAPI and ReferencePointAPI applied.

## Troubleshooting

| Symptom | Cause | Resolution |
|---|---|---|
| The robot does not show up in the Gain Tuner | RobotAPI is not applied | Run the script from Step 3 or apply **IsaacRobotAPI** to the root prim from the GUI |
| Import error for `usd.schema.isaac.robot_schema` | The `isaacsim.robot.schema` extension is disabled | Search for `isaacsim.robot.schema` in **Window > Extensions** and enable it |
| `default_prim` is `None` | The default prim is not set | Right-click the root Xform and select **Set as Default Prim** |
| `robotLinks` / `robotJoints` are empty | No rigid bodies or joints exist under the Default Prim when the script runs | Check the prim hierarchy or change `default_prim` to the correct root |
| Duplicate relationships when re-running | Repeated `AddTarget` calls | Delete `configuration/*_robot_schema.usda` and re-run |
| The Robot section does not appear in the Properties panel | Extension load failure / wrong prim selected | Restart Isaac Sim, reload the stage, and re-select the root prim |
| `RuntimeError: Accessed invalid null prim` from `ApplyReferencePointAPI` or similar | The target path does not exist as a prim | Verify the result of `stage.GetPrimAtPath(...)` with `prim.IsValid()`. If absent, create the prim first with `UsdGeom.Xform.Define` and then apply the API (see Step 6-2) |

## Summary

This tutorial covered the following topics:

1. **The Robot Schema concept** — an extension schema that complements the Physics Schema with robot-specific semantics
2. **Roles and attributes of the four main APIs** (RobotAPI / LinkAPI / JointAPI / ReferencePointAPI)
3. **Non-destructive application via a dedicated layer** (`configuration/<robot>_robot_schema.usda`)
4. **Bulk application via Python** — automatic application across all links and joints
5. **Supplementary GUI application** — adding APIs to individual prims and editing attributes
6. **Verifying the result** — Properties panel and Gain Tuner dropdown
7. **Adding a reference point** — registering meaningful points such as end-effectors

This brings a manually rigged robot to parity with one imported from URDF, and makes it usable from Asset Editor tools such as the Gain Tuner and Grasp Editor.

!!! tip "Official Documentation"
    For more detailed Robot Schema specifications (Surface Gripper, AttachmentPointAPI, robot composition, and so on), refer to the Isaac Sim official documentation: [Robot Schema](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/omniverse_usd/robot_schema.html).

## Next Steps

Proceed to the next tutorial, "[Setup a Manipulator](06_setup_manipulator.md)," to enter the intermediate section by importing a robot arm from URDF. The Robot Schema is automatically applied during URDF import, so the concepts you learned in this tutorial will continue to apply.
