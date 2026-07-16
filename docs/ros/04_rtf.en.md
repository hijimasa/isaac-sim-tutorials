---
title: ROS 2 Publish RTF
---

# ROS 2 Publish Real Time Factor (RTF)

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Publish Isaac Sim's Real Time Factor as a ROS 2 Float32 message.

RTF = simulated elapsed time / real elapsed time, computed per frame. RTF > 1 means simulation runs faster than wall clock; RTF < 1 means slower.

## Publish RTF

1. **Tools > Robotics > ROS 2 OmniGraphs > Generic Publisher**, select **Publish RTF as Float32**, click OK.
2. An Action Graph is generated with **Isaac Real Time Factor** connected to a generic **ROS2 Publisher** (std_msgs/msg/Float32). Inspect it via right-click **Open Graph** on `/Graph/ROS_GenericPub`.
3. Press **Play**, then:

    ```bash
    ros2 topic echo /topic
    ```

For an unloaded system, RTF should be close to 1.0.

![RTF graph](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_rtf_graph.png)

## Next Steps

- [Tutorial 5: ROS 2 Cameras](05_camera.md)
