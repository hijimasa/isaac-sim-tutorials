---
title: Replicator Overview
---

# Replicator Overview

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Get an overview of the Isaac Sim Replicator tooling for synthetic data generation (SDG), largely provided by the [omni.replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html) extension. The Synthetic Data Generation Layout enables the relevant UI panels.

## Tools

- **Semantics Schema Editor** (Tools > Replicator > Semantics Schema Editor) — view/add/edit/remove semantic labels on prims; labeling is required for annotators like segmentation or bounding boxes.
- **Synthetic Data Visualizer** — visualize sensor outputs directly in the viewport via the visualizer icon (Cross Correspondence needs a special two-camera setup).
- **Synthetic Data Recorder** (Tools > Replicator > Synthetic Data Recorder) — GUI recording built on BasicWriter; see [Tutorial 2](02_recorder.md).
- **Replicator YAML** (Tools > Replicator > Replicator YAML) — config-file-based SDG pipelines converted into OmniGraph workflows.
- **Getting Started Scripts** — script-based starting points covering annotators, writers, and randomizers; see [Tutorial 3](03_getting_started_scripts.md).

![Semantics Schema Editor](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_gui_semantics_editor_window.jpg)

## Next Steps

- [Tutorial 2: Synthetic Data Recorder](02_recorder.md)
