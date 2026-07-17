---
title: ROS 2 Python Custom OmniGraph Node
---

# ROS 2 Python Custom OmniGraph Node

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and complete code.

## Learning Objectives

Create a custom OmniGraph Python node (via the Isaac Sim VS Code Edition extension template) that subscribes to `/number` (std_msgs/msg/Int32) with rclpy and outputs the Fibonacci number.

## Steps

1. **Template > Extension** in Isaac Sim VS Code Edition: name `custom.python.ros2_node`, check *Ready-to-use extension* and *Omnigraph node*. Add `"isaacsim.ros2.bridge" = {}` to `[dependencies]` in `extension.toml`.
2. Define the node in `OgnCustomPythonRos2NodePy.ogn`: inputs execIn + topic (default `/number`); outputs execOut + fibonacci (uint64).
3. Implement `OgnCustomPythonRos2NodePy.py`: an internal-state class (inheriting `BaseResetNode`) creates the rclpy node/subscription, `spin_once()` pulls messages, and `custom_reset()` destroys them on timeline stop; the node class computes Fibonacci in `compute(db)` and triggers `execOut` when a value arrives.
4. Enable the extension (**Window > Extensions**, search `custom.python.ros2_node`), then build a graph: On Playback Tick → Custom Python ROS 2 Node → To String → Print Text (check *To Screen*).

![Custom node graph](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/tutorial_ros2_custom_omnigraph_node_python_node_graph.png)

Play, then:

```bash
ros2 topic pub -1 /number std_msgs/msg/Int32 "{data: 10}"
```

The Fibonacci value appears in the viewport's top-left corner (fades without new values).

## Next Steps

- [Tutorial 27: ROS 2 Custom C++ OmniGraph Node](27_custom_cpp_node.md)
