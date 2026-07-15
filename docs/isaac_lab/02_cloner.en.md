---
title: Getting Started with Cloner
---

# Getting Started with Cloner

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Set up examples using the `Cloner` and `GridCloner` classes
- Access cloned objects with vectorized View APIs
- Understand physics replication and additional cloning parameters

## Getting Started

Enable the **Isaac Sim Cloner** extension (`isaacsim.core.cloner`) via **Window > Extensions**, then open **Window > Script Editor** to run the snippets.

## Introduction to Cloner

```python
from isaacsim.core.cloner import Cloner
from isaacsim.core.utils.stage import get_current_stage
from pxr import UsdGeom
import numpy as np

base_env_path = "/World/Cube_0"
UsdGeom.Cube.Define(get_current_stage(), base_env_path)

cloner = Cloner()
target_paths = cloner.generate_paths("/World/Cube", 4)

cube_positions = np.array([[0, 0, 0], [3, 0, 0], [6, 0, 0], [9, 0, 0]])
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths, positions=cube_positions)
```

Orientations can be specified with an `orientations` argument.

## Grid Cloner

`GridCloner(spacing=3)` places clones in a grid automatically — no precomputed transforms needed.

## Accessing Cloned Objects

```python
from isaacsim.core.prims import XFormPrimView

boxes = XFormPrimView("/World/Cube_*")
positions, orientations = boxes.get_world_poses()
positions[:, 2] += 1.5
boxes.set_world_poses(positions, orientations)
```

## Physics Replication

Pass `replicate_physics=True` (with `base_env_path` and `root_path`) to replicate physics directly in PhysX for faster parsing. Runtime modification of shape properties is not supported on replicated prims — skip this flag if you need runtime randomization of materials/friction/restitution.

## Additional Parameters

By default clones are USD Inherits of the source (fast, but source changes propagate to clones). Set `copy_from_source=True` to make independent copies.

## Next Steps

- [Tutorial 3: Instanceable Assets](03_instanceable_assets.md)
