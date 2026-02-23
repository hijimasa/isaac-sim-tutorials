---
title: Stage Setup
---

# Stage Setup

## Learning Objectives

After completing this tutorial, you will have learned:

- How to check and configure stage properties (axis orientation, units, rotation order)
- How to create a Physics Scene and configure gravity and broadphase settings
- How to add a ground plane
- How to add and adjust lighting

## Getting Started

### Prerequisites

- Isaac Sim is installed and can be launched

### Estimated Time

Approximately 10-15 minutes.

### Overview

In this tutorial, you will learn how to set up a virtual environment for physics simulation. You will configure stage properties, create a Physics Scene, and add a ground plane and lighting through GUI operations.

## Setting Up Stage Properties

1. Open **Edit > Preferences** and review the Stage settings.

    - **Up Axis**: Z (default)
    - **Stage Units**: Meters (default)
    - **Rotation Order**: XYZ

    ![Preferences](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_preferences.png)

## Creating the Physics Scene

1. Select **Create > Physics > Physics Scene**.

2. In the Properties panel, review and configure the following:

    - **Gravity**: Verify the default gravity settings
    - **Enable GPU Dynamics**: Disable for efficiency
    - **Broadphase Type**: Set to MBP

    ![Physics Properties](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_base_ref_gui_physics_properties.png)

## Adding a Ground Plane

1. Select **Create > Physics > Ground Plane**.

2. Enable the Grid visualization to visually confirm the ground position.

    ![Eye icon](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_eyecon.png)

## Adding Lighting

1. Select **Create > Light > Sphere Light** to add a sphere light.

2. Adjust the following in the Properties panel:

    - **Position**: Place at an appropriate position to illuminate the scene
    - **Intensity**: Adjust brightness
    - **Color**: Set the light color
    - **Radius**: Set the light's area of influence

    ![Lighting](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_lighting.png)

## Summary

This tutorial covered the following topics:

1. Checking and configuring **stage properties**
2. Creating a **Physics Scene** and configuring physics engine settings
3. Adding a **ground plane**
4. Adding and adjusting **lighting**

## Next Steps

Proceed to the next tutorial, "[Assemble a Simple Robot](02_assemble_robot.md)", to learn how to build a robot using primitive shapes.
