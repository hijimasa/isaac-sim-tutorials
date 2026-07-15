---
title: NameOverride Attribute
---

# NameOverride Attribute

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Use the `isaac:nameOverride` prim attribute to publish custom joint/link names over ROS without renaming prims.

## Setting up the Attribute

With the joint-state scene from [Tutorial 12](12_manipulation.md):

1. Select a joint prim; if **Name Override** is absent in Raw USD Properties, click **Add > Isaac > NameOverride**.
2. Enter a custom name, press Play, and `ros2 topic echo /joint_states` shows the custom name.

**Publishers** (ROS2 Publish Transform Tree / Joint State) automatically use the override. **Subscribers** need the **Isaac Joint Name Resolver** node (Target Prim / Robot Path = `/panda`) inserted in the pipeline so custom names in incoming commands resolve to actual prim paths for the Articulation Controller.

![NameOverride subscriber pipeline](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_isaac_nameoverride_attr.png)

## Next Steps

- [Tutorial 14: ROS 2 Ackermann Controller](14_ackermann.md)
