---
title: Getting Started Scripts
---

# Getting Started Scripts

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and complete code.

## Learning Objectives

Script-based Replicator SDG workflows, runnable asynchronously in the Script Editor (`step_async`/`await`) or synchronously as standalone apps (`./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_0N.py`).

## Setup Essentials

- `rep.orchestrator.step(rt_subframes=-1, pause_timeline=True, delta_time=None)` triggers capture; randomizations are bound to custom events instead.
- Disable capture-on-play: `rep.orchestrator.set_capture_on_play(False)`.
- Raise `rt_subframes` against ghosting/unloaded materials; set DLSS Quality mode: `carb.settings.get_settings().set("/rtx/post/dlss/execMode", 2)` (Performance mode causes edge artifacts below ~600×600).
- Custom-event randomizers: `with rep.trigger.on_custom_event(event_name=...)` + `rep.utils.send_og_event(event_name=...)`.
- Wait for writers before exit: `rep.orchestrator.wait_until_complete()`.

## Examples

1. **BasicWriter** (`sdg_getting_started_01.py`) — cube + dome light, `add_labels()` semantics, render product from the viewport camera, BasicWriter with rgb + bounding_box_2d_tight, three `step()` captures.
2. **Custom writer & annotators, multiple cameras** (`_02.py`) — a custom `Writer` subclass reading camera_params + bounding_box_3d, rgb annotators accessed directly via `get_data()`, and a PoseWriter attached to two render products.
3. **Custom randomizations** (`_03.py`) — dome-light color via a custom-event Replicator graph (triggered every other step), cube location via plain USD API; capture with `step(rt_subframes=32)`.
4. **Event-triggered capture in simulation** (`_04.py`) — cube and sphere fall with rigid-body physics; capture whenever the cube drops 0.5, pausing the timeline and using `step(delta_time=0.0)` to capture the same simulation state multiple times (once with the cube hidden).

![BasicWriter output](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_external_getting_started_01.jpg)

## Next Steps

- Back to the [Synthetic Data index](index.md). Scene-based and object-based SDG tutorials are planned next.
