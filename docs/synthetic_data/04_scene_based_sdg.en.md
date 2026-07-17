---
title: Scene Based Synthetic Dataset Generation
---

# Scene Based Synthetic Dataset Generation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Generate offline datasets in a realistic warehouse scene: config files (YAML/JSON), custom environments, Isaac Sim API asset spawning, randomized physics simulation, Replicator randomization graphs, cameras/render products, and writers.

## Scenario

A forklift is randomly placed; a pallet is placed in front of it; boxes are scattered on the pallet with `scatter_2d(check_for_collisions=True)` each frame; a traffic cone is placed at a random bottom corner of the forklift's OBB; a short physics simulation drops boxes on a rear pallet. Three cameras (top view, randomized pallet view, driver view) feed BasicWriter through a configurable backend (default: `DiskBackend`; annotators rgb, bounding_box_2d_tight, semantic_segmentation, distance_to_image_plane, bounding_box_3d, occlusion) into `_out_scene_based_sdg`. Config files now take `backend_type`/`backend_params` keys (KITTI/COCO configs use `backend_type: null`); the default renderer is `RealTimePathTracing` with `rt_subframes: 32`, `num_frames: 10`.

## Running

```bash
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py
# with custom config (basic/default/kitti/coco writer examples in scene_based_sdg/config/*)
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py \
    --config standalone_examples/replicator/scene_based_sdg/config/config_kitti_writer.yaml
```

KittiWriter/CocoWriter output plugs directly into KITTI/COCO-based training pipelines (e.g. TAO Toolkit with Detectnet V2).

## Key Implementation Points

- Create `SimulationApp` before importing omni modules; load the stage with `stage_opened, _ = open_stage(assets_root_path + url)`; seed randomization with `rep.set_global_seed(42)` and `np.random.default_rng(42)`.
- Cameras are created with `rep.functional.create.camera` under an `/SDG/Cameras` scope; render products are disabled until SDG starts; a `setup_writer(config)` helper initializes the writer with optional backend support.
- One-shot placement uses `define_prim` + `add_reference_to_stage` + `add_labels` + `XformPrim` from `isaacsim.core.experimental`; per-frame randomization mixes direct `rep.functional` calls (`rep.functional.randomizer.scatter_2d`, `rep.functional.modify.pose` for cameras) with graph randomizers for box materials and sphere lights registered via `rep.trigger.on_custom_event` and fired with `rep.utils.send_og_event`.
- The pre-SDG physics drop uses `SimulationManager` with experimental `GeomPrim`/`RigidPrim` classes; cleanup waits with `rep.orchestrator.wait_until_complete()` before detaching the writer and destroying render products.

## Next Steps

- [Tutorial 5: Object Based Synthetic Dataset Generation](05_object_based_sdg.md)
