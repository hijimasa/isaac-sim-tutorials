---
title: Data Generation with MobilityGen
---

# Data Generation with MobilityGen

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

**MobilityGen** collects mobile-robot data by separating recording from rendering: record lightweight trajectories (teleop or automated scenarios), then replay them to render RGB / segmentation / depth / normals. Supports differential drive (Jetbot, Carter), quadruped (Spot), and humanoid (H1); keyboard/gamepad teleop plus random accelerations and random path following.

## Workflow

1. **Occupancy map** — for `warehouse_multiple_shelves.usd`: Origin (2, 0, 0), Upper (10, 20, 2), Lower (-14, -18, 0.1); Calculate → Visualize (Rotate 180, ROS YAML) → save `~/MobilityGenData/maps/warehouse_multiple_shelves/map.yaml` (change the image line to `map.png`) and `map.png`.
2. **Record** — enable the **MobilityGen UI** extension, set Stage URL and map.yaml, pick **H1Robot** + **KeyboardTeleoperationScenario**, Build, drive with WASD, Start/Stop recording (→ `~/MobilityGenData/recordings`).
3. **Replay & render**:

    ```bash
    ./python.sh standalone_examples/replicator/mobility_gen/replay_directory.py --render_interval 40 --enable isaacsim.replicator.mobility_gen.examples
    ```

    Flags: --rgb_enabled, --segmentation_enabled, --depth_enabled, --instance_id_segmentation_enabled, --normals_enabled, --render_rt_subframes, --render_interval. Output in `~/MobilityGenData/replays`; visualize with the MobilityGen repo's Gradio script.

**Procedural data**: choose RandomPathFollowingScenario (auto-drives and auto-splits recordings; still press Start recording). **Custom robots**: subclass `MobilityGenRobot` (or `WheeledMobilityGenRobot`) in the extension's `robots.py`, implement `build()` and `write_action()`, register with `ROBOT.register()` — keep an external copy of the file.

This completes the Synthetic Data Generation series.
