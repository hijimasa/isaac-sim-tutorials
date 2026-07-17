---
title: ROS 2 Custom C++ OmniGraph Node
---

# ROS 2 Custom C++ OmniGraph Node

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

!!! warning
    Supported only on Linux with ROS 2 Jazzy.

## Learning Objectives

Build an extension containing a custom C++ OmniGraph node that publishes ROS 2 messages via the **rcl** C API.

## Steps

1. **Custom message** — build `tutorial_interfaces` per the official "Creating custom msg and srv files" tutorial (up to step 6). Message (`Sphere.msg`): `geometry_msgs/Point center` + `float64 radius`.
2. **Extension template** — clone and build the [Isaac Sim repository](https://github.com/isaac-sim/IsaacSim) (Quick Start), then create an **Isaac Sim OmniGraph Node Extension** template named `custom.cpp.ros2_node` with `./repo.sh template new`. Add `system_ros` (e.g. `/opt/ros/jazzy`) and `additional_ros_workspace` (your `install/tutorial_interfaces`) dependencies to `deps/kit-sdk-deps.packman.xml` with full paths, and extend `includedirs` / add `libdirs` and `links` in `source/extensions/custom.cpp.ros2_node/premake5.lua` for the ROS 2 C API and message libraries.
3. **Node code** — create `ROS2CustomMessageNode.ogn` (inputs: execIn, publishCenter float[3], publishRadius float) and `ROS2CustomMessageNode.cpp` in `source/extensions/custom.cpp.ros2_node/nodes`, then run `./build.sh`. The built extension lands in `_build/linux-*/release/exts`; errors during the Python stubs generation post-build step can be ignored.
4. **Add to Isaac Sim** — source the ROS 2 installation (`/opt/ros/jazzy/setup.bash`) and the workspace's `install/local_setup.bash`, launch Isaac Sim from that terminal, and enable `custom.cpp.ros2_node` under **Window > Extensions** (for a different Isaac Sim application, add the built `exts` path under Extension Search Paths).
5. **Run** — build a graph with On Playback Tick → **ROS2 Publish Custom Message**; after Play, verify with `ros2 topic list` and `ros2 topic echo /custom_node/sphere_msg`.

In the C++ node, `compute()` creates the node/publisher on first execution and publishes each tick.

## Next Steps

- [Tutorial 28: ROS 2 Launch](28_launch.md)
