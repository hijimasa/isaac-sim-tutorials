---
title: Modular Behavior Scripting
---

# Modular Behavior Scripting

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

The `isaacsim.replicator.behavior` extension packages randomizers as **behavior scripts** (Python Scripting Components) attached to prims: reusable, shareable, persistent with the USD, and configurable through **variables exposed as USD attributes** (namespace `exposedVar:<behaviorNamespace>:<attrName>`, edited via an auto-generated Property-panel UI from `isaacsim.replicator.behavior.ui`). The core extension has no UI dependency (headless-capable); core and UI communicate via the carb event `isaacsim.replicator.behavior.EXPOSED_VARS_CHANGED`. Attaching scripts from the Property panel requires enabling `omni.behavior.scripting.ui`. Scripts live under `/exts/isaacsim.replicator.behavior/.../behaviors/*`.

## Built-in Behaviors

- **Location Randomizer** — position within min/max bounds; relative frame option; includeChildren; interval.
- **Rotation Randomizer** — Euler-angle ranges per axis.
- **Look At Behavior** — face a fixed location or target prim (targetPrimPath wins), with upAxis control — camera tracking, sensor aiming.
- **Light Randomizer** — color and intensity ranges over prims with UsdLux.LightAPI.
- **Texture Randomizer** — random textures from asset arrays / CSV with scale, rotation, and UV-projection probability.
- **Volume Stack Randomizer** — physics-based stacking, **custom-event driven** (event:input/output, assets, numRange, dropHeight, renderSimulation, preserveSimulationState); reset → setup → run → completion-event flow enables chaining and external orchestration.

Timeline-based behaviors respond to on_init/on_play/on_update/on_stop/on_destroy; event-based behaviors decouple from the timeline. Templates (`example_behavior.py`, `base_behavior.py`, `example_custom_event_behavior.py`) provide starting points for custom behaviors.

The final example combines volume stacking, texture/light randomization, and a look-at camera into a Script Editor SDG pipeline, assigning a per-behavior `seed` exposed variable for reproducible randomization.

## Next Steps

- [Tutorial 13: Randomization Snippets](13_isaac_randomizers.md)
