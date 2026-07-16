---
title: RTX Sensor Annotators
---

# RTX Sensor Annotators

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The `isaacsim.sensors.rtx` extension uses Omniverse Replicator to provide **Annotators** for RTX Lidar/Radar data collection. Attach them to render products (on `OmniLidar`/`OmniRadar` prims) either via the Replicator API (`rep.AnnotatorRegistry.get_annotator(...).attach([render_product.path])`) or via the `LidarRtx` class (`sensor.attach_annotator(...)` + `sensor.get_current_frame()`).

!!! warning
    Annotators rely on the simulation timeline — no data is collected while paused/stopped. Step with `omni.kit.app.get_app().update()`, not `orchestrator.step()`. The `GenericModelOutput` AOV must be on-device (`--/app/sensors/nv/lidar|radar/outputBufferOnGPU`).

## Key annotators

- **`IsaacCreateRTXLidarScanBuffer`**: accumulates frames into a single scan. Outputs a 3D Cartesian point cloud (`data`), plus optional `azimuth`, `elevation`, `distance`, `intensity`, `timestamp`, `emitterId`, `materialId`, `objectId`, `normal`, `velocity` (enabled via `initialize(...)` flags; some require specific `omni:sensor:Core:auxOutputType` levels).
- **`IsaacComputeRTXLidarFlatScan`**: extracts depth/azimuth from a 2D scan (no Radar, no 3D Lidar support).
- **`IsaacExtractRTXSensorPointCloudNoAccumulator`**: per-frame Cartesian point cloud extraction (no accumulation).

## GenericModelOutput & Object IDs

Read the buffer via the `isaacsim.sensors.rtx.generic_model_output` module (example: `inspect_lidar_metadata.py`). With `--/rtx-transient/stableIds/enabled=true`, `objectId` gives stable 128-bit IDs mapping to prim paths for semantic segmentation. Resolve via `LidarRtx.decode_stable_id_mapping` and `LidarRtx.get_object_ids` (example: `resolve_object_ids_from_gmo.py`).

## Deprecated annotators

As of Isaac Sim 5.0, several 4.5 annotators (`RtxSensorCpu/Gpu...PointCloud`, `IsaacComputeRTXLidarFlatScanSimulation/SystemTime`, `IsaacReadRTXLidarData`) were removed in favor of `IsaacExtractRTXSensorPointCloudNoAccumulator`, `IsaacComputeRTXLidarFlatScan`, and the `read_gmo_data` utility.
