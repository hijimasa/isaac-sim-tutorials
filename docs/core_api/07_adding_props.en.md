---
title: Adding Props
---

# Adding Props

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add objects (Props) to a scene
- How to configure Rigid Body properties
- How to configure Collider properties
- How to set Mass properties
- How to visualize and customize collision shapes
- How to apply Physics Materials (restitution and friction)

## Getting Started

### Prerequisites

- Complete [Tutorial 1: Hello World](01_hello_world.md) before starting this tutorial.

### Estimated Time

Approximately 10-15 minutes.

### Overview

In the previous tutorials, we used the Python API to add objects and robots to scenes. In this tutorial, we take a different approach and use **GUI operations** to add objects to a scene, then step by step configure the attributes required for physics simulation.

Objects participating in physics simulation in Isaac Sim need the following attributes properly configured:

| Attribute | Role |
|---|---|
| **Rigid Body** | Registers the object as a physics object affected by gravity and external forces |
| **Collider** | Enables collision detection with other objects |
| **Mass** | Sets mass, density, and inertia |
| **Physics Material** | Sets restitution (bounciness) and friction coefficients |

!!! note "Note"
    When using Python API classes like `DynamicCuboid`, these attributes are automatically configured internally. With GUI operations, you need to add each attribute manually.

## Adding a Rubik's Cube

First, create a new stage and place an object.

1. Click **File > New** to create a new stage.<br>
   ![New stage](images/11_new_stage.png)

