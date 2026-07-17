---
title: Actor Simulation and Synthetic Data Generation (IRA)
---

# Actor Simulation and Synthetic Data Generation (IRA)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The **Omni.Metropolis.Pipeline (OMP)**, **Isaacsim.Replicator.Agent (IRA)**, and **Isaacsim.Anim.Robot.Core (IAR)** extensions together generate synthetic data of **human characters and robots** across 3D environments, controlling actor behaviors, environments, and sensors through a single YAML configuration file (codeless). Characters and robots are collectively called *agents/actors*. The framework builds on `omni.anim.behavior`, `omni.anim.navigation`, and `omni.replicator.core`.

!!! warning "Breaking changes from IRA 0.x"
    IRA 1.x (Isaac Sim 6.0+) is a complete architectural redesign: external command files (.txt), the `response`/`event`/`incident` sections, and the `filters` field are removed; behaviors are defined inline in YAML (routines/triggers); configs are validated with Pydantic v2; actor configs persist as USD schemas/prims. See the [official migration guide](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/ext_isaacsim_replicator_agent_migration_guide.html).

## What you will learn

- **Enable**: Extension Manager → `Omni.Metropolis.Pipeline`, `Isaacsim.Anim.Robot.Core`, `isaacsim.replicator.agent.core` + `.ui`. UI at `Tools > Action and Event Data Generation > Actor SDG`.
- **UI workflow (two clicks)**: `minimal.yaml` auto-loads (samples under `.../isaacsim.replicator.agent.core-[version]/data/sample_configs/`; use `full_pipeline.yaml` for an end-to-end demo) → **Set Up Simulation** (fully reloads the scene from the config; NavMesh required) → **Start Data Generation** (runs for **Simulation Duration** in seconds). Output defaults to `~/IRA_output` (Linux) / `%USERPROFILE%\IRA_output` (Windows).
- **Config file** top-level sections: root `version` (1.x.x), `seed`, `simulation_duration` (seconds); `environment` (`base_stage_asset_path` required, `prop_asset_paths`); `character`/`robot`/`sensor` with **named groups** (characters: `asset_path`, `spawn_areas`, `semantic_labels`, inline `routines`, `triggers`, `colliders`; robots: `config_file_path` to an IAR config such as `nova_carter.yaml`, `camera_prim_paths`; sensors: `aim_at_targets` or `maximum_coverage` placement strategies, `num: -1` auto-calculates); `replicator.writers` dict supporting multiple concurrent writers (`IRABasicWriter`, `CosmosIRAWriter`, `SceneGraphWriter`, `CustomWriter`) with per-writer `start_frame`/`end_frame` and `sensor_prim_list`.
- **Actor behaviors**: a routine-trigger loop — weighted `wander`/`patrol`/`stop` (characters) and `wander`/`patrol`/`halt` (robots) routines interrupted by `event_trigger`/`time_trigger`/`collision_trigger` with priority queuing; per-actor deterministic seeds; configs embedded as `IRACharacterAPI`/`AnimRobotAPI` USD schemas. Experimental **behavior tree** groups (`behavior_tree` + `overrides`, JSON trees) are an alternative to routines/triggers (triggers unsupported there).
- **Script / API**: `./python.sh tools/actor_sdg/actor_sdg.py -c <config>` (replaces `sdg_scheduler.py`), or the Python API `isaacsim.replicator.agent.core.api` (`load_config_file`, `setup_simulation`, `start_data_generation_async`).

!!! warning
    Camera count is bounded by VRAM; reduce sensor group sizes on CUDA memory errors. Raise the file-descriptor limit on "Too many open files".
