---
title: RTX Sensor Non-Visual Materials
---

# RTX Sensor Non-Visual Materials

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The `omni.sensors.nv.materials` extension renders materials visible in **non-visual spectra** for RTX sensors ("non-visual materials"). They are specified via **USD attributes**; the `isaacsim.core.experimental.materials.NonVisualMaterial` class simplifies setting them on Material prims. The renderer computes a **material ID** from the attribute combination, exposed through the `GenericModelOutput` AOV and annotators.

## Specifying attributes

- **UI**: right-click a material in the Stage window > **Add > Attribute**, then populate the custom non-visual attributes.
- **Python**: `isaacsim.core.experimental.materials.NonVisualMaterial` — see `standalone_examples/api/isaacsim.sensors.experimental.rtx/apply_nonvisual_materials.py`.
- **Visualize**: **RTX - Real-Time > Debug View > Non-Visual Material ID** shows each material ID as a color. After modifying non-visual attributes, save and reload the stage for the changes to take effect.

## CSV mapping (removed)

Mapping visual materials to sensor materials via CSV (`RtxSensorMaterialMap.csv` plus the `rtx.materialDb.rtSensorNameToIdMap` / `rtx.materialDb.rtSensorMaterialLogs` carb settings) was deprecated in Isaac Sim 5.1 and is **no longer supported** — those settings and the CSV file are now ignored. Specify non-visual materials via USD attributes (`omni:simready:nonvisual:*`) instead.
