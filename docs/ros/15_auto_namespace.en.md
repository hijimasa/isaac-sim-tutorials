---
title: Automatic ROS 2 Namespace Generation
---

# Automatic ROS 2 Namespace Generation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Configure assets so every ROS 2 OmniGraph node's namespace is generated automatically — essential for multi-robot simulations. Namespaces can also be set manually per node via `nodeNamespace`; the recommended way is the `isaac:namespace` prim attribute.

## How Namespaces Are Generated

The namespace is built by concatenating every `isaac:namespace` value along the prim hierarchy down to each publisher. The search path depends on the node type:

| Node type | Path used |
|---|---|
| TF nodes | only the **top-level** namespace value (all TFs of one robot live under `robot1/tf`) |
| Camera / Lidar helper nodes | the **sensor prim's** location (helper location irrelevant) |
| All other nodes | the **OmniGraph node's** location |

## Hands-on

Build a mock robot (`/mock_robot/base_link` with lidar_link, camera_link, wheel_left/right — see the Japanese page for the script), add an Example Rotary 2D lidar and a Hawk stereo camera (the new prim is named `hawk_v1_1_nominal`; rename it to `Hawk`), then create Generic/TF/Camera×2/RTX-Lidar publishers via the menu shortcuts, placing each graph under the corresponding link.

Add `isaac:namespace` (Property window **Add > Isaac > Namespace**) to lidar_link, camera_link, Hawk, Hawk/left, Hawk/right, wheel_left with values equal to the prim names. After Play, `ros2 topic list` shows e.g. `/camera_link/Hawk/left/rgb`, `/lidar_link/laser_scan`, `/wheel_left/tf`, `/wheel_left/topic`.

Then add `isaac:namespace = mock_robot` to `/mock_robot`, **Duplicate** the robot, change the copy's attribute to `mock_robot_01`, and observe both robots' topics fully namespaced (`/mock_robot/...`, `/mock_robot_01/...`) — a one-attribute change per robot.

## Next Steps

- [Tutorial 16: Running a Reinforcement Learning Policy through ROS 2](16_rl_controller.md)