2. In the Content Browser, navigate to **Isaac Sim > Props > Rubiks_Cube > rubiks_cube.usd** and drag-and-drop the USD file into the viewport.<br>
   ![Place Rubik's Cube](images/12_put_rubiks_cube.webp)

3. Left-click the Rubik's Cube to select it, and set the **Translate** to `(0, 0, 0.1)` in the Properties panel.

4. Right-click on the stage and select **Create > Isaac > Environment > Flat Grid** to create a ground plane.<br>
   ![Create Flat Grid](images/13_create_flat_grid.png)

5. Press the **PLAY** button to start the simulation.

    **Result:** The Rubik's Cube does not fall. Since no **Rigid Body** attribute has been set, the object is not part of the physics simulation.

6. Press the **STOP** button to stop the simulation.

## Configuring Physics Properties

### Adding Rigid Body Properties

1. Right-click the Xform Rubik's Cube on the stage and select **Add > Physics > Rigid Body**.<br>
   ![Add Rigid Body](images/14_add_rigid_body.png)

!!! warning "Warning"
    In the following steps, be careful not to click the Rubik's Cube in the viewport and add attributes to the Mesh node. Attributes must be added to the Xform node, otherwise the simulation will not work correctly.

2. Press the **PLAY** button.

    **Result:** The Rubik's Cube falls but **passes through the ground**. Adding a Rigid Body makes it affected by gravity, but without collision detection it cannot detect contact with the ground.

    ![Rubik's Cube without collision](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_core_add_prop_1.webp)

3. Press the **STOP** button.

### Adding Collision Properties

1. Right-click the Xform Rubik's Cube on the stage and select **Add > Physics > Collider Presets**.

2. Press the **PLAY** button.

    **Result:** The Rubik's Cube now lands on the ground. Collision detection is now enabled thanks to the Collider attribute.

    ![Rubik's Cube with collision](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_core_add_prop_2.webp)

3. Press the **STOP** button.

### Adding Mass

1. Right-click the Xform Rubik's Cube on the stage and select **Add > Physics > Mass**.

2. In the Properties panel, scroll to the **Mass** section and set **Mass** to `0.1` (100 grams).

!!! note "About Mass Settings"
    Setting Mass to `0` causes the simulation to automatically compute mass at runtime based on the object's volume (assuming `1000 kg/m³` density if not explicitly specified). In addition to mass, you can also set **Density**, **Center of Mass**, **Diagonal Inertia**, and **Principal Axes**.

### Visualizing Collision Shapes

Collision shapes are normally invisible, but they can be visualized for debugging.

1. Right-click the **Eye icon** in the top-left of the viewport and select **Show By Type > Physics > Colliders > All**.
   ![Show Colliders setting location](images/15_show_colliders.png)

    **Result:** Collision shapes for all objects in the scene are displayed.

    - The ground (static object) collider is shown in **pink**
    - The Rubik's Cube (dynamic object) collider is shown in **green**

    ![Collision shape visualization](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_core_add_prop_3.png)

!!! tip "Collision Approximation Types"
    You can change the collision shape approximation method. Select the `World/rubiks_cube/RubikCube` mesh, then choose a different approximation type in the **Approximation** tab of the **Physics/Collider** section.

### Customizing the Collision Shape

Let's replace the default collision shape (mesh approximation) with a simpler sphere to simulate rolling behavior.

1. Left-click the `World/rubiks_cube/RubikCube` mesh and press the **×** button in the **Physics/Collider** section to delete the existing collider.

2. With the RubikCube mesh selected, select **Create > Shape > Sphere** to add a sphere shape.

3. In the **Geometry** section, set the **Radius** to `0.07` (sized to match the cube).

4. Select the created sphere and add **Add > Physics > Collider Presets**.

5. Uncheck the eye icon next to the sphere in the stage to hide its visual representation.

6. Select the ground (FlatGrid), click the **Toggle Offset Mode** icon to the right of Transform in the Properties panel, and set **Rotation** to `(10, 0, 0)` (tilting the ground by 10 degrees).

7. Press the **PLAY** button.

    **Result:** The Rubik's Cube rolls down the slope. Due to the sphere collider, the physics simulation treats it as a sphere rather than a box.

    ![Rubik's Cube rolling with sphere collider](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_core_add_prop_4.webp)

8. Press the **STOP** button.

### Adding Physics Materials

Set the restitution to make the object bounce.

1. Left-click the Xform Rubik's Cube on the stage and change the **Translate** to `(0, 0, 1)` in the Properties panel (to drop it from a higher position).

2. Right-click the Xform Rubik's Cube on the stage and select **Create > Physics > Physics Material**. In the popup, check **Rigid Body Material** and click OK. Drag-and-drop the created material into the `World/rubiks_cube/Looks` folder.<br>
   ![Create Physics Material](images/16_create_physics_material.png)

3. In the Properties panel, scroll to the **Physics Material** section and set **Restitution** to `1` (perfectly elastic collision).

4. Select the sphere collider created earlier, and in the **Physics/Physics material on selected Material** section, select `/World/rubiks_cube/Looks/PhysicsMaterial` to apply the physics material.

5. Press the **PLAY** button.

    **Result:** The Rubik's Cube falls to the ground and bounces. Since the Restitution is set to 1, it bounces back with almost no energy loss.

    ![Rubik's Cube with physics material](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_core_add_prop_6.webp)

6. Press the **STOP** button.

!!! note "Friction Settings"
    In addition to restitution, you can also set **Static Friction** and **Dynamic Friction** in the physics material.

!!! tip "Completed Asset"
    The completed asset for this tutorial is available in the Content Browser at **Isaac Sim > Samples > Rigging > RubiksCube > rubiks_cube.usd**.

## Advanced: Building Complex Collision Shapes

In real robotics applications, you may need accurate collisions for complex-shaped objects. In such cases, a common approach is to approximate the shape by combining multiple basic shapes (spheres, cylinders, boxes, etc.).

![Bearing collision approximation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_core_add_prop_5.png)

The figure above shows an example of collision shapes for a bearing. Cylinders and rectangles are combined to approximate the complex shape.

## Summary

This tutorial covered the following topics:

1. **Adding objects** to a scene
2. Configuring physics properties with **Rigid Body**, **Collider**, and **Mass**
3. **Visualizing and customizing** collision shapes
4. Applying **Physics Materials** (restitution and friction)

!!! note "Relationship with Python API"
    The attributes manually configured via GUI in this tutorial are automatically set when using Python API classes like `DynamicCuboid`, `FixedCuboid`, and `DynamicSphere`. Understanding the physics attribute mechanisms through GUI operations makes it easier to comprehend the meaning of each parameter when using the Python API.

## Next Steps

Proceed to the next tutorial, "[Data Logging](08_data_logging.md)", to learn how to record and replay simulation data.
