---
title: ROS 2 Bridge in Standalone Workflow
---

# ROS 2 Bridge in Standalone Workflow

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Run standalone ROS 2 Python examples and manually step ROS 2 components.

## Manually Stepping ROS2 Components

Connect an **OnImpulseEvent** node to any ROS 2 node to control publish timing precisely. The sample builds a clock publisher with a ROS2 Context on Domain ID 1 (`useDomainIDEnvVar` disabled) via `og.Controller.edit(...)`, then ticks it once per impulse:

```python
og.Controller.set(og.Controller.attribute("/ActionGraph/OnImpulseEvent.state:enableImpulse"), True)
```

Because rendering/physics steps are explicitly controlled, wall-clock speed differs from the GUI — use the simulation clock as reference.

## Examples

All run from the Isaac Sim directory; exit with CTRL-C:

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/clock.py            # /sim_time, /manual_time
./python.sh standalone_examples/api/isaacsim.ros2.bridge/camera_periodic.py  # rates via Simulation Gate steps
./python.sh standalone_examples/api/isaacsim.ros2.bridge/camera_manual.py    # rates via Branch nodes
./python.sh standalone_examples/api/isaacsim.ros2.bridge/carter_stereo.py
./python.sh standalone_examples/api/isaacsim.ros2.bridge/carter_multiple_robot_navigation.py --environment hospital  # or office
./python.sh standalone_examples/api/isaacsim.ros2.bridge/moveit.py
./python.sh standalone_examples/api/isaacsim.ros2.bridge/subscriber.py       # then: ros2 topic pub -r 1 /move_cube std_msgs/msg/Empty
```

Camera samples publish camera info every frame, RGB every 5 frames, depth every 60. Visualize with `rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/camera_manual.rviz` (for depth display issues use rqt_image_view) or `carter_stereo.rviz` (Stop/Play if images don't appear).

## Next Steps

- [Tutorial 18: ROS 2 Navigation](18_navigation.md)
