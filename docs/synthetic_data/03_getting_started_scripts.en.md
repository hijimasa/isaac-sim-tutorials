---
title: Getting Started Scripts
---

# Getting Started Scripts

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and complete code.

## Learning Objectives

Script-based Replicator SDG workflows, runnable asynchronously in the Script Editor (`step_async`/`await`) or synchronously as standalone apps (`./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_0N.py`).

## Setup Essentials

- `rep.orchestrator.step(rt_subframes=-1, pause_timeline=True, delta_time=None, wait_for_render=True)` triggers capture; randomizations are bound to custom events instead.
- Disable capture-on-play: `rep.orchestrator.set_capture_on_play(False)`.
- Raise `rt_subframes` against ghosting/unloaded materials; set DLSS Quality mode: `carb.settings.get_settings().set("/rtx/post/dlss/execMode", 2)` (Performance mode causes edge artifacts below ~600×600).
- `wait_for_render=False` decouples capture from rendering for higher throughput (data may lag one frame); write-to-fabric mode (`/exts/omni.replicator.core/enableWriteToFabric`) bypasses USD→Fabric sync for faster randomization (changes are not persisted to the stage).
- Custom-event randomizers: `with rep.trigger.on_custom_event(event_name=...)` + `rep.utils.send_og_event(event_name=...)`.
- Wait for writers before exit: `rep.orchestrator.wait_until_complete()`.

## Examples

1. **BasicWriter** (`sdg_getting_started_01.py`) — world/dome light/cube built with `rep.functional.create`, semantics via `rep.functional.modify.semantics`, a `DiskBackend` initialized and passed to BasicWriter (`writer.initialize(backend=backend, rgb=True, bounding_box_2d_tight=True)`), three `step()` captures.
2. **Custom writer & annotators, multiple cameras** (`_02.py`) — a custom `Writer` subclass reading camera_params + bounding_box_3d, rgb annotators accessed directly via `get_data()`, and a PoseWriter attached to two render products (top + perspective cameras created with `rep.functional.create.camera`).
3. **Custom randomizations** (`_03.py`) — dome-light color via a custom-event Replicator graph (triggered every other step), cube location via `rep.functional.modify.position`; capture with `step(rt_subframes=32)`.
4. **Event-triggered capture in simulation** (`_04.py`) — cube and sphere with rigid bodies via `rep.functional.physics.apply_rigid_body`, poses read through `isaacsim.core.experimental.prims.RigidPrim`; capture whenever the cube drops 0.5 m, using `step(delta_time=0.0)` to capture the same simulation state multiple times (once with the cube hidden).
5. **Batch randomization & performance** (`_05.py`) — 100 cubes via `rep.functional.create_batch.cube` randomized in batch with `ReplicatorRNG`; compares default, `wait_for_render=False`, and write-to-fabric configurations with per-step timings.

![BasicWriter output](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_external_getting_started_01.jpg)

## Next Steps

- Back to the [Synthetic Data index](index.md). Scene-based and object-based SDG tutorials are planned next.
