---
title: Object Simulation and Synthetic Data Generation (IRO)
---

# Object Simulation and Synthetic Data Generation (IRO)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

`isaacsim.replicator.object` (IRO) is a **no-code-change** tool generating synthetic data (RGB, 2D/3D bounding boxes, segmentation) for object detection and robotics. It takes a YAML **description file** of a mutable scene and lets non-3D-experts describe domain-randomized scenes compactly via macros. The new **Chat IRO** extension generates IRO description files from plain-English scene descriptions with immediate viewport preview.

## What you will learn

- **Pipeline**: acquire USD assets (convert OBJ etc. via asset converter) → compose a description file → generate data → train a CV model (TAO 6.0 example).
- **Run from UI**: Extension Manager → enable `isaacsim.replicator.object.core` and `isaacsim.replicator.object.ui`; the **Object SDG** panel appears. Configs live under `PATH_TO_CORE_EXTENSION/isaacsim/replicator/object/core/configs`. Edit `global.yaml` `output_path`, pick `demo_kaleidoscope` (or `demo_empty_space.yaml` for empty space detection), click **Simulate** (replace `PATH_TO_*` placeholders).
- **Run from Docker**: `bash isaac-sim.sh --no-window --enable isaacsim.replicator.object.core ... --/config/file=<config>` (filter the log by `METROPERF`).
- **Embedded interface**: **Initialize Scene Randomization** then **Randomize Scene** to prototype without writing to disk (a black viewport between the two clicks is normal; press "F" to focus).
- **Concepts**: description file key/value pairs are **Mutables** (objects randomized per frame), **Harmonizers** (constrain how mutables randomize together), or **Settings** (frame count, output switches, physics). A description walkthrough drops boxes (`physics: rigidbody`, `tracked: true`) onto a table (`physics: collision`) with `distribution_type: range/folder` randomization and `$[/...]` macros. The catalog adds **Force** and **Empty Space Detection** pages in 6.0.
