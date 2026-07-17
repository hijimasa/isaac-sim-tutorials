---
title: Getting Started with Cloner
---

# Getting Started with Cloner

## Learning Objectives

After completing this tutorial, you will know:

- How to duplicate environments with the **Cloner** class
- Automatic grid placement with the **GridCloner** class
- Accessing cloned objects with the **vectorized API** (`XformPrim`)
- **Physics replication** and advanced parameters such as `copy_from_source`

## Getting Started

### Prerequisites

- Familiarity with basic Isaac Sim usage and the Script Editor
- Python scripting knowledge at the level of the [Core API tutorials](../core_api/index.md)

### Estimated Time

About 10–15 minutes

### Overview

In reinforcement learning, it is common to lay out **many copies of an environment** performing the same task and collect data (trajectories) from all of them simultaneously. The **Cloner** interface is an API that makes this "duplicate the environment as many times as needed" step easy. Besides the duplication itself, it provides utilities for generating the target paths, computing the placement coordinates automatically, and excluding collisions between clones.

This tutorial proceeds in the following order:

1. **Cloner basics** — duplicate a cube into 4 copies
2. **GridCloner** — place clones on a grid automatically
3. **Accessing the cloned objects** — manipulate them together through vectorized APIs
4. **Advanced topics** — physics replication and `copy_from_source`

## Step 1: Preparation

1. Open the extensions window via **Window > Extensions**, search for **Isaac Sim Cloner** (`isaacsim.core.cloner`), and enable it with the toggle switch next to its name.
2. Open the Script Editor via **Window > Script Editor**. All the sample code below can be pasted into the Script Editor and executed with **Run**.

!!! warning "Don't forget to enable the extension"
    Before running the snippets below, make sure `isaacsim.core.cloner` is enabled. Otherwise you will get an ImportError at `from isaacsim.core.cloner import Cloner`.

## Step 2: Cloner Basics

As a simple first example, let's create a scene with 4 cubes:

```python
from isaacsim.core.cloner import Cloner    # import the Cloner interface
from isaacsim.core.experimental.utils.stage import get_current_stage
from pxr import UsdGeom

# create the base environment with one cube
base_env_path = "/World/Cube_0"
UsdGeom.Cube.Define(get_current_stage(), base_env_path)

# create an instance of the Cloner
cloner = Cloner()

# generate 4 paths that begin with "/World/Cube" (a _{index} suffix is appended)
target_paths = cloner.generate_paths("/World/Cube", 4)

# clone the cube to the generated paths
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths)
```

The stage now contains 4 cubes: `/World/Cube_0`, `/World/Cube_1`, `/World/Cube_2`, and `/World/Cube_3`. However, as it stands they are all created **stacked at the same position**.

To give each cube a position, replace the last line with:

```python
import numpy as np

cube_positions = np.array([[0, 0, 0], [3, 0, 0], [6, 0, 0], [9, 0, 0]])

# clone to the specified positions
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths, positions=cube_positions)
```

If you want to specify the orientation of each clone, pass an `orientations` argument in the same way (also an `np.ndarray`).

## Step 3: Grid Placement with GridCloner

**GridCloner** is a specialization of Cloner that automatically places the clones **on a grid**, without you having to precompute positions or orientations. Specify the spacing between clones (`spacing`) at initialization:

```python
from isaacsim.core.cloner import GridCloner    # import the GridCloner interface
from isaacsim.core.experimental.utils.stage import get_current_stage
from pxr import UsdGeom

# create the base environment with one cube
base_env_path = "/World/Cube_0"
UsdGeom.Cube.Define(get_current_stage(), base_env_path)

# create a GridCloner with spacing 3
cloner = GridCloner(spacing=3)

# generate 4 paths that begin with "/World/Cube"
target_paths = cloner.generate_paths("/World/Cube", 4)

# clone (the placement is computed automatically)
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths)
```

This gives you a scene with 4 cubes arranged on a grid. The placement of parallel environments in reinforcement learning (`env_0`, `env_1`, ...) is done with this mechanism.

## Step 4: Accessing the Cloned Objects

