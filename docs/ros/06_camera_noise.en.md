---
title: Add Noise to Camera
---

# Add Noise to Camera

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Add an augmentation to the sensor pipeline
- Publish image data with noise added

## Running the Example

With your ROS 2 environment sourced (and internal-library env vars set for the standalone workflow):

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/camera_noise.py
```

Open `rviz2`, add an **Image** display, and set the topic to `/rgb_augmented` — a noisy version of the Isaac Sim view appears.

![Noisy camera](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_ros_tut_gui_ros2_camera_noise.gif)

## Code Overview

1. Set the camera on the render product: `set_camera_prim_path(render_product_path, CAMERA_STAGE_PATH)`.
2. Define a noise kernel — options: C++/Python OmniGraph node, omni.warp kernel (GPU), or numpy (CPU). The sample provides `image_gaussian_noise_warp` and `image_gaussian_noise_np`.
3. Register an augmented annotator composing the standard `rgb` annotator with `rep.annotators.Augmentation.from_function(...)` as `rgb_gaussian_noise`.
4. Register a writer `CustomROS2PublishImage` (node type `isaacsim.ros2.bridge.ROS2PublishImage`) using that annotator plus the simulation-time connection.
5. `writer.initialize(topicName="rgb_augmented", frameId="sim_camera"); writer.attach([render_product_path])`.

The `seed` argument is a predefined Replicator Augmentation option; None or < 0 derives a repeatable unique seed from Replicator's global seed.

## Next Steps

- [Tutorial 7: Publishing Camera's Data](07_camera_publishing.md)
