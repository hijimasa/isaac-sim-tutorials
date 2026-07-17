---
title: Synthetic Data Generation Tutorials
---

# Synthetic Data Generation Tutorials

<span class="badge badge-intermediate">Intermediate</span>

Tutorials for generating synthetic datasets, centered on Replicator.

## Overview

Synthetic data generation (SDG) produces labeled training data directly from simulation: Isaac Sim's **Replicator** (omni.replicator) renders images together with accurate annotations (bounding boxes, segmentation, depth, …) and applies domain randomization for better real-world generalization.

## Tutorials

### Basics and Getting Started

!!! example "[Tutorial 1: Replicator Overview](01_replicator_overview.md)"
    The Replicator tool family: semantics labeling, visualization, recorder, YAML workflow.

!!! example "[Tutorial 2: Synthetic Data Recorder](02_recorder.md)"
    GUI-based recording, custom writers, the DataVisualizationWriter, and randomized cameras.

!!! example "[Tutorial 3: Getting Started Scripts](03_getting_started_scripts.md)"
    Script-based SDG essentials (capture on play, step, RTSubframes, DLSS, wait_for_render, write-to-fabric) and five worked examples.

### SDG Tutorials

!!! example "[Tutorial 4: Scene Based SDG](04_scene_based_sdg.md)"
    Warehouse scene randomization with KITTI/COCO output.

!!! example "[Tutorial 5: Object Based SDG](05_object_based_sdg.md)"
    Object-centric pipeline for pose estimation (DOPE/CenterPose).

!!! example "[Tutorial 6: Environment Based SDG with Infinigen](06_infinigen_sdg.md)"
    Procedurally generated indoor environments with multiple writers.

!!! example "[Tutorial 7: Randomization in Simulation – AMR Navigation](07_amr_navigation.md)"
    Proximity-triggered captures from a navigating Nova Carter.

!!! example "[Tutorial 8: Randomization in Simulation – UR10 Palletizing](08_ur10_palletizing.md)"
    Event-triggered SDG that leaves the running simulation untouched.

!!! example "[Tutorial 9: Cosmos Synthetic Data Generation](09_cosmos.md)"
    Multi-modal CosmosWriter data for Cosmos Transfer.

### Customization Tools and Techniques

!!! example "[Tutorial 10: Data Augmentation](10_augmentation.md)"
    warp/NumPy augmentation of annotator and writer data.

!!! example "[Tutorial 11: Custom Replicator Randomization Nodes](11_custom_og_randomizer.md)"
    From Python functions to OmniGraph nodes to ReplicatorItems.

!!! example "[Tutorial 12: Modular Behavior Scripting](12_modular_scripting.md)"
    Prim-attached, reusable behavior-script randomizers.

!!! example "[Tutorial 13: Randomization Snippets](13_isaac_randomizers.md)"
    Lights, textures, chained randomization, volume filling, SimReady assets.

!!! example "[Tutorial 14: Useful Snippets](14_isaac_snippets.md)"
    Multi-camera access, custom events, motion blur, custom FPS.

### Other Data Generation Tools

!!! example "[Tutorial 15: Grasping Synthetic Data Generation](15_grasping_sdg.md)"
    Antipodal sampling and physics-based grasp evaluation.

!!! example "[Tutorial 16: Data Generation with MobilityGen](16_mobility_gen.md)"
    Record-then-render data collection for mobile robots.

### Action and Event Data Generation

- [Tutorial 17: Actor Simulation and SDG (IRA)](17_replicator_agent.md)
- [Tutorial 18: Object Simulation and SDG (IRO)](18_replicator_object.md)
- [Tutorial 19: VLM Scene Captioning (IRC)](19_replicator_caption.md)
- [Tutorial 20: Physical Space Event Generation (IRI)](20_replicator_incident.md)
- [Tutorial 21: RTX Sensors Placement and Calibration (ISP)](21_sensors_rtx_placement.md)
