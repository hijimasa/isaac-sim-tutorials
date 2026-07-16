---
title: Cosmos Synthetic Data Generation
---

# Cosmos Synthetic Data Generation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Use the **CosmosWriter** to capture synchronized multi-modal data (RGB, depth, instance/semantic segmentation, shaded segmentation, Canny edges) from a Carter Nova navigating a warehouse — ground truth for **Cosmos Transfer**, which turns control signals into high-quality visual simulations via Multi-ControlNet (control branches: vis / edge / depth / seg, each weighted 0.0–1.0).

## Running

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/cosmos_writer_warehouse.py
```

Key parameters: NUM_CLIPS, NUM_FRAMES_PER_CLIP, CAPTURE_INTERVAL, START_DELAY. The render product uses the robot's front camera at 1280×720; `pause_timeline=False` keeps the robot moving during capture. Output is organized into clips of consecutive frames.

## Advanced

- Two segmentation modes: instance ID (default) or semantic (requires semantic annotations); custom label→color mapping for consistent classes across datasets.
- Tunable Canny low/high thresholds (typically 10–200).
- With Cosmos Transfer: weights above 1.0 total are normalized; prompt single scenes richly (no camera instructions); faces are auto-blurred by Cosmos Guardrail.

## Next Steps

- [Tutorial 10: Data Augmentation](10_augmentation.md)
