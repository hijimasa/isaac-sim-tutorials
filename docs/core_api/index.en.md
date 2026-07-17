---
title: Core API Tutorials
---

# Core API Tutorials

<span class="badge badge-beginner">Beginner</span>

## Overview

NVIDIA Isaac Sim is a reference application for robotics built on NVIDIA Omniverse (more precisely, the Omniverse Kit). When developing on Omniverse, you can use the NVIDIA Omniverse™ Kit and Pixar's USD Python API.

The NVIDIA Omniverse™ Kit is a toolkit that provides the GUI, extensions, and runtime environment needed for application development, and includes a Python interpreter for scripting. This allows you to utilize various features as Python APIs, in addition to many operations executable via the GUI.

Meanwhile, Pixar's USD Python API provides a low-level API for manipulating objects, hierarchies, attributes, transformations, and more within a scene. Since Isaac Sim scenes are also internally represented in USD, you can directly use these APIs as needed.

However, working across Omniverse Kit and the USD Python API involves a steep learning curve and often leads to cumbersome procedures. Therefore, Isaac Sim provides a set of high-level APIs for robotics applications. These abstract away the complexity of the USD API and enable you to implement frequently performed tasks with fewer steps.

This tutorial introduces the concepts of the core API and how to use it. We start by adding a cube to an empty stage and build upon this to construct a scene where multiple robots perform multiple tasks simultaneously (see figure below).

![tutorial target](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_6_2.webp)

!!! note "About the Core API in Isaac Sim 6.0"
    In Isaac Sim 6.0, the legacy `isaacsim.core.api` (the World / Scene / Task based API) is **deprecated**, and the official Core API tutorials have been rewritten to use `isaacsim.core.experimental.*` and `isaacsim.core.simulation_manager`. This section follows the rewritten content. For migrating from the legacy API, see the [official migration guides](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/index.html).

## Tutorials

<!-- Add tutorial articles below -->

!!! example "[Tutorial 1: Hello World](01_hello_world.md)"
    Learn how to manipulate the USD stage with the Core API (experimental), add rigid bodies to the Stage, and run simulations.

!!! example "[Tutorial 2: Hello Robot](02_hello_robot.md)"
    Learn how to load robot assets from the Nucleus server and control robot joints using the Articulation class.

!!! example "[Tutorial 3: Adding a Controller](03_adding_a_controller.md)"
    Learn how to create custom controllers and use the built-in controllers available in Isaac Sim. (This page was removed from the official Isaac Sim 6.0 documentation and is retained here as this site's own guide.)

!!! example "[Tutorial 4: Adding a Manipulator Robot](04_adding_a_manipulator_robot.md)"
    Learn how to add a Franka Panda manipulator to the scene and execute pick-and-place operations with the FrankaPickPlace class.

!!! example "[Tutorial 5: Adding Multiple Robots](05_adding_multiple_robots.md)"
    Build a multi-robot simulation where Jetbot and Franka cooperate, using state machine logic to coordinate their actions.

!!! example "[Tutorial 6: Multiple Robot Scenarios](06_multiple_tasks.md)"
    Learn how to organize robot scenarios into Python classes and run multiple instances in parallel using an offset parameter.

!!! example "[Tutorial 7: Adding Props](07_adding_props.md)"
    Learn how to configure Rigid Body, Collider, Mass, and Physics Material attributes on objects via the GUI.

!!! example "[Tutorial 8: Data Logging](08_data_logging.md)"
    Learn how to record, save, and replay simulation data using the DataLogger class. (This page was removed from the official Isaac Sim 6.0 documentation and is retained here as this site's own guide.)

!!! example "[Tutorial 9: Deformable Body](09_deformable_body.md)"
    Learn how to create deformable objects using the Deformable Body (Beta) feature and configure physics materials.
