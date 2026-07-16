---
title: Randomization in Simulation – UR10 Palletizing
---

# Randomization in Simulation – UR10 Palletizing

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Extend the running UR10 palletizing demo to trigger SDG at specific events **without changing the simulation's outcome**: annotator-based manual writing vs writer-based implicit writing, multi-rate randomization graphs, on-the-fly graph/render-product creation and destruction, and render-mode switching.

## Scenario

Two capture events, monitored via timeline ticks + overlap checks around the active bin:

- **Bin flip** (bin on the flipping helper): PathTracing render mode; data taken directly from rgb + instance segmentation annotators via `get_data()` and saved with helper functions; lights randomized from a color palette (`rep.distribution.choice`), camera cycled through predefined positions (`rep.distribution.sequence`), both `on_frame()`.
- **Bin on pallet**: BasicWriter; original materials cached and restored afterwards; bin material colors randomized every frame, pallet textures (`rep.randomizer.texture`) and camera poses every 4 frames (`on_frame(interval=4)`).

Both scenarios dispatch a delayed preview command so graphs are fully built before `step_async`, then destroy render products and graphs and resume the timeline. Run from the Script Editor (full code on the official page; adjust `NUM_CAPTURES`).

## Next Steps

- [Tutorial 9: Cosmos Synthetic Data Generation](09_cosmos.md)
