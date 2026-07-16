---
title: Object Based Synthetic Dataset Generation
---

# Object Based Synthetic Dataset Generation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Object-centric SDG for pose estimation / detection training: labeled assets and distractors float inside an invisible collision-walled working area, captured from multiple randomized cameras, with hybrid Replicator + custom USD randomizers, PathTracing motion blur, and PoseWriter (DOPE / CenterPose formats).

## Running

```bash
./python.sh standalone_examples/replicator/object_based_sdg/object_based_sdg.py
# DOPE / CenterPose config examples in object_based_sdg/config/*
```

## Key Points

- Config covers working_area_size, num_frames/num_cameras, disable_render_products_between_captures, simulation_duration_between_captures, camera properties, writer type/kwargs, labeled assets, shape/mesh distractors.
- Custom randomizers: overlap-triggered bounce velocities, camera poses looking at random labeled assets (with optional camera colliders), velocities pulling objects toward the center; Replicator randomizers for sphere lights and shape distractor colors via custom events.
- Motion blur combines path-traced subframes over a chosen movement duration; render products (optionally including the viewport) can be disabled between captures for headless performance.
- PoseWriter parameters: output_dir, format (dope/centerpose), use_subfolders, write_debug_images, skip_empty_frames.
- Real-world example: **SyntheticaDETR**, trained entirely on Replicator data, tops the BOP YCBV detection leaderboard; assets without CAD models can be captured with the AR Code app (LiDAR + multi-view → USD).

## Next Steps

- [Tutorial 6: Environment Based SDG with Infinigen](06_infinigen_sdg.md)