The state of the cloned objects can be read and written together through the **vectorized APIs** of `isaacsim.core.experimental.prims`. Instead of processing them one at a time in a loop, you can fetch and apply the data of all objects (or a subset) at once as tensors, which stays efficient even with many environments.

The following example gets the world poses of all cubes in the scene and lifts them up by 1.5 units in one operation:

```python
# import the vectorized API for Xform prims
import numpy as np
from isaacsim.core.experimental.prims import XformPrim

# create a wrapper matching all 4 cubes with a regex expression
boxes = XformPrim("/World/Cube_.*")

# get the world poses of all cubes
#   - positions has shape (4, 3): X, Y, Z translation
#   - orientations has shape (4, 4): W, X, Y, Z quaternion
positions, orientations = boxes.get_world_poses()
positions = positions.numpy()
orientations = orientations.numpy()

# raise the Z coordinate by 1.5
positions[:, 2] += 1.5
# apply the new positions
boxes.set_world_poses(positions, orientations)
```

!!! note "What changed from the old API (XFormPrimView)"
    Tutorials for Isaac Sim 5.x used `XFormPrimView` from `isaacsim.core.prims` and specified paths with a **wildcard** (`/World/Cube_*`). With `isaacsim.core.experimental.prims.XformPrim` in 6.0, paths are specified as a **regular expression** (`/World/Cube_.*`). Also, `get_world_poses()` returns Warp arrays, so convert them with `.numpy()` before manipulating them with NumPy.

## Step 5: Physics Replication

If you pass `replicate_physics=True` when cloning, the physics is **replicated directly inside PhysX** instead of copying the USD physics properties, which makes physics parsing faster. This is especially effective for reinforcement learning where the number of environments reaches into the thousands.

Using this feature requires additional parameters:

- `base_env_path` — the path of the prim that is the common ancestor of all clones
- `root_path` — the prefix of each clone's path, up to just before the index

```python
cloner.clone(
    source_prim_path="/World/Ants/Ant_0",
    prim_paths=target_paths,
    positions=position_offsets,
    replicate_physics=True,
    base_env_path="/World/Ants",
    root_path="/World/Ants/Ant_",
)
```

!!! note "When the parameters can be omitted"
    If you have already called `define_base_env()` and `generate_paths()`, the Cloner already has the necessary information, so `base_env_path` and `root_path` can be omitted. Note that when using this feature, the paths of all clones must have the form "prefix + sequential index".

    A complete sample is available at `standalone_examples/api/isaacsim.core.cloner/cloner_ants.py`.

!!! warning "Limitations of physics replication"
    On prims created with physics replication, **shape properties cannot be modified at runtime**. Do not enable `replicate_physics` in scenes where you want to randomize or modify materials, friction, restitution, and the like at runtime.

## Step 6: copy_from_source

The Cloner has one more important option, `copy_from_source`:

```python
cloner.clone(
    source_prim_path="/World/Ants/Ant_0",
    prim_paths=target_paths,
    positions=position_offsets,
    replicate_physics=True,
    base_env_path="/World/Ants",
    root_path="/World/Ants/Ant_",
    copy_from_source=True,
)
```

| Setting | What each clone is | Characteristics |
|---|---|---|
| `copy_from_source=False` (default) | A [USD Inherits](https://openusd.org/release/api/class_usd_inherits.html) of the source prim | Cloning is **fast**. However, changes made to the source prim after cloning **propagate to all clones** |
| `copy_from_source=True` | An independent copy of the source prim | Each clone becomes an independent entity, unaffected by changes to the source. Useful when you want per-environment customizations |

## Summary

This tutorial covered the following topics:

1. Duplicating environments and specifying positions with **Cloner**
2. Automatic grid placement with **GridCloner**
3. Vectorized access to the clones with **XformPrim** (`isaacsim.core.experimental.prims`)
4. Speedups with **physics replication** and its limitations
5. Choosing between inheritance and independent copies with **copy_from_source**

## Next Steps

- [Tutorial 3: Instanceable Assets](03_instanceable_assets.md) - Learn how to build instanceable assets that keep the memory consumption of massively cloned environments in check.
