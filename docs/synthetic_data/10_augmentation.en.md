---
title: Data Augmentation
---

# Data Augmentation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Augment rgb and depth annotator data with warp (GPU) or NumPy (CPU) kernels — warp avoids GPU→CPU copies when data is already on the GPU. A red cube rotates every frame via a Replicator graph; augmentations include channel swapping, HSV+gaussian-noise composition, and depth noise at various sigmas.

## Annotator Augmentation

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/augmentation_annotator.py   # --use_warp --num_frames 25
```

Enable scripting, define NumPy/warp functions, register noise functions in the AnnotatorRegistry, build augmentations from functions or the registry (optionally registering a new augmented annotator), then attach the augmented annotators (1× rgb, 2× depth) to a render product.

## Writer Augmentation

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/augmentation_writer.py      # --use_warp --num_frames 25
```

Replace the writer's built-in rgb annotator with an augmented one using the same `name="rgb"` via `add_annotator` (HSV → gaussian noise → RGB composition); augment `distance_to_camera` with the built-in `augment_annotator`.

Use the annotator path for direct `get_data()` access and custom storage; use the writer path to keep an existing writer pipeline and only transform what gets written.

## Next Steps

- [Tutorial 11: Custom Replicator Randomization Nodes](11_custom_og_randomizer.md)
