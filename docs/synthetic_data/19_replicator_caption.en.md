---
title: VLM Scene Captioning (IRC)
---

# VLM Scene Captioning (IRC)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

`Isaacsim.Replicator.Caption.Core` (IRC) generates image-caption pairs for VLM training using Omniverse 3D ground truth, capturing scene descriptions, object relationships, and spatial reasoning. It plugs into [IRO](18_replicator_object.md) and [IRA](17_replicator_agent.md), and can export **scene graphs** (nodes = objects, edges = spatial relationships), organized by a **Support Tree** (floor = level 0, objects on floor = level 1, etc.).

## What you will learn

- **Enable**: Extension Manager → `isaacsim.replicator.caption.core`; UI at `Tools > Action and Event Data Generation > VLM Scene Captioning`. Run via UI, Python API, IRA, or IRO.
- **UI**: Load a stage USD (demo at `.../Samples/Replicator/Captioning/test_caption.usda`), enter LLM API key, pick Brief/Full caption + camera prim path + output path, then **Generate Scene Graph** (also works for a region of interest by aiming a selected camera at it). Default NVIDIA NIM services are free on a trial basis; pick models from the NVIDIA NIM API reference page; local NIM hosting is possible.
- **Python API**: `CaptionAPI` (`isaacsim.replicator.caption.core.api`) — `set_model_params(url, name, key)` (key from `NVIDIA_API_KEY`), `load_config_file()`, async `get_captions()`.
- **Config** (`caption_configs`, config `version: 0.6.6`): `save_full/pruned_scene_graph`, `pruning_ratio` (MST edges kept), `attach_label_to_usd`, `use_ai_label`, `visualize_caption`, `max_object_capacity`, `export_edges`, `export_world`, `global/qa/brief_caption`.
- **In IRA/IRO**: with IRA 1.x, add `SceneGraphWriter` under `replicator.writers` with caption parameters inline (`scene_graph_interval`, `caption_interval`, ...); for IRO use `CombinedIROSceneGraphWriter`/`IROSceneGraphWriter`. Captions are written as `caption/scene_graph_caption_<frame id>.json`. Set the `NVIDIA_API_KEY` env var (not needed for scene-graph-only).
