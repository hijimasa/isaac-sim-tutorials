---
title: Instanceable Assets
---

# Instanceable Assets

## Learning Objectives

After completing this tutorial, you will know:

- The **hierarchy requirements** for making an asset instanceable
- How to create instanceable assets directly with the **URDF / MJCF importers**
- How to use the utility scripts that convert **existing USD assets** to instanceable ones

## Getting Started

### Prerequisites

- Completion of [Tutorial 2: Getting Started with Cloner](02_cloner.md)
- Understanding the basics of [URDF import](../importer_exporter/01_import_urdf.md) and [MJCF import](../importer_exporter/03_import_mjcf.md)

### Estimated Time

About 10–15 minutes

### Overview

In reinforcement learning, training typically runs in large scenes containing many clones of the same robot. The more robots you add, the more memory is consumed by each full set of robot and mesh assets.

To keep this memory consumption down, you can use USD's [Scenegraph Instancing](https://graphics.pixar.com/usd/dev/api/_usd__page__scenegraph_instancing.html) feature to mark the meshes shared by all copies of the robot as **instanceable**. Each copy then **references a single mesh entity**, preventing the same mesh from being duplicated many times in the scene and reducing the overall memory usage of the simulation.

!!! note "An intuitive picture of instancing"
    Where normal cloning "copies the robot's 3D data 1000 times", instancing "keeps a single copy of the 3D data and has 1000 placements reference it". The appearance and physical behavior do not change, but the mesh data exists only once in memory. In exchange, there is one constraint: **properties of the descendants of an instanced prim can no longer be modified individually**. Since a robot's mesh geometry does not vary between environments, this constraint is normally not a problem.

## Step 1: Understanding the Hierarchy Requirements

USD **prohibits modifying properties on the descendants** of an instanced prim. For robot assets, the mesh properties never differ between environments during simulation, so normally **only the mesh prims** are targeted for instancing (the Transform of each link moves differently per robot and therefore cannot be instanced).

For the instanceable flag to work, the asset's tree structure must have a specific shape. Concretely, each mesh (or primitive geometry) prim you want to instance needs a **parent Xform prim**. The reference to the master USD file holding the mesh definition is added to this parent Xform.

For example, the following structure **cannot** be instanced:

```
World
  |_ Robot
       |_ Collisions
               |_ Sphere
               |_ Box
```

It must be changed into a structure where each mesh has a parent Xform inserted:

```
World
  |_ Robot
       |_ Collisions
               |_ Sphere_Xform
               |      |_ Sphere
               |_ Box_Xform
                      |_ Box
```

If the original `Sphere` or `Box` prims had References set on them, those need to move to the `Sphere_Xform` / `Box_Xform` side.

## Step 2: Creating Assets with the URDF / MJCF Importers

Both the [URDF importer](../importer_exporter/01_import_urdf.md) and the [MJCF importer](../importer_exporter/03_import_mjcf.md) support an option to **import directly as an instanceable asset**. When you choose this option, the imported asset is split into **two USD files** following the hierarchy requirements above: a USD for the mesh data, and the robot definition itself (the master stage) that references it.

Procedure:

1. Check the **Create Instanceable Asset** option in the import settings.
2. In the **Instanceable USD Path** text box, specify the destination file path for the mesh data. The default is `./instanceable_meshes.usd`, which generates `instanceable_meshes.usd` in the current directory.
3. Run the import.

After the import, the stage (master stage) shows the robot definition. If you expand the robot's hierarchy in the Stage panel, you can confirm that the parent prims holding meshes as descendants are marked **Instanceable** and reference prims inside the USD file specified as the Instanceable USD Path. Also, the attributes of the descendant meshes can no longer be modified.

When adding the instanced asset to a new stage, it is enough to **add only the master USD file** (the mesh USD is referenced automatically).

## Step 3: Converting Existing Assets

Existing (non-instanceable) assets cannot necessarily be instanced as-is, because of the hierarchy requirements. Here we introduce two utility scripts that make the conversion easy. Both are run from **Window > Script Editor**.

### 3-1. Inserting Parent Xforms for Meshes (create_parent_xforms)

First, fix the hierarchy so that every mesh prim has a parent Xform. The following utility automatically inserts a new Xform prim as the parent of every mesh prim in the stage:

