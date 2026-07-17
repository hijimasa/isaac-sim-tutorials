---
title: Environment Based SDG with Infinigen
---

# Environment Based Synthetic Dataset Generation with Infinigen

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Use procedurally generated [Infinigen](https://infinigen.org/) indoor environments as SDG backdrops: prepare them with colliders, spawn labeled assets and distractors on a working area (dining table), capture floating and physics-settled scenarios with multiple cameras and multiple writers, and cycle environments until the target capture count.

## Workflow

1. Install Infinigen and generate rooms per the Hello Room guide (loop over seeds; the scene generation step is only tested on Linux), then export to USD via `infinigen.tools.export` (`-f usdc --omniverse`).
2. Run:

    ```bash
    ./python.sh standalone_examples/replicator/infinigen/infinigen_sdg.py   # --config for custom YAML/JSON
    ```

3. Config groups: environments (folders/files), capture (total_captures, num_floating/num_dropped captures per env, num_cameras, resolution, rt_subframes, path_tracing, camera offsets/distances, num_scene_lights), writers (multiple writers with kwargs; BasicWriter, DataVisualizationWriter, PoseWriter, custom), labeled_assets (auto_label via regex from filenames, or manual_label; per-asset gravity_disabled_chance), distractors (shape/mesh), physics (gpu_collision_stack_size, default 300 MB to avoid PhysX `collisionStackSize` buffer overflows in collider-heavy Infinigen scenes), debug_mode (hides ceilings).
4. Pipeline: load labeled assets once up front (`load_auto_labeled_assets` / `load_manual_labeled_assets`, returning floating and falling lists) → configure PhysX GPU memory (`configure_physics_scene`) → load env with colliders, find working area, randomize poses with explicit ranges → create cameras via `rep.functional.create.camera` under a `/Cameras` scope → attach writers → randomize scene lights; dome light and distractor colors as graph randomizers fired via `rep.utils.send_og_event` → short overlap-resolving sim → floating captures (polar angles 0-75°) → ~200-frame settle sim without rendering → dropped captures (0-45°) → next environment; final cleanup waits for writes then detaches writers and destroys render products.

## Next Steps

- [Tutorial 7: Randomization in Simulation – AMR Navigation](07_amr_navigation.md)
