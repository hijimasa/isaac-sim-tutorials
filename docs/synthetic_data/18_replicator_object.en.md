---
title: Object Simulation and Synthetic Data Generation (IRO)
---

# Object Simulation and Synthetic Data Generation (IRO)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

`isaacsim.replicator.object` (IRO) is a **no-code-change** extension generating synthetic data (RGB, 2D/3D bounding boxes, segmentation) for object detection and robotics. It takes a YAML **description file** of a mutable scene and lets non-3D-experts describe domain-randomized scenes compactly via macros.

## What you will learn

- **Pipeline**: acquire USD assets (convert OBJ etc. via asset converter) → compose a description file → generate data → train a CV model (TAO 6.0 example).
- **Run from UI**: Extension Manager → enable `isaacsim.replicator.object`; the **Object Detection SDG** panel appears. Edit `configs/global.yaml` `output_path`, pick `demo_kaleidoscope`, click **Simulate** (replace `PATH_TO_*` placeholders).
- **Run from Docker**: `bash isaac-sim.sh --no-window --enable isaacsim.replicator.object ... --/config/file=<config>` (filter the log by `METROPERF`).
- **Embedded interface**: **Initialize Scene Randomization** then **Randomize Scene** to prototype without writing to disk.
- **Concepts**: description file key/value pairs are **Mutables** (objects randomized per frame), **Harmonizers** (constrain how mutables randomize together), or **Settings** (frame count, output switches, physics). A description walkthrough drops boxes (`physics: rigidbody`, `tracked: true`) onto a table (`physics: collision`) with `distribution_type: range/folder` randomization and `$[/...]` macros.
