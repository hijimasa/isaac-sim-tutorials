---
title: Useful Snippets
---

# Useful Snippets

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough; full code is on the official page.

Replicator data-access and capture-control snippets (standalone paths under `standalone_examples/api/isaacsim.replicator.examples/`):

- **multi_camera.py** — annotator and custom-writer data from multiple cameras.
- **simulation_get_data.py** — RGB / semantic segmentation at specific simulation events.
- **custom_event_and_write.py** — custom events triggering randomization and writing at arbitrary times.
- **motion_blur.py** — motion blur in RTX Real-Time (post-process parameters) and Path Tracing (`pathTracedMotionBlurSubSamples`); handles custom physics FPS so physics-driven assets provide motion samples at arbitrary delta times.
- **subscribers_and_events.py** — stage/physics/render event subscriptions at custom update rates.
- **custom_fps_writer_annotator.py** — trigger writers / read annotators at a custom FPS with rendering disabled when idle. Note: set timeline (stage) FPS **before** creating the Replicator graph — changing it afterwards resets the graph.
- **cosmos_writer_simple.py** — minimal CosmosWriter example (falling box); see [Tutorial 9](09_cosmos.md).

## Next Steps

- [Tutorial 15: Grasping Synthetic Data Generation](15_grasping_sdg.md)
