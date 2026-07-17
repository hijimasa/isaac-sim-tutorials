---
title: Import URDF from a ROS 2 Node
---

# Import URDF from a ROS 2 Node

## Learning Objectives

After completing this tutorial, you will have learned:

- How to import a robot description published by a ROS 2 node (`robot_state_publisher`) directly into Isaac Sim
- How to import XACRO files without explicitly converting them to URDF
- How to switch to another robot and re-import

## Getting Started

### Prerequisites

- Complete [Tutorial 1: Import URDF](01_import_urdf.md).
- ROS 2 is installed (installing ROS may require root or sudo access).
- A ROS 2 workspace with a robot description package (for example [Universal Robots ROS 2 Description](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description)).

### Estimated Time

Approximately 10 minutes.

### Overview

Importing a URDF through a ROS 2 node lets you integrate Isaac Sim directly with your existing ROS 2 workflow. Because it reads the robot description published by `robot_state_publisher`, a major benefit is that **XACRO files** (the ROS format that generates URDF from macros and parameters) **can be imported indirectly without an explicit conversion to URDF**.

!!! warning "Supported platforms"
    This feature is supported **only on Isaac Sim on Linux** (it may work in other Omniverse applications, but this is not guaranteed).

## Step 1: Launch the Robot Description Node

**Terminal 1** — source your ROS 2 environment and launch a node that publishes the robot description:

```bash
source /opt/ros/humble/setup.bash
# also source your workspace's setup.bash
ros2 launch ur_description view_ur.launch.py ur_type:=ur10e
```

**Terminal 2** — check the name of the node you just launched:

```bash
source /opt/ros/humble/setup.bash
ros2 node list
# e.g. /robot_state_publisher is listed
```

## Step 2: Import from Isaac Sim

**Terminal 3** — start Isaac Sim and import:

1. Source the ROS 2 environment, then start Isaac Sim.
2. Install and enable the `isaacsim.ros2.urdf` extension.
3. Open the **File > Import from ROS 2 URDF Node** menu.
4. Enter the node name (e.g. `robot_state_publisher`) in the text box.
5. Click the **Find Node** button to find the node.
6. Define an output directory.
7. Click **Import**.

!!! note "If you do not define an output directory"
    If no output directory is defined, the USD is written to a system temp directory and a warning with the output path is logged. Always specify an output directory if you want to control where the file is saved.

!!! note "ROS 2 Bridge required"
    This feature is only available when the ROS 2 Bridge (`isaacsim.ros2.bridge`) is enabled. See [ROS 2 Setup](../ros/00_setup.md) for setting up the ROS 2 environment.

## Step 3: Extra — Switch to Another Robot and Re-import

1. Stop the publisher in Terminal 1 and restart it with another robot (e.g. `ros2 launch ur_description view_ur.launch.py ur_type:=ur3`).
2. Click the **Find Node** button in Isaac Sim.
3. Change the output directory and click **Import**.

!!! note "The old Kit command `URDFImportFromROS2Node` is deprecated"
    In Isaac Sim 6.0, the Kit command `URDFImportFromROS2Node` used to drive this feature from scripts is **deprecated**. To achieve the same programmatically, the recommended approach is to fetch the robot description with `RobotDefinitionReader` and import it with `URDFImporter`.

## Summary

This tutorial covered the following topics:

1. **Direct import into Isaac Sim** of a robot description (XACRO capable) published by `robot_state_publisher`
2. Node lookup with **Find Node** and specifying the output directory
3. Switching to another robot and re-importing

## Next Steps

- [Tutorial 2: Export URDF](02_export_urdf.md) - Learn how to convert USD to URDF.
- [ROS 2 Tutorials](../ros/index.md) - Dive deeper into Isaac Sim and ROS 2 integration.
