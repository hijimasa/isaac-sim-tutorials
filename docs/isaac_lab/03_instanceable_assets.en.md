---
title: Instanceable Assets
---

# Instanceable Assets

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Understand the hierarchy requirements for making assets instanceable
- Create instanceable assets with the URDF and MJCF importers
- Convert existing assets to instanceable assets with utility scripts

## Overview

Reinforcement learning scenes contain many clones of the same robot. Marking shared meshes as **instanceable** leverages USD Scenegraph Instancing so every copy references a single mesh, reducing memory consumption.

## Hierarchy Requirement

USD prohibits modifying properties on descendants of instanced prims, so only mesh prims are instanced. Each mesh prim must have a parent Xform prim, which holds the reference to the master mesh USD:

```
World
  |_ Robot
       |_ Collisions
               |_ Sphere_Xform
               |      |_ Sphere
               |_ Box_Xform
                      |_ Box
```

## Using URDF and MJCF Importers

Check **Create Instanceable Asset** and set **Instanceable USD Path** (default `./instanceable_meshes.usd`). The import produces two USD files: the mesh USD and the master robot definition that references it. Add only the master USD to new stages.

## Modifying Existing Assets

Two Script Editor utilities help convert existing assets:

- `create_parent_xforms()` — inserts a new Xform parent for every Mesh/Geometry prim. Note that USD Relationships on the meshes (visual/physics materials, filtered collision pairs) are removed; set them on the parent Xforms instead.
- `convert_asset_instanceable()` — optionally runs the above, copies the asset to `<asset>_meshes.usd`, then marks each mesh's parent as instanceable with a reference to the mesh USD.

See the Japanese page for the full source code of both utilities.

## Next Steps

- Back to the [Isaac Lab tutorial index](index.md)
