---
title: Assemble a Simple Robot
---

# Assemble a Simple Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add and manipulate basic shapes on the stage
- How to enable physics properties on objects
- How to examine collision properties
- How to edit physics properties such as friction
- How to edit material properties such as color and reflectivity

## Getting Started

### Prerequisites

- Complete [Tutorial 1: Stage Setup](01_stage_setup.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In this tutorial, you will use GUI operations to build the basic structure of a simple two-wheeled robot using primitive shapes (cubes, cylinders). You will create the robot body and two wheels, then learn how to configure physics properties, examine collision meshes, and apply materials.

## Preparation

1. Create a new **Stage** from the menu bar via **File > New**.
2. Generate a ground plane via **Create > Physics > Ground Plane** from the menu bar.

## Adding Objects to the Scene

### Creating the Robot Body

1. Right-click on the stage and select **Create > Xform**.
2. Right-click the created Xform and select **Rename**, then rename it to **body**.
3. In the Property panel, set **Transform > Translate** to **(0, 0, 1)**.
4. Click **Create > Shape > Cube** from the menu bar to create a cube.
5. In the Property panel, set **Transform > Translate** to **(0, 0, 1)**.
6. In the Property panel, set **Transform > Scale** to **(2, 1, 0.5)**.
7. Drag and drop the cube into the **body** Xform to make it a child element.

   ![Creating the robot body](images/03_make_robot_body.png)

### Creating the Wheels

1. Right-click on the stage and select **Create > Xform**. In the Property panel, set **Translate** to **(0, 1.5, 1)** and **Orient** to **(90, 0, 0)**.
2. Rename it to **wheel_left**.
3. Right-click **wheel_left** on the stage, then click **Create > Shape > Cylinder** to create a cylinder.
4. Scroll down to the **Geometry** section in the Property panel.
5. Change **Radius** to **0.5** and **Height** to **1.0**.
7. Rename the cylinder to **wheel_left**.
8. Right-click the **wheel_left** Xform and select **Duplicate**.
9. Move the duplicated wheel's **Translate** y value to **-1.5**.
10. Rename the duplicated Xform to **wheel_right**.
11. Rename the duplicated cylinder to **wheel_right**.

    ![Creating the wheels](images/04_make_robot_wheel.png)

## Adding Physics Properties

### Applying Rigid Body Physics

1. Select the cube and both cylinders using **Ctrl+Shift** or **Shift** keys.
2. Click the **+ Add** button in the **Property** tab.
3. Select **Physics > Rigid Body with Colliders Preset**.
4. Press **Play** to verify that the objects fall to the ground.

!!! note "About Rigid Body with Colliders Preset"
    Selecting "Rigid Body with Colliders Preset" automatically applies both the **Rigid Body API** (gravity and simulation dynamics) and the **Collision API** (collision detection).

![Applying Rigid Body](images/05_adding_rigid_body_and_collider.webp)

### Examining Collision Meshes

1. Click the ![Eye icon](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_eyecon.png) at the top of the viewport.
2. Select **Show By Type > Physics > Colliders > All**.
3. Purple outlines appear around static objects with the Collision API applied (in this case, the ground plane). Green outlines appear around dynamic objects (in this case, the cube and two cylinders).

    ![Collision](images/06_show_colliders.png)

### Adding Contact and Friction Parameters

1. From the menu bar, click **Create > Physics > Physics Material**.
2. Select **Rigid Body Material** in the popup.
3. Tune parameters such as friction coefficients and restitution in the Property tab.
4. Select an object in the stage tree.
5. Find **physics materials on selected models** in the **Property > Physics** tab.
6. Select the desired material from the dropdown menu to assign it.

    ![Materials](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_materials.png)

## Setting Material Properties

### Creating and Assigning Visual Materials

1. Click **Create > Materials > OmniPBR** from the menu bar three times to create three materials.
2. Right-click the newly created materials and rename them to **ground**, **body**, and **wheel** respectively.
3. Select the **body** material and change the **Albedo Color** to **RGB: (0.1, 1.0, 0.1)** in the **Material and Shader / Albedo** section of the **Property** tab.
4. Adjust reflectivity, roughness, and other properties as needed.
5. Select the **wheel** material and change the **Albedo Color** to **RGB: (0.1, 0.1, 1.0)** in the **Material and Shader / Albedo** section of the **Property** tab.
6. Adjust reflectivity, roughness, and other properties as needed.
7. Select the **GroundPlane** Xform and assign the **ground** material from **Materials on selected models** in the **Property** tab.
8. Select the **body** Xform and assign the **body** material from **Materials on selected models** in the **Property** tab.
9. Select the **wheel_left** Xform and assign the **wheel** material from **Materials on selected models** in the **Property** tab.
9. Select the **wheel_right** Xform and assign the **wheel** material from **Materials on selected models** in the **Property** tab.
10. Verify that color changes appear on the corresponding robot parts.

    ![Applying visual materials](images/07_apply_visual_materials.png)

## Summary

This tutorial covered the following topics:

1. Building a robot structure using **primitive shapes** (Cube, Cylinder)
2. Configuring physics with **Rigid Body with Colliders Preset**
3. Visualizing and examining **collision meshes**
4. Setting friction and restitution with **Physics Material**
5. Configuring visual appearance with **OmniPBR materials**

!!! tip "Reference Asset"
    The completed robot is similar to the `mock_robot_no_joints` asset found in the **Samples > Rigging > MockRobot** folder in the Content tab at the bottom right of the screen.

## Next Steps

Proceed to the next tutorial, "[Articulate a Basic Robot](03_articulate_robot.md)", to learn how to configure joints and articulations.
