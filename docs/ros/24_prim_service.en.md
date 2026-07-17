---
title: ROS 2 Service for Manipulating Prims Attributes
---

# ROS 2 Service for Manipulating Prims Attributes

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Expose stage prims over ROS 2 services with the **ROS2 Service Prim** node. The calling terminal needs the `isaac_ros2_messages` package from the Isaac Sim ROS workspace (Isaac Sim itself ships the service in its internal bridge libraries).

## Services

Four services from `isaac_ros2_messages`: **GetPrims** (paths + types under a path), **GetPrimAttributes** (attribute names/displays/types), **GetPrimAttribute** (value + type as JSON), **SetPrimAttribute** (value as JSON). Numeric containers (Gf.Vec3f, Gf.Matrix4d, Gf.Quatd, …) are read/written as row-first lists of numbers.

## Example

Create a Cube, build the graph with the ROS2 Service Prim node, press Play, then:

```bash
ros2 service list
ros2 service call /get_prims isaac_ros2_messages/srv/GetPrims "{path: /World}"
ros2 service call /get_prim_attributes isaac_ros2_messages/srv/GetPrimAttributes "{path: /World/Cube}"
ros2 service call /get_prim_attribute isaac_ros2_messages/srv/GetPrimAttribute "{path: /World/Cube, attribute: xformOp:translate}"
ros2 service call /set_prim_attribute isaac_ros2_messages/srv/SetPrimAttribute "{path: /World/Cube, attribute: xformOp:translate, value: [1, 2, 3]}"
```

![Prim service graph](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/tutorial_ros2_prim_service.png)

## Next Steps

- [Tutorial 25: ROS 2 Python Custom Messages](25_custom_message.md)
