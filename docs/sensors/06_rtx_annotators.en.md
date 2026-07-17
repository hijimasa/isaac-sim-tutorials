---
title: RTX Sensor Annotators
---

# RTX Sensor Annotators

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The `isaacsim.sensors.experimental.rtx` and `isaacsim.sensors.rtx.nodes` extensions use Omniverse Replicator to provide **Annotators** for RTX Lidar/Radar data collection. The recommended approach is the `LidarSensor` / `RadarSensor` runtime classes, which manage annotators and render products automatically: `sensor = LidarSensor(lidar, annotators=["generic-model-output"])`, then `data, info = sensor.get_data("generic-model-output")` and `parse_generic_model_output_data(data)`.

!!! warning
    Annotators rely on the simulation timeline — no data is collected while paused/stopped. With multi-tick rendering enabled (the default), GMO timestamps respect timeline Play/Pause/Stop, and stepping via `omni.kit.app.get_app().update()` or `orchestrator.step()` both work (the latter is preferred when Writers are attached). With multi-tick disabled, timestamps advance monotonically from "App Ready" independent of the timeline; step with `omni.kit.app.get_app().update()` in that case.

## Active annotator

- **`IsaacExtractRTXSensorPointCloud`** (from `isaacsim.sensors.rtx.nodes`): extracts the GMO buffer's point cloud into a Cartesian (x, y, z) buffer every frame; works with both `OmniLidar` and `OmniRadar` prims and outputs a sensor-to-world transform. Visualize via the `RtxSensorDebugDrawPointCloud` writer, or pass `writers=["draw-point-cloud"]` to `LidarSensor` / `RadarSensor` / `AcousticSensor` (requires `isaacsim.sensors.rtx.nodes` enabled).
- Auxiliary fields (intensity, emitter/material IDs, ...) come through the GMO buffer, gated by `aux_output_level` (`_replicator:rendervar:GenericModelOutput:channels`).

## GenericModelOutput & Object IDs

Read the buffer via `parse_generic_model_output_data` from `isaacsim.sensors.experimental.rtx` (examples: `inspect_lidar_gmo.py --aux-data-level FULL`, `inspect_radar_gmo.py`). With `--/rtx-transient/stableIds/enabled=true`, `objId` gives stable 128-bit IDs mapping to prim paths for semantic segmentation. Resolve via `parse_stable_id_map_data` (example: `resolve_lidar_object_ids.py`). Not every ID has a map entry (procedural geometry, unexpanded submeshes) — use `map.get(id, "<unknown>")` instead of direct lookups.

## Deprecated annotators

As of Isaac Sim 6.0, `IsaacCreateRTXLidarScanBuffer` (accumulated scans; Lidar only; optional outputs `azimuth`, `elevation`, `distance`, `intensity`, `timestamp`, `emitterId`, `channelId`, `materialId`, `tickId`, `hitNormal`, `velocity`, `objectId`, `echoId`, `tickState` gated by `aux_output_level`), `IsaacComputeRTXLidarFlatScan` (2D Lidar depth/azimuth), and `IsaacExtractRTXSensorPointCloudNoAccumulator` ship with the deprecated `isaacsim.sensors.rtx` extension and will be removed; use `IsaacExtractRTXSensorPointCloud` (usually indirectly via `LidarSensor` / `RadarSensor`).
