---
title: ROS 2 Cameras
---

# ROS 2 Cameras

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Add cameras to the scene and robot
- Build camera publishers in OmniGraph (and via the menu shortcut)
- Publish ground-truth synthetic perception data over rostopics

## RGB Publisher Graph

Add two stationary cameras (`Camera_1`, `Camera_2`), open extra viewports via **Window > Viewports > Viewport 2**, then build:

![Camera graph](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros2_camera_graph.png)

| Node | Field | Value |
|---|---|---|
| Isaac Create Render Product | cameraPrim / enabled | /World/Camera_1 / True |
| ROS 2 Camera Helper | type / topicName / frameId | rgb / rgb / turtle |

Key nodes: **Isaac Create Render Product** (acquires rendered data from the camera prim), **Isaac Run One Simulation Frame** (runs pipeline setup once), **ROS 2 Camera Helper** (selects data type and topic). The helper auto-generates a session-only `/Render/PostProcessing/SDGPipeline` graph.

## Other Ground Truth Data

Each Camera Helper publishes one `type`: depth, point cloud, bbox 2D tight/loose, bbox 3D, semantic/instance labels (bounding boxes require `vision_msgs` and semantically annotated scenes). Once activated, a helper's type cannot be changed — use a new node or reload the stage. Sample scene: **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial.usd**.

**Camera Info Helper** computes K/P/R matrices from fx = width·focalLength/horizontalAperture etc.; for monocular cameras Tx = Ty = 0.

## Graph Shortcut

**Tools > Robotics > ROS 2 OmniGraphs > Camera** — set Graph Path, Camera Prim, frameId, check desired outputs; optionally append to an existing graph.

## Verifying

```bash
ros2 topic echo /rgb
ros2 run rqt_image_view rqt_image_view /depth
```

In RViz2 add an **Image** display on topic `rgb`. If depth looks black/white only, limit the field of view so the depth range is bounded.

## Next Steps

- [Tutorial 6: Add Noise to Camera](06_camera_noise.md)
