---
title: Troubleshooting
---

# Troubleshooting

Common issues and solutions when using Isaac Sim.

## Difficulty Entering Numeric Values

### Symptom

Double-clicking a numeric field in the Property panel may not reliably switch to direct input mode.

### Solution

**Hold `Ctrl` and click** the field to reliably enter numeric input mode.

| Action | Behavior |
|--------|----------|
| Double-click | May activate slider mode instead |
| `Ctrl` + Click | Reliably enters numeric input mode |

## Screen Flickering

### Symptom

The viewport rendering flickers or the display becomes unstable.

### Solution

Adjusting the ray tracing settings in **Render Settings** may resolve this issue.

1. Open **Window > Render Settings** from the menu bar.
2. Expand the **Ray Tracing** section.
3. Set the **NVIDIA DLSS** **Mode** to **Auto**.

!!! tip
    DLSS (Deep Learning Super Sampling) is NVIDIA's AI-based upscaling technology. Setting the Mode to Auto allows the system to automatically select the optimal settings based on GPU load, improving rendering stability.

![DLSS Settings](images/01_dlss_setting.png)

## Switching Coordinate Systems (Global / Local)

### Symptom

When moving or rotating objects, the gizmo (arrow and ring handles) is displayed in world coordinates, making it difficult to operate along the object's local axes. Conversely, you may want to switch back from local to global coordinate mode.

### Solution

Toggle the **Transform Space** setting in the toolbar at the top of the viewport.

1. In the toolbar above the viewport, locate the dropdown near the Move / Rotate / Scale tools.
2. Select one of the following:

| Mode | Description |
|------|-------------|
| **World** | The gizmo is aligned to the world (global) coordinate system. Operations follow the scene's axis directions. |
| **Local** | The gizmo is aligned to the object's local coordinate system. Operations follow the object's own axis directions. |

!!! tip
    Use **Local** mode when you need to operate along an object's own axes, such as adjusting robot joint angles. Use **World** mode for intuitive scene-level positioning.
