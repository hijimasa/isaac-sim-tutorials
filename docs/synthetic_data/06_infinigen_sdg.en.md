---
title: Environment Based SDG with Infinigen
---

# Environment Based Synthetic Dataset Generation with Infinigen

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Use procedurally generated [Infinigen](https://infinigen.org/) indoor environments as SDG backdrops: prepare them with colliders, spawn labeled assets and distractors on a working area (dining table), capture floating and physics-settled scenarios with multiple cameras and multiple writers, and cycle environments until the target capture count.

## Workflow

1. Install Infinigen and generate rooms per the Hello Room guide (loop over seeds), then export to USD (`-f usdc --omniverse`).
2. Run:

    ```bash
    ./python.sh standalone_examples/replicator/infinigen/infinigen_sdg.py   # --config for custom YAML/JSON
    ```

3. Config groups: environments (folders/files), capture (total_captures, num_floating/num_dropped captures per env, num_cameras, resolution, rt_subframes, path_tracing, camera offsets/distances, num_scene_lights), writers (multiple writers with kwargs), labeled_assets (auto_label via regex from filenames, or manual_label; per-asset gravity_disabled_chance), distractors (shape/mesh), debug_mode (hides ceilings).
4. Pipeline: load env → add colliders, find working area, spawn assets → create cameras/render products → attach writers → register randomizers (poses, scene lights, dome light, distractor colors; manually triggered) → short overlap-resolving sim → floating captures → longer settle sim → dropped captures → next environment.

## Next Steps

- [Tutorial 7: Randomization in Simulation – AMR Navigation](07_amr_navigation.md)
