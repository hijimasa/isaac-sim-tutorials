---
title: Add Camera and Sensors
---

# Add Camera and Sensors

## Learning Objectives

After completing this tutorial, you will have learned:

- How to create a camera and configure its position
- How to inspect camera output using Camera Inspector
- How to attach a camera to a robot
- How to display camera feed in dual viewports

## Getting Started

### Prerequisites

- Complete [Tutorial 3: Articulate a Basic Robot](03_articulate_robot.md) before starting this tutorial.

### Estimated Time

Approximately 10-15 minutes.

### Overview

In this tutorial, you will learn how to create camera sensors in Isaac Sim and attach them to a robot. You will adjust camera positioning, inspect camera output, and secure the camera to the robot body.

## Adding a Camera

1. Select **Create > Camera** to create a camera.

2. Configure the camera transform (position and rotation).

## Inspecting the Camera

1. Open **Tools > Robotics > Camera Inspector**.

2. Select the camera from the dropdown and verify the camera feed.

    ![Camera Inspector](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_camera_widget.png)

## Attaching the Camera to the Robot

1. Rename the camera to `car_camera`.

2. Open a second viewport and set one viewport to the camera view.

3. Drag and drop the camera prim under the robot body.

4. Adjust the transform:
    - **Translation**: `(-6, 0, 2.2)`
    - **Orientation**: `(0, -80, -90)`

5. Press the **PLAY** button and verify the camera feed in the dual viewports.

!!! tip "Best Practice"
    Affix the camera to its parent prim with the correct offset rather than moving the camera directly, to avoid accidental position changes.

## Summary

This tutorial covered the following topics:

1. Creating and positioning a **camera**
2. Inspecting output using **Camera Inspector**
3. **Attaching a camera** to a robot
4. Displaying feed in **dual viewports**

## Next Steps

Proceed to the next tutorial, "[Rig a Mobile Robot](05_rig_mobile_robot.md)", to learn how to convert a real robot asset into a fully articulated mobile robot.
