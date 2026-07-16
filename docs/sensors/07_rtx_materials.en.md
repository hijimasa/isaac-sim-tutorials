---
title: RTX Sensor Non-Visual Materials
---

# RTX Sensor Non-Visual Materials

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The `omni.sensors.nv.materials` extension renders materials visible in **non-visual spectra** for RTX sensors ("non-visual materials"). They are specified via **USD attributes**; `isaacsim.sensors.rtx` provides APIs to set them on Material prims. The renderer computes a **material ID** from the attribute combination, exposed through the `GenericModelOutput` AOV and annotators.

## Specifying attributes

- **UI**: right-click a material in the Stage window > **Add > Attribute**, then populate the custom non-visual attributes.
- **Python**: `isaacsim.sensors.rtx` APIs — see `standalone_examples/api/isaacsim.sensors.rtx/specify_non_visual_materials.py`.
- **Visualize**: **RTX - Real-Time > Debug View > Non-Visual Material ID** shows each material ID as a color.

## CSV mapping (deprecated)

Mapping visual materials to sensor materials via CSV is **deprecated as of Isaac Sim 5.1** (USD attributes are now the default). The legacy system had 21 sensor material types (`Default`, `AsphaltStandard`, ... `MetalSilver`, plus `INVALID`=31), configured via `--/rtx/materialDb/rtSensorNameToIdMap` and `kit/rendering-data/runtime/RtxSensorMaterialMap.csv` (partial prim name → sensor material type, lowercase, with `Material` appended). Debug with `rtx.materialDb.rtSensorMaterialLogs=true`.
