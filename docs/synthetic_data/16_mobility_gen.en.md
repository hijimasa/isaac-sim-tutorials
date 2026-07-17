---
title: Data Generation with MobilityGen
---

# Data Generation with MobilityGen

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

**MobilityGen** collects mobile-robot data by separating recording from rendering: record lightweight trajectories (teleop or automated scenarios), then replay them to render RGB / segmentation / depth / normals. Supports differential drive (Jetbot, Carter), quadruped (Spot), and humanoid (H1) — each with a single front-camera configuration (`H1Robot`, ...) or a USD-based multi-sensor rig (`H1MultiSensorRobot`, ...; multi-camera only for now); keyboard/gamepad teleop plus random accelerations and random path following. In Isaac Sim 6.0 the core extension moved to `isaacsim.replicator.experimental.mobility_gen`. Always launch with multi-GPU rendering disabled: `./isaac-sim.sh --/renderer/multiGpu/enabled=false`.

## Workflow

1. **Occupancy map** — for `warehouse_multiple_shelves.usd`: Origin (2, 0, 0), Upper (10, 20, 2), Lower (-14, -18, 0.1); Calculate → Visualize Image → enter `map` in Image File Name, **Update YAML** → **Save YAML** as `~/MobilityGenData/maps/warehouse_multiple_shelves/map.yaml` → **Save Image** as `map.png`.
2. **Record** — enable the **MobilityGen UI** extension, set Stage URL and map.yaml, pick **H1Robot** + **KeyboardTeleoperationScenario**, Build, drive with WASD, Start/Stop recording (→ `~/MobilityGenData/recordings`). Sensor edits are persisted per recording as a lightweight `sensor_overrides.usda` layer and re-applied at replay.
3. **Replay & render**:

    ```bash
    ./python.sh standalone_examples/replicator/mobility_gen/replay_directory.py --input ~/MobilityGenData/recordings --output ~/MobilityGenData/replays --render_interval 40
    ```

    Flags: --rgb_enabled / --depth_enabled / --segmentation_enabled (default True), --normals_enabled / --instance_id_segmentation_enabled (default False), --render_rt_subframes, --render_interval (negate with `--no-<flag>`). Recordings made with Isaac Sim 5.x must be converted first with `migrate_recordings.py` (see the [MobilityGen Recordings migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/mobility_gen_recordings_migration.html)). Output in `~/MobilityGenData/replays`; visualize with the MobilityGen repo's Gradio script.

**Procedural data**: choose RandomPathFollowingScenario (auto-drives and auto-splits recordings; still press Start recording). **Custom robots**: subclass `MobilityGenRobot` (or `WheeledMobilityGenRobot`) in the extension's `robots.py`, implement `build()` and `write_action()`, register with `ROBOTS.register()` — keep an external copy of the file. **NuRec scenes**: reconstructed environments (Particle/Volume USD from the NVIDIA PhysicalAI-Robotics NuRec dataset) can be used as stages directly; RGB is fully supported, depth accuracy is not guaranteed, and semantic segmentation is unsupported (`--no-depth_enabled --no-segmentation_enabled`).

This completes the Synthetic Data Generation series.