```python
import omni.usd
import omni.client

from pxr import UsdGeom, Sdf

def create_parent_xforms(asset_usd_path, source_prim_path, save_as_path=None):
    """ Adds a UsdGeom.Xform parent prim to each Mesh/Geometry prim under source_prim_path.
        If a Mesh/Geometry prim has a material binding, it is moved to the new parent prim.

        Args:
            asset_usd_path (str): USD file path for the asset
            source_prim_path (str): USD path of the root prim
            save_as_path (str): USD file path to save the modified USD to. If None, overwrites the same file.
    """
    omni.usd.get_context().open_stage(asset_usd_path)
    stage = omni.usd.get_context().get_stage()

    prims = [stage.GetPrimAtPath(source_prim_path)]
    edits = Sdf.BatchNamespaceEdit()
    while len(prims) > 0:
        prim = prims.pop(0)
        print(prim)
        if prim.GetTypeName() in ["Mesh", "Capsule", "Sphere", "Cube"]:
            new_xform = UsdGeom.Xform.Define(stage, str(prim.GetPath()) + "_xform")
            print(prim, new_xform)
            edits.Add(Sdf.NamespaceEdit.Reparent(prim.GetPath(), new_xform.GetPath(), 0))
            continue

        children_prims = prim.GetChildren()
        prims = prims + children_prims

    stage.GetRootLayer().Apply(edits)

    if save_as_path is None:
        omni.usd.get_context().save_stage()
    else:
        omni.usd.get_context().save_as_stage(save_as_path)
```

!!! note "About `Box` in the type name list"
    In the official documentation's code, the check list is `["Mesh", "Capsule", "Sphere", "Box"]`, but the type name of USD's box prim is `Cube` (`UsdGeomCube`) — there is no type named `Box` (the limitations list in Tutorial 2 also says `Cube`). As-is, Cube prims would slip through the conversion, so this page corrects it to `Cube`. If your assets contain Cylinder or Cone prims, add them to the list as needed.

The arguments are:

| Argument | Description |
|---|---|
| `asset_usd_path` | File path of the existing USD asset |
| `source_prim_path` | USD path of the asset's root prim |
| `save_as_path` | Destination for the modified asset. If omitted, the original file is overwritten |

```python
create_parent_xforms(
    asset_usd_path=ASSET_USD_PATH,
    source_prim_path=SOURCE_PRIM_PATH,
    save_as_path=SAVE_AS_PATH
)
```

!!! warning "USD Relationships on the meshes are lost"
    This conversion removes all [USD Relationships](https://graphics.pixar.com/usd/dev/api/class_usd_relationship.html) on the referenced meshes. This is because the Relationship targets point inside the original prims and may become invalid from the new stage. Examples of Relationships commonly set on meshes include visual materials, physics materials, and filtered collision pairs. We recommend setting these Relationships **on the parent Xform** rather than on the mesh itself.

### 3-2. Converting in One Go (convert_asset_instanceable)

This is an all-in-one conversion utility that includes the processing above. If you pass `create_xforms=True`, it starts by inserting the parent Xforms, generates a new USD file for referencing (`<asset name>_meshes.usd`), then walks the asset tree, marks the parents of mesh/primitive prims as instanceable, and inserts references to the mesh USD:

```python
def convert_asset_instanceable(asset_usd_path, source_prim_path, save_as_path=None, create_xforms=True):
    """ Makes all mesh/geometry prims instanceable.
        Can optionally add UsdGeom.Xform prims as parents of the mesh/geometry prims.
        Makes a copy of the asset USD file, which is used for referencing.
        Updates the asset so that the parent prims of the mesh/geometry prims reference the copied USD file.

        Args:
            asset_usd_path (str): USD file path for the asset
            source_prim_path (str): USD path of the root prim
            save_as_path (str): USD file path to save the modified USD to. If None, overwrites the same file.
            create_xforms (bool): Whether to add parent Xforms to the mesh/geometry prims.
    """

    if create_xforms:
        create_parent_xforms(asset_usd_path, source_prim_path, save_as_path)
        asset_usd_path = save_as_path

    instance_usd_path = ".".join(asset_usd_path.split(".")[:-1]) + "_meshes.usd"
    omni.client.copy(asset_usd_path, instance_usd_path)
    omni.usd.get_context().open_stage(asset_usd_path)
    stage = omni.usd.get_context().get_stage()

    prims = [stage.GetPrimAtPath(source_prim_path)]
    while len(prims) > 0:
        prim = prims.pop(0)
        if prim:
            if prim.GetTypeName() in ["Mesh", "Capsule", "Sphere", "Cube"]:
                parent_prim = prim.GetParent()
                if parent_prim and not parent_prim.IsInstance():
                    parent_prim.GetReferences().AddReference(assetPath=instance_usd_path, primPath=str(parent_prim.GetPath()))
                    parent_prim.SetInstanceable(True)
                    continue

            children_prims = prim.GetChildren()
            prims = prims + children_prims

    if save_as_path is None:
        omni.usd.get_context().save_stage()
    else:
        omni.usd.get_context().save_as_stage(save_as_path)
```

## Summary

This tutorial covered the following topics:

1. The **hierarchy requirements** for instanceable assets (a parent Xform for each mesh)
2. Creating assets with the **Create Instanceable Asset** option of the **URDF / MJCF importers**
3. The utilities for **converting existing assets** (`create_parent_xforms` / `convert_asset_instanceable`)

This completes the Isaac Lab tutorial series.

## Next Steps

- Back to the [Isaac Lab tutorial index](index.md)
- To move on to training itself, head to the [official Isaac Lab documentation](https://isaac-sim.github.io/IsaacLab)
