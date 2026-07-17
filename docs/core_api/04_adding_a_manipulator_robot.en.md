---
title: Adding a Manipulator Robot
---

# Adding a Manipulator Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add a manipulator robot (Franka Panda) to the scene using the `Franka` class
- The basic APIs for inverse kinematics (IK) based end-effector control and gripper control
- How to execute pick-and-place operations with the `FrankaPickPlace` class
- Understanding and customizing the pick-and-place state machine

## Getting Started

### Prerequisites

- Completed [Tutorial 2: Hello Robot](02_hello_robot.md)

!!! note "This tutorial uses the Standalone Workflow"
    While the previous tutorials used the Extension Workflow (editing `hello_world.py`), this tutorial uses **standalone Python scripts**. Run the scripts with the Python environment bundled with Isaac Sim (`python.sh`, or `python.bat` on Windows). The procedure is the same as what you learned in ["Converting the Example to a Standalone Application" in Hello World](01_hello_world.md).

### Estimated Time

Approximately 15–20 minutes

## Creating the Scene with a Franka Robot

Add a Franka robot and a cube for the robot to pick up using the `Franka` class. This class inherits from `Articulation` and provides high-level control methods including inverse kinematics (IK) and gripper control.

When you set `create_robot=True` in the constructor, `Franka` automatically spawns the Franka robot USD asset at the specified path.

Create the following script, for example as `create_franka_scene.py`:

```python linenums="1" hl_lines="13-15 20 28-29 31-40 42-46"
"""Create a scene with ground, Franka robot, and blue cube."""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.app as app_utils

app_utils.enable_extension("isaacsim.robot.experimental.manipulators.examples")

from isaacsim.core.experimental.objects import Cube, DomeLight, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.manipulators.examples.franka import Franka

DEVICE = "cpu"

GroundPlane("/World/ground_plane")
dome_light = DomeLight("/World/DomeLight")
dome_light.set_intensities(1000)

# Create the Franka robot
robot = Franka(robot_path="/World/robot", create_robot=True)

# Create a blue cube for the robot to pick up
cube_shape = Cube(
    paths="/World/Cube",
    positions=[0.5, 0.0, 0.0258],
    sizes=1.0,
    scales=[0.0515, 0.0515, 0.0515],
    colors="blue",
)
GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
RigidPrim(paths=cube_shape.paths)

SimulationManager.setup_simulation(dt=1.0 / 60.0, device=DEVICE)
physics_scene = SimulationManager.get_physics_scenes()[0]
physics_scene.set_enabled_gpu_dynamics(False)
app_utils.play()
app_utils.update_app(steps=20)

step_count = 0
max_test_steps = 60
while simulation_app.is_running():
    simulation_app.update()
    step_count += 1
    if args.test and step_count >= max_test_steps:
        break

app_utils.stop()
simulation_app.close()
```

Run the script. A window opens with the Franka robot and cube in the scene; the simulation runs until you close the window.

```bash
cd <Isaac Sim installation directory>
./python.sh create_franka_scene.py
```

Key points of this script:

| Operation | Description |
|---|---|
| `app_utils.enable_extension()` | Enables the `isaacsim.robot.experimental.manipulators.examples` extension that provides the `Franka` class |
| `Franka(robot_path=..., create_robot=True)` | Spawns the Franka USD asset and creates the wrapper in one step |
| `SimulationManager.setup_simulation()` | Configures the physics time step (`dt`) and execution device (CPU/GPU) |
| `app_utils.play()` / `app_utils.update_app()` | Plays the timeline and advances the app by the specified number of steps |

The `Franka` class provides these key methods for robot control:

| Method | Description |
|---|---|
| `set_end_effector_pose(position, orientation)` | Move the end-effector using inverse kinematics (IK) |
| `open_gripper()` / `close_gripper()` | Control the gripper |
| `get_current_state()` | Get DOF positions and end-effector pose |
| `get_downward_orientation()` | Get the quaternion for a downward-facing end-effector orientation |
| `reset_to_default_pose()` | Reset the robot to its home position |

!!! note "What is inverse kinematics (IK)?"
    **Inverse kinematics** is the computation that derives the joint angles needed to achieve a target position and orientation of the end-effector (hand). By simply calling `set_end_effector_pose()`, the `Franka` class automatically computes the joint angles internally.

## Using FrankaPickPlace for Complete Pick-and-Place

For a complete pick-and-place operation, use the `FrankaPickPlace` class. This class has a `setup_scene()` method that spawns everything needed for pick-and-place: the Franka robot, ground plane, and a cube to manipulate.

