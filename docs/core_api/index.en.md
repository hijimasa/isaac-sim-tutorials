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

![tutorial target](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## Tutorials

<!-- Add tutorial articles below -->

!!! example "[Tutorial 1: Hello World](01_hello_world.md)"
    Learn how to create Worlds and Scenes defined by the Core API, add rigid bodies to Stages, and run simulations.

!!! example "[Tutorial 2: Hello Robot](02_hello_robot.md)"
    Learn how to load robot assets from the Nucleus server and control robots using the Robot and WheeledRobot classes.

!!! example "[Tutorial 3: Adding a Controller](03_adding_a_controller.md)"
    Learn how to create custom controllers and use the built-in controllers available in Isaac Sim.

!!! example "[Tutorial 4: Adding a Manipulator Robot](04_adding_a_manipulator_robot.md)"
    Learn how to add a Franka Panda manipulator to the scene, use the pick-and-place controller, and modularize tasks.
