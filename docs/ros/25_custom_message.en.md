---
title: ROS 2 Python Custom Messages
---

# ROS 2 Python Custom Messages

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! warning
    Fully supported on Linux only; not supported on Windows (WSL).

## Learning Objectives

Use custom messages with rclpy inside Isaac Sim. Packages must be built with **Python 3.11** (place your package under `humble_ws/src` or `jazzy_ws/src`, run `./build_ros.sh`, and source before launching Isaac Sim).

The demo uses the `custom_message` package from IsaacSim-ros_workspaces (`custom_message/msg/SampleMsg.msg`):

```text
std_msgs/String my_string
int64 my_num
```

## Script Editor

Launch Isaac Sim from the sourced terminal, then run in the Script Editor:

```python
import rclpy
from custom_message.msg import SampleMsg

sample_msg = SampleMsg()
sample_msg.my_string.data = "hello from Isaac Sim!"
sample_msg.my_num = 23
print("Message assignment completed!")
```

## Standalone Script

Create `ros2_custom_message.py` that starts `SimulationApp`, calls `enable_extension("isaacsim.ros2.bridge")`, then imports and uses the message (full listing on the Japanese page). Run with `./python.sh ros2_custom_message.py` from a terminal with the workspace sourced; verify "Message assignment completed!" is printed.

## Next Steps

- [Tutorial 26: ROS 2 Python Custom OmniGraph Node](26_custom_python_node.md)