```python linenums="1" hl_lines="19 27-30 35-39 41-53"
"""Pick-and-place using FrankaPickPlace."""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.app as app_utils

app_utils.enable_extension("isaacsim.robot.experimental.manipulators.examples")

from isaacsim.core.experimental.objects import DomeLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.manipulators.examples.franka import FrankaPickPlace

DEVICE = "cpu"

GroundPlane("/World/ground_plane")
dome_light = DomeLight("/World/DomeLight")
dome_light.set_intensities(1000)

# FrankaPickPlace spawns robot and cube, and provides the pick-place state machine
controller = FrankaPickPlace()
controller.setup_scene()

SimulationManager.setup_simulation(dt=1.0 / 60.0, device=DEVICE)
physics_scene = SimulationManager.get_physics_scenes()[0]
physics_scene.set_enabled_gpu_dynamics(False)
app_utils.play()
# Run a few steps so the articulation's physics tensor entity is valid before `controller.reset()`
app_utils.update_app(steps=20)
controller.reset()

# Main loop: run one pick-place step each physics frame until done
step_count = 0
max_test_steps = sum(controller.events_dt) + 60
while simulation_app.is_running():
    simulation_app.update()
    step_count += 1
    if app_utils.is_playing():
        if not controller.is_done():
            controller.forward()
        else:
            print("Pick-and-place completed")
            app_utils.pause()
            if args.test:
                break
    if args.test and step_count >= max_test_steps:
        raise RuntimeError("Pick-and-place did not complete within the test step budget")

app_utils.stop()
simulation_app.close()
```

Run the script. The robot automatically executes all phases of picking up and placing the cube.

![Pick-and-place with the Franka](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_4_1.webp)

## Understanding the Pick-and-Place State Machine

The `FrankaPickPlace` class uses a state machine with the following phases:

| Phase | Description | Default Steps |
|---|---|---|
| 0 | Move to x, y position above cube | 60 |
| 1 | Approach down to cube | 40 |
| 2 | Close gripper to grasp | 20 |
| 3 | Lift cube upward | 40 |
| 4 | Move cube to target location | 80 |
| 5 | Open gripper to release | 20 |
| 6 | Move up and away | 20 |

You can customize the phase durations by passing `events_dt` to the constructor, and change the cube starting position, size, and target position using `setup_scene()`:

```python linenums="1"
# Custom phase durations (steps for each phase)
controller = FrankaPickPlace(events_dt=[80, 60, 30, 60, 100, 30, 30])
# Customize cube position, size, and target position
controller.setup_scene(
    cube_initial_position=[0.4, 0.2, 0.0258], cube_size=[0.05, 0.05, 0.05], target_position=[-0.4, 0.2, 0.12]
)
```

The complete code is as follows:

```python linenums="1" hl_lines="27-34"
"""Pick-and-place using FrankaPickPlace."""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.app as app_utils

app_utils.enable_extension("isaacsim.robot.experimental.manipulators.examples")

from isaacsim.core.experimental.objects import DomeLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.manipulators.examples.franka import FrankaPickPlace

DEVICE = "cpu"

GroundPlane("/World/ground_plane")
dome_light = DomeLight("/World/DomeLight")
dome_light.set_intensities(1000)

# -- Begin custom setup -- #
# Custom phase durations (steps for each phase)
controller = FrankaPickPlace(events_dt=[80, 60, 30, 60, 100, 30, 30])
# Customize cube position, size, and target position
controller.setup_scene(
    cube_initial_position=[0.4, 0.2, 0.0258], cube_size=[0.05, 0.05, 0.05], target_position=[-0.4, 0.2, 0.12]
)
# -- End of custom setup -- #

SimulationManager.setup_simulation(dt=1.0 / 60.0, device=DEVICE)
physics_scene = SimulationManager.get_physics_scenes()[0]
physics_scene.set_enabled_gpu_dynamics(False)
app_utils.play()
# Run a few steps so the articulation's physics tensor entity is valid before `controller.reset()`
app_utils.update_app(steps=20)
controller.reset()

# Main loop: run one pick-place step each physics frame until done
step_count = 0
max_test_steps = sum(controller.events_dt) + 60
while simulation_app.is_running():
    simulation_app.update()
    step_count += 1
    if app_utils.is_playing():
        if not controller.is_done():
            controller.forward()
        else:
            print("Pick-and-place completed")
            app_utils.pause()
            if args.test:
                break
    if args.test and step_count >= max_test_steps:
        raise RuntimeError("Pick-and-place did not complete within the test step budget")

app_utils.stop()
simulation_app.close()
```

!!! tip "See also: a more complete example"
    For a complete standalone pick-and-place example with `--device`, `--ik-method`, and `--test` options, see `standalone_examples/api/isaacsim.robot.experimental.manipulators/franka/pick_place.py` shipped with Isaac Sim.

## Summary

This tutorial covered the following topics:

1. Adding a Franka manipulator robot using the **Franka class** with `create_robot=True`
2. Key methods for **inverse kinematics (IK) and gripper control**
3. Using the **`FrankaPickPlace.setup_scene()`** method to spawn a complete pick-and-place scene
4. Executing pick-and-place operations with the **`forward()`** method
5. **Understanding and customizing** the pick-and-place state machine phases

## Next Steps

Continue to the next tutorial, [Adding Multiple Robots](05_adding_multiple_robots.md), to learn how to build simulations where multiple robots work together.
