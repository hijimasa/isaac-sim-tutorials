---
title: Actor Simulation and Synthetic Data Generation (IRA)
---

# Actor Simulation and Synthetic Data Generation (IRA)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The **Isaacsim.Replicator.Agent (IRA)** extension generates synthetic data of **human characters and robots** across 3D environments, with control over environment, cameras, characters, and robot motion via config and command files. Characters and robots are collectively called *agents/actors*. IRA is beta and builds on `omni.anim.graph`, `omni.anim.navigation`, and `omni.replicator.core`.

## What you will learn

- **Enable**: Extension Manager → `isaacsim.replicator.agent.core` + `.ui`. UI at `Tools > Action and Event Data Generation > Actor SDG`.
- **Quick start**: load a config (default at `.../isaacsim.replicator.agent.core-[version]/config/default_config.yaml`) → **Set Up Simulation** → **Generate Random Commands** + save → **Start Data Generation**.
- **Config file** sections: `global` (seed, simulation_length @30 FPS), `scene` (asset_path), `sensor` (camera_num or camera_list), `character` (num, asset_path, command_file, filters, spawn/navigation areas), `robot` (nova_carter_num, iw_hub, write_data), `response`, `incident`, `replicator` (writer + parameters). Minimum config is just the header + `version`.
- **Data generation**: UI (edit fields, save before running; NavMesh required, disable Auto-Bake for speed) or script (`./python.sh tools/actor_sdg/sdg_scheduler.py -c <config>`, `--save_usd` to export the set-up USD).

!!! warning
    Camera count is bounded by VRAM; reduce `camera_num` on CUDA memory errors. Raise the file-descriptor limit on "Too many open files".
