---
title: Scene Based Synthetic Dataset Generation
---

# Scene Based Synthetic Dataset Generation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Generate offline datasets in a realistic warehouse scene: config files (YAML/JSON), custom environments, Isaac Sim API asset spawning, randomized physics simulation, Replicator randomization graphs, cameras/render products, and writers.

## Scenario

A forklift is randomly placed; a pallet is placed in front of it; boxes are scattered on the pallet with `scatter_2d(check_for_collisions=True)` each frame; a traffic cone is placed at a random bottom corner of the forklift's OBB; a short physics simulation drops boxes on a rear pallet. Three cameras (top view, randomized pallet view, driver view) feed BasicWriter (rgb, semantic_segmentation, bounding_box_3d) into `_out_scene_based_sdg`.

## Running

```bash
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py
# with custom config (basic/default/kitti/coco writer examples in scene_based_sdg/config/*)
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py \
    --config standalone_examples/replicator/scene_based_sdg/config/config_kitti_writer.yaml
```

KittiWriter/CocoWriter output plugs directly into KITTI/COCO-based training pipelines (e.g. TAO Toolkit with Detectnet V2).

## Key Implementation Points

- Create `SimulationApp` before importing omni modules; load the stage with `open_stage(assets_root_path + url)`.
- Render products are disabled until SDG starts; the driver camera is wrapped via `rep.get.prim_at_path` for graph randomization.
- One-shot placement uses the Isaac Sim API (`prims.create_prim` + transform math); per-frame randomization uses registered Replicator graphs (`rep.randomizer.register`): scattered boxes + materials, cone placement via `rep.distribution.sequence` on OBB corners, and light randomization above the combined AABB. Triggers can be per-frame, per-interval, or manual.

## Next Steps

- [Tutorial 5: Object Based Synthetic Dataset Generation](05_object_based_sdg.md)
