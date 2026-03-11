---
title: Deformable Body
---

# Deformable Body

## Learning Objectives

After completing this tutorial, you will have learned:

- How to enable the Deformable Body (Beta) feature in Isaac Sim
- How to create a deformable object (Volume Deformable) from a primitive mesh
- How to import external meshes (STL/OBJ, etc.) and create deformable objects
- The difference between Volume Deformable and Surface Deformable
- How to create and apply a Deformable Body Material

## Getting Started

### Prerequisites

- Complete [Tutorial 7: Adding Props](07_adding_props.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Overview

In the previous tutorials, we worked with **rigid bodies**. Rigid bodies are objects whose shape never changes regardless of how much force is applied. However, in the real world, there are many objects that deform under force, such as sponges, cloth, and rubber products.

Isaac Sim provides the **Deformable Body (Beta)** feature to simulate such **deformable objects**. There are two main types of deformable objects:

| Type | Description | Examples |
|---|---|---|
| **Volume Deformable** | Solid, closed (watertight) objects with thickness | Sponges, rubber blocks, organ models, etc. |
| **Surface Deformable** | Thin membranes or surface-only objects | Cloth, paper, thin sheets, etc. |

!!! note "Beta Feature"
    Deformable Body is a Beta feature. Its specifications may change in future versions.

## Preparation: Enabling the Deformable Feature

To use Deformable Body, you first need to enable the feature in Isaac Sim's settings. This only needs to be done once.

1. Open **Edit > Preferences** from the top menu.

2. In the **Physics > General** section, turn on **Enable Deformable schema Beta (Requires Restart)**.

    ![Enabling Deformable schema](images/19_enable_deformable_schema.png)

3. **Restart** Isaac Sim.

!!! tip "Visualizing Deformable Meshes (Recommended)"
    When working with deformable objects, it is helpful to visualize the simulation and collision meshes to verify that the mesh density is appropriate. Click the **Eye icon** in the viewport and select **Show By Type > Physics > Deformables (beta) > All**.

## Setting Up the Stage

Create a new stage and prepare it for physics simulation.

1. Create a new stage with **File > New**.

2. From the top menu, select **Create > Physics > Ground Plane** to add a ground plane.

3. Select **Create > Physics > Physics Scene** to add a physics scene (some templates may already include one).

4. Select the created **PhysicsScene** in the Stage window and configure the following settings in the Properties panel:

    - Turn on **Enable GPU Dynamics**
    - Set **Broadphase Type** to `GPU`

!!! warning "GPU Settings Are Required"
    Deformable Body is processed through the PhysX GPU pipeline. The simulation will not work correctly if GPU Dynamics is disabled. Make sure to configure the settings above.

## Pattern 1: Creating a Deformable Object from a Primitive Mesh

The most basic approach is to create a deformable object using Isaac Sim's primitive mesh (Cube).

### Step 1: Creating an Xform and Mesh

First, create the root Xform for the deformable object and a sufficiently subdivided mesh.

1. Right-click in the Stage window and select **Create > Xform**. Rename it to `DeformPlate` (e.g., `/World/DeformPlate`).

2. From the top menu, select **Create > Mesh > Settings** to open the Mesh Settings dialog.

3. Set **Primitive Type** to `Cube`.

4. Increase the **U/V/W Verts Scale** values (e.g., `10` to `30`).

    ![Mesh Settings dialog](images/20_mesh_generation_settings.png)

    !!! warning "About Mesh Subdivision"
        If the subdivision count is too low, deformation will not be visually noticeable. Start with values around 10-30. You can fine-tune the values with Ctrl + left-click.

5. Click the **Create** button to generate the mesh.

6. **Drag-and-drop** the generated mesh as a child of `/World/DeformPlate`.

    ![Creating the mesh](images/21_create_mesh.png)

### Step 2: Applying Volume Deformable

Apply deformable physics properties to the created mesh.

7. Select the root Xform (`/World/DeformPlate`).

8. Right-click and select **Create > Physics > Deformable (beta) > Volume**.

    ![Creating Volume Deformable Body](images/22_add_deformable_attr.png)

9. A dialog will appear. If needed, turn on **Hexahedral Simulation Mesh** (to generate a separate simulation mesh for improved stability).

    ![Create Volume Deformable Body dialog](images/23_deformable_settings.png)

10. Click the **Create** button.

### Step 3: Testing the Result

11. Select `/World/DeformPlate` and set the **Translate** Z value to approximately `1.0` to `2.0` in the Properties panel to raise it above the ground.

12. Press the **PLAY** button to start the simulation.

    **Result:** The deformable object falls to the ground and deforms upon collision.

    ![Deformable Cube test](images/24_deformable_cube_test.webp)

13. Press the **STOP** button to stop the simulation.

## Pattern 2: Creating a Deformable Object from an External Mesh

You can create deformable objects with arbitrary shapes by importing external mesh files such as STL/OBJ/FBX.

### Step 1: Importing the Mesh

To use an external mesh in Isaac Sim, you first need to convert it to USD format.

1. From the top menu, select **File > Import** and use the CAD Converter to import the mesh file. The following images and videos use a [sample file](test_mesh/test.gltf).

    ![Import Mesh](images/30_import_settings.png)

    !!! note "Checking the Scale"
        STL files often do not contain unit information. After importing, always verify the scale (in meters).

### Step 2: Selecting and Applying the Deformable Type

Choose between Volume Deformable or Surface Deformable depending on the shape of the imported mesh.

#### For Solid, Closed Shapes → Volume Deformable

Use Volume Deformable when the mesh is a closed solid shape (watertight).

2. Right-click in the Stage window and select **Create > Xform** (e.g., `/World/DeformMesh`).

3. **Drag-and-drop** the imported mesh as a child of the Xform.

4. Select the Xform, right-click, and select **Create > Physics > Deformable (beta) > Volume**.

5. If needed, specify the target mesh in the **Source Mesh** field of the dialog.

    ![Creating Deformable Body](images/25_create_deformable_body.png)

    !!! tip "About Source Mesh"
        You can specify a Source Mesh separate from the rendering mesh for generating the simulation mesh. The Source Mesh can be a mesh located outside the Deformable subtree.

6. Click the **Create** button.

7. Raise the object in the Z direction and press **PLAY** to verify the behavior.

    ![Deformable Mesh test](images/26_deformable_mesh_test.webp)

#### For Thin Membranes or Surface-Only Shapes → Surface Deformable

Use Surface Deformable when the mesh represents a thin sheet or membrane that is not closed.

- Select the Xform, right-click, and select **Create > Physics > Deformable (beta) > Surface**.

### Troubleshooting

If deformation is not visible or the simulation is unstable, check the following:

- **Insufficient input mesh resolution**: If the mesh has too few vertices, deformation will not be reflected visually. Increase the mesh subdivision count.
- **Resolution mismatch between simulation and collision meshes**: If the resolutions differ significantly, convergence issues are more likely to occur.

## Configuring Deformable Body Material

The physical properties of deformable objects (stiffness, elasticity, etc.) are controlled by creating and assigning a **Deformable Body Material**.

### Step 1: Creating a Physics Material

1. From the top menu, select **Create > Physics > Physics Material**.

2. In the dialog that appears, select **Deformable Body Material** and click **OK**.

    ![Creating Deformable Material](images/27_create_deformable_material.png)

### Step 2: Setting Parameters

Adjust the following parameters in the Properties panel of the created physics material:

| Parameter | Description |
|---|---|
| **Young's Modulus** | Determines the stiffness of the object. Higher values make it stiffer |
| **Poisson's Ratio** | The ratio of lateral contraction when the object is stretched (typically 0 to 0.5) |
| **Density** | Mass density of the object (kg/m³) |
| **Dynamic Friction** | The strength of friction when the object is in motion |

!!! tip "Parameter Effects"
    Density, Young's Modulus, and Poisson's Ratio primarily affect the simulation mesh, while friction coefficients primarily affect the collision mesh.

### Step 3: Assigning the Material

3. Select the deformable object (the Deformable root Xform or related Prim).

4. In the Properties panel, select the created Deformable Body Material from the **Physics Materials on Selected …** section to assign it.

    ![Assigning the material](images/28_select_deformable_material.png)

5. Press the **PLAY** button to verify the behavior.

    ![Deformable Material test](images/26_deformable_mesh_test.webp)

## Summary

This tutorial covered the following topics:

1. **Enabling the Deformable Body (Beta) feature**
2. Creating a **Volume Deformable** from a primitive mesh
3. Importing external meshes and choosing between **Volume / Surface Deformable**
4. Configuring and assigning physics parameters with **Deformable Body Material**

!!! note "Difference from Rigid Bodies"
    Rigid bodies are computationally efficient because their shape does not change. Deformable objects, on the other hand, require individual calculations for each mesh vertex, resulting in higher computational cost. Choose between rigid bodies and deformable objects depending on the purpose of your simulation.

## References

- [Deformable Visual Authoring (Beta) — Omni Physics](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/deformables_beta/deformable_authoring.html)
- [Omni Physics Deformable Schema — Omni Physics](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/deformables_beta/omniphysics_deformable_schema.html)
- [Physics Simulation Fundamentals — Isaac Sim Documentation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/physics/simulation_fundamentals.html)
