---
title: ROS 2 Custom C++ OmniGraph Node
---

# ROS 2 Custom C++ OmniGraph Node

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! warning
    Supported only on Linux with ROS 2 Humble.

## Learning Objectives

Build an extension containing custom C++ OmniGraph nodes that publish ROS 2 messages via the **rcl** C API.

## Steps

1. **Custom message** — build `tutorial_interfaces` per the official "Creating custom msg and srv files" tutorial (up to step 6). Message: `geometry_msgs/Point center` + `float64 radius`.
2. **Kit Extension Template C++** — clone [kit-extension-template-cpp](https://github.com/NVIDIA-Omniverse/kit-extension-template-cpp), checkout `release/107.3.0`, `./build.sh`. Extract the sample `omni.example.cpp.omnigraph_node_ros` extension into `source/extensions`, add `system_ros` (e.g. `/opt/ros/humble`) and `additional_ros_workspace` (your `install/tutorial_interfaces`) dependencies to `deps/kit-sdk-deps.packman.xml` with full paths, and rebuild.
3. **Add to Isaac Sim** — source only the workspace's `install/local_setup.bash` (NOT the ROS 2 installation — Python 3.10 vs 3.11 symbol conflicts), launch Isaac Sim, add the built `exts` path under Extension Search Paths, enable **Custom ROS2 OGN Example Extension**. A missing `libtutorial_interfaces__rosidl_typesupport_c.so` error means the workspace isn't sourced.
4. **Run** — build a graph with On Playback Tick → **ROS 2 Publish Custom Message** and **ROS 2 Publish String**; after Play, `ros2 topic list` shows `/custom_node/my_string` and `/custom_node/sphere_msg`.

The `premake5.lua` wires ROS includes/libs (rosidl_runtime_c, rcl, rmw, std_msgs/geometry_msgs/tutorial_interfaces typesupport); in the C++ node, `compute()` creates the node/publisher on first execution and publishes each tick.

## Next Steps

- [Tutorial 28: ROS 2 Launch](28_launch.md)
