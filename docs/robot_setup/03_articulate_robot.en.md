---
title: Articulate a Basic Robot
---

# Articulate a Basic Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to organize the stage tree hierarchy
- How to create joints between rigid bodies
- How to configure joint drives (drive properties)
- How to build efficient physics simulations by adding articulations
- How to control robot movement using the Articulation Velocity Controller

## Getting Started

### Prerequisites

- Complete [Tutorial 2: Assemble a Simple Robot](02_assemble_robot.md) before starting this tutorial.

!!! tip "Starting from a Checkpoint Asset"
    If you have not completed the previous tutorial, you can start from this tutorial by loading the `mock_robot_no_joints` asset from the **Samples > Rigging > MockRobot** folder in the **Content** tab at the bottom right of the screen. When loading, open it as a **File (not as a reference)**. Since this tutorial makes direct changes to the asset, it must be opened as a file rather than a reference.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will connect the robot body and wheels assembled in the previous tutorial using **joints**, configure **articulations** to create a functioning robot, and finally add a **velocity controller** to learn how to control the robot during simulation.

## Adding Joints

Joints are mechanisms for physically connecting two rigid bodies. Here we use **Revolute Joints** to enable wheel rotation.

### Creating a Scope for Joints

First, create a Scope to organize and store the joints.

1. Right-click **World** (or **mock_robot** if using the `mock_robot_no_joints` asset) in the stage tree and select **Create > Scope**.
2. Rename the created Scope to **Joints**.

### Creating the Left Wheel Joint

1. Select the **body** Xform in the stage tree, then hold **Ctrl** and select the **wheel_left** Xform.

    !!! note "Selection order matters"
        The first selected object becomes **Body 0** (parent: fixed side), and the second selected object becomes **Body 1** (child: rotating side). Always select the body first, then the wheel.

2. Right-click and select **Create > Physics > Joints > Revolute Joint**.
3. Right-click the **RevoluteJoint** added to the stage tree, select **Rename**, and rename it to **wheel_joint_left**.
4. Verify the following in the **Property** tab:
    - **Body 0**: The body Xform's path is set
    - **Body 1**: The wheel_left Xform's path is set

### Configuring the Joint Rotation Axis

Configure the joint axis so that the wheels rotate in the correct direction. Since there is a 90-degree transformation difference between the body and the cylinder, the Local Rotation needs to be adjusted.

1. With **wheel_joint_left** selected, check the **Property** tab.
2. Set **Local Rotation 0** as follows:
    - **X**: `0.0`, **Y**: `0.0`, **Z**: `0.0`
3. Set **Local Rotation 1** as follows:
    - **X**: `-90.0`, **Y**: `0.0`, **Z**: `0.0`
4. Change **Axis** to **Y**.

### Creating the Right Wheel Joint

Create the right wheel joint following the same procedure as the left wheel.

1. Select the **body** Xform in the stage tree, then hold **Ctrl** and select the **wheel_right** Xform.
2. Right-click and select **Create > Physics > Joints > Revolute Joint**.
3. Rename it to **wheel_joint_right**.
4. Configure **Local Rotation** and **Axis** the same way as the left wheel.

### Organizing the Joints

1. Drag and drop the created **wheel_joint_left** and **wheel_joint_right** into the **Joints** Scope created earlier to organize them.

    ![Joint configuration](images/08_add_joints.png)

## Adding Joint Drives

Joint drives provide driving force to joints. Here we add drives to control the wheels by **angular velocity (rotation speed)**.

1. Select both **wheel_joint_left** and **wheel_joint_right** in the stage tree while holding the **Ctrl** key.
2. Click the **+ Add** button in the **Property** tab.
3. Select **Physics > Angular Drive**.
4. In the added **Angular Drive** section, set the following parameters:
    - **Damping**: `1e4` (10000)
    - **Target Velocity**: `200` (deg/s)

!!! note "Difference between Damping and Stiffness"
    - Setting **Damping** enables **velocity control**. Driving force is applied toward the target velocity.
    - Setting **Stiffness** enables **position control**. Driving force is applied toward the target angle.
    - For continuous rotation like wheels, use **Damping** and keep Stiffness at `0`.

![Joint drives](images/09_apply_angular_drive.webp)

## Adding Articulation

**Articulation** is a mechanism for treating multiple rigid bodies and joints as a single robot unit. Configuring this significantly improves simulation accuracy and performance.

1. Select **World** (or **mock_robot** if using the `mock_robot_no_joints` asset) (the parent Xform of the entire robot) in the stage tree.
2. Click the **+ Add** button in the **Property** tab.
3. Select **Physics > Articulation Root**.

!!! note "Effects of Articulation Root"
    Setting an Articulation Root converts the connected rigid bodies and joints into an efficient articulation structure. This provides the following benefits:

    - **Improved simulation accuracy**: Fewer joint errors occur
    - **Better mass ratio handling**: Stable simulation even for robots with large mass ratios
    - **Improved computational efficiency**: Physics calculations are processed more efficiently

![Articulation](images/10_add_articulation_root.png)

## Adding a Controller

Finally, add a **Velocity Controller** to control robot movement during simulation.

### Creating a Scope for the Controller

1. Right-click **World** (or **mock_robot** if using the `mock_robot_no_joints` asset) in the stage tree and select **Create > Scope**.
2. Rename the created Scope to **Graphs**.

### Adding the Velocity Controller

1. Select **Tools > Robotics > Omnigraph Controllers > Joint Velocity** from the menu bar.
2. When the dialog appears, configure the following:
    - **Robot Prim**: Click **+ Add** and select the Prim with the Articulation Root API (**World**, or **mock_robot** if using the `mock_robot_no_joints` asset).
    - **Graph Path**: Enter `/World/Graphs/Velocity_Controller` (or `mock_robot/Graphs/Velocity_Controller` if using the `mock_robot_no_joints` asset).
3. Click **OK** to create the controller.

![Adding the graph](images/11_add_graph.png)

### Testing in Simulation

1. Press **Play** to start the simulation.
2. Select **JointCommandArray** inside **Graphs > velocity_controller** in the stage tree.
3. Change the **input0** and **input1** values displayed in the **Property** tab to verify that you can independently control the speed of the left and right wheels.

!!! warning "Note about units"
    The controller uses **radians (rad/s)**, but USD drive properties display angles in **degrees**. Be aware of this difference when setting velocity and position values.

![Controller](images/12_test_controller.webp)

## Summary

This tutorial covered the following topics:

1. Organizing the stage tree hierarchy using **Scope**
2. Connecting the body and wheels with **Revolute Joints**
3. Configuring angular velocity control with **Angular Drive**
4. Improving simulation accuracy and performance by adding an **Articulation Root**
5. Controlling robot movement with **Velocity Controller**

!!! tip "Reference Asset"
    The completed robot is similar to the `mock_robot_rigged` asset found in the **Samples > Rigging > MockRobot** folder in the Content tab at the bottom right of the screen.

## Next Steps

Proceed to the next tutorial, "[Add Camera and Sensors](04_camera_sensors.md)", to learn how to attach camera sensors to a robot.
