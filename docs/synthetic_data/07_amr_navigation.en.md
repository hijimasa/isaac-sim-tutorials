---
title: Randomization in Simulation – AMR Navigation
---

# Randomization in Simulation – AMR Navigation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Capture data from a driving robot's viewpoint: a Nova Carter with an OmniGraph navigation stack (no collision avoidance) drives toward a randomized dolly; when close enough, SDG captures LdrColor from both stereo cameras, then the scene re-randomizes. The background environment switches every `env_interval` captures.

## Running

```bash
./python.sh standalone_examples/replicator/amr_navigation.py --use_temp_rp --num_frames 9 --env_interval 3
```

`--use_temp_rp` creates render products only for capture frames (major speedup); default output `_out_nav_sdg_demo`.

## NavSDGDemo Structure

The demo class tracks the Carter chassis/nav target, dolly, randomized dolly light, props, cycled env URLs, a timeline subscription as the feedback loop, and a per-capture randomized trigger distance. `start` builds the scene; `_on_timeline_event` checks the Carter–dolly distance, pauses, unsubscribes, and triggers SDG (sync standalone / async Script Editor). Randomizers: `_randomize_dolly_pose` (min distance from Carter; nav target follows), `_randomize_dolly_light`, `_randomize_prop_poses` (props dropped above the dolly). `_setup_next_frame` re-randomizes, cycles the environment on interval, and restarts the timeline; on completion it waits via `rep.orchestrator.wait_until_complete`.

## Next Steps

- [Tutorial 8: Randomization in Simulation – UR10 Palletizing](08_ur10_palletizing.md)
