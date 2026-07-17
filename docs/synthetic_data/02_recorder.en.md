---
title: Synthetic Data Recorder
---

# Synthetic Data Recorder

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and code.

## Learning Objectives

Record synthetic data from the GUI (Tools > Replicator > Synthetic Data Recorder), including custom writers. Assets must be semantically labeled; the sample stage `Isaac Sim > Samples > Replicator > Stage > full_warehouse_worker_and_anim_cameras.usd` comes pre-labeled with animated cameras.

## UI

- **Writer frame** — *Render Products* (camera path + resolution entries; defaults to the active viewport camera or stage-selected cameras), *Parameters* (BasicWriter annotator checkboxes, or a custom writer with a JSON parameters file), *Output* (working directory, incremented folder names, optional S3), *Config* (save/load the GUI state as JSON).
- **Control frame** — Start/Stop, Pause/Resume, Number of Frames (0 = until stopped), **RTSubframes** (extra subframes per frame — raise it for teleported objects, unloaded materials, or low light), Control Timeline, Verbose.

![Recorder window](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_gui_sd_recorder_window.jpg)

## Custom Writers

Register a custom writer (e.g. `MyCustomWriter` writing rgb/normals) in the Script Editor via `rep.writers.register_writer(...)`, then select it in Parameters with a JSON file. The recorder calls `writer.initialize(backend=..., **parameters)`, so custom writers must accept a `backend` argument (the configured `DiskBackend`/`S3Backend`) or `**kwargs`, and write through that backend (e.g. `self.backend.schedule(F.write_image, path=..., data=...)`). The **DataVisualizationWriter** (`from isaacsim.replicator.writers import DataVisualizationWriter`) overlays bbox 2D tight/loose and 3D annotations on rgb or normals backgrounds.

## Replicator Randomized Cameras

Create a randomized camera before starting the recorder and add it as a render product:

```python
import omni.replicator.core as rep

camera = rep.create.camera()
with rep.trigger.on_frame():
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((-5, 5, 1), (-1, 15, 5)),
            look_at="/Root/Warehouse/SM_CardBoxA_3",
        )
```

## Recording Loop

The recorder drives `rep.orchestrator.step_async(rt_subframes=..., delta_time=None, pause_timeline=False)` per frame, keeping frames synchronized with the stage; the loop works with or without advancing the timeline (dynamic vs static captures).

## Next Steps

- [Tutorial 3: Getting Started Scripts](03_getting_started_scripts.md)
