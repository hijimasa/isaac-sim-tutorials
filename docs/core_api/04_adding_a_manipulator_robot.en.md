---
title: Adding a Manipulator Robot
---

# Adding a Manipulator Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add a manipulator robot (Franka Panda) to the scene
- How to implement pick-and-place operations using the `PickPlaceController`
- How to modularize tasks by inheriting from `BaseTask`
- How to use the pre-built task classes available in Isaac Sim

## Getting Started

### Prerequisites

- Complete [Tutorial 3: Adding a Controller](03_adding_a_controller.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

!!! warning "Warning"
    Pressing **STOP** then **PLAY** may not properly reset the world. Use the **RESET** button to restart the simulation.

## Creating the Scene

In the previous tutorials, we used a wheeled robot (Jetbot). Here, we introduce a new type of robot — a **manipulator (robot arm)**.

Isaac Sim provides a dedicated `Franka` class for the Franka Panda robot, offering manipulator-specific features such as access to the gripper and end-effector instances.

```python linenums="1" hl_lines="3-4 18-19 21-28"
from isaacsim.examples.interactive.base_sample import BaseSample
# Extension containing Franka-related tasks and controllers
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
import numpy as np


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        # Franka is a robot-specific class that provides extra functionalities
        # such as gripper and end-effector instances
        franka = world.scene.add(
            Franka(prim_path="/World/Fancy_Franka", name="fancy_franka")
        )
        # Add a cube for the Franka to pick up
        world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0.3, 0.3, 0.3]),     # Initial cube position
                scale=np.array([0.0515, 0.0515, 0.0515]),# Cube size
                color=np.array([0, 0, 1.0]),              # Blue
            )
        )
        return
```

Save the code and verify the simulation:

1. Press **Ctrl+S** to save the code and hot-reload Isaac Sim.
2. Click **File > New From Stage Template > Empty** to create a new world, then click **LOAD**.
3. Verify that the Franka robot and blue cube appear in the scene.

## Using the PickAndPlace Controller

Next, we use the Franka's pick-and-place controller to pick up the cube and move it to a different location.

The `PickPlaceController` operates as a state machine, automatically executing the following sequence:

1. Move to the cube's position
2. Close the gripper to grasp the cube
3. Move to the goal position
4. Open the gripper to place the cube

```python linenums="1" hl_lines="4 33-38 40-41 50-56 58-59"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController  # Pick and place controller
import numpy as np


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        franka = world.scene.add(
            Franka(prim_path="/World/Fancy_Franka", name="fancy_franka")
        )
        world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0.3, 0.3, 0.3]),
                scale=np.array([0.0515, 0.0515, 0.0515]),
                color=np.array([0, 0, 1.0]),
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._franka = self._world.scene.get_object("fancy_franka")
        self._fancy_cube = self._world.scene.get_object("fancy_cube")
        # Initialize the PickPlaceController
        self._controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,            # Gripper instance
            robot_articulation=self._franka,          # Robot articulation
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        # Set the gripper to the open position
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        # In async workflow, use the async version of play
        await self._world.play_async()
        return

    # Called after the RESET button is pressed
    # Any reset logic should be placed here
    async def setup_post_reset(self):
        self._controller.reset()
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        cube_position, _ = self._fancy_cube.get_world_pose()
        goal_position = np.array([-0.3, -0.3, 0.0515 / 2.0])  # Goal placement position
        current_joint_positions = self._franka.get_joint_positions()
        # The controller computes actions for each stage of pick and place
        actions = self._controller.forward(
            picking_position=cube_position,
            placing_position=goal_position,
            current_joint_positions=current_joint_positions,
        )
        self._franka.apply_action(actions)
        # Pause simulation when the state machine reaches the final state
        if self._controller.is_done():
            self._world.pause()
        return
```

Save the code and verify the simulation:

1. Press **Ctrl+S** to save, then do **File > New From Stage Template > Empty** and click **LOAD**.
2. Press the **PLAY** button and observe the Franka picking up the cube and placing it at the goal position.
3. The simulation automatically pauses when the operation is complete.

![Franka performing pick and place](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_4_1.webp)

## What is a Task?

So far, the scene creation (`setup_scene`), controller initialization (`setup_post_load`), and physics step handling (`physics_step`) are all mixed together in the `HelloWorld` class.

A **Task** is a mechanism for modularizing specific work within the scene. By defining a task class that inherits from `BaseTask`, you can independently manage the following:

| Method | Description |
|---|---|
| `set_up_scene` | Place assets needed for the task in the scene |
| `get_observations` | Return observation data needed to solve the task |
| `pre_step` | Logic executed before each physics step (e.g., task completion check) |
| `post_reset` | Initialization logic after reset |

By modularizing tasks, you can reuse the same task across different robots and scenes.

### Task Implementation Example

The following code defines a `FrankaPlaying` task that changes the cube's color to green when it reaches the goal position.

```python linenums="1" hl_lines="5 8-62 69 78-81"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.core.api.tasks import BaseTask  # Base class for tasks
import numpy as np


class FrankaPlaying(BaseTask):
    # We only override a subset of available task methods here
    # Other overridable methods include: calculate_metrics, is_done, etc.
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._goal_position = np.array([-0.3, -0.3, 0.0515 / 2.0])
        self._task_achieved = False
        return

    # Place all assets needed for the task in the scene
    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        scene.add_default_ground_plane()
        self._cube = scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0.3, 0.3, 0.3]),
                scale=np.array([0.0515, 0.0515, 0.0515]),
                color=np.array([0, 0, 1.0]),
            )
        )
        self._franka = scene.add(
            Franka(prim_path="/World/Fancy_Franka", name="fancy_franka")
        )
        return

    # Return observation data needed to solve the task
    def get_observations(self):
        cube_position, _ = self._cube.get_world_pose()
        current_joint_positions = self._franka.get_joint_positions()
        observations = {
            self._franka.name: {
                "joint_positions": current_joint_positions,
            },
            self._cube.name: {
                "position": cube_position,
                "goal_position": self._goal_position,
            },
        }
        return observations

    # Called before each physics step
    # Check if the task is accomplished and provide visual feedback
    def pre_step(self, control_index, simulation_time):
        cube_position, _ = self._cube.get_world_pose()
        if not self._task_achieved and np.mean(np.abs(self._goal_position - cube_position)) < 0.02:
            # Change the cube's color to green when it reaches the goal
            self._cube.get_applied_visual_material().set_color(color=np.array([0, 1.0, 0]))
            self._task_achieved = True
        return

    # Called after each reset
    # Open the gripper and reset the cube's color to blue
    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        self._cube.get_applied_visual_material().set_color(color=np.array([0, 0, 1.0]))
        self._task_achieved = False
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        # Add the task to the world
        world.add_task(FrankaPlaying(name="my_first_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        # The world has already called the task's set_up_scene (during the first reset)
        # so we can retrieve the task objects
        self._franka = self._world.scene.get_object("fancy_franka")
        self._controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,
            robot_articulation=self._franka,
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        # Get all task observations
        current_observations = self._world.get_observations()
        actions = self._controller.forward(
            picking_position=current_observations["fancy_cube"]["position"],
            placing_position=current_observations["fancy_cube"]["goal_position"],
            current_joint_positions=current_observations["fancy_franka"]["joint_positions"],
        )
        self._franka.apply_action(actions)
        if self._controller.is_done():
            self._world.pause()
        return
```

By using a Task, the `HelloWorld` class becomes much simpler. The scene construction and task completion logic are separated into `FrankaPlaying`, allowing `HelloWorld` to focus on controller execution.

## Using the Pre-built PickPlace Task

Isaac Sim's robot extensions also provide pre-defined task classes. For Franka, the `PickPlace` task achieves the same functionality as the custom task above with even less code.

Key features of pre-built tasks:

- Dynamically retrieve task parameters (robot name, cube name, etc.) via `get_params()`
- Modify parameters during simulation via `set_params()`
- The goal position is accessed with the key `target_position` (note: this differs from `goal_position` in our custom task)

```python linenums="1" hl_lines="2-3 11 17-20 22-23"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace        # Pre-built task
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        # Add the pre-built PickPlace task
        world.add_task(PickPlace(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        # Dynamically retrieve task parameters
        # {"task_param_name": {"value": [value], "modifiable": [True/False]}}
        task_params = self._world.get_task("awesome_task").get_params()
        self._franka = self._world.scene.get_object(task_params["robot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        self._controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,
            robot_articulation=self._franka,
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        actions = self._controller.forward(
            picking_position=current_observations[self._cube_name]["position"],
            placing_position=current_observations[self._cube_name]["target_position"],  # Pre-built task uses target_position
            current_joint_positions=current_observations[self._franka.name]["joint_positions"],
        )
        self._franka.apply_action(actions)
        if self._controller.is_done():
            self._world.pause()
        return
```

### Custom Task vs Pre-built Task

| Feature | Custom Task | Pre-built Task (`PickPlace`) |
|---|---|---|
| Scene construction | Self-implemented in `set_up_scene` | Automatically built by the task |
| Parameters | Hardcoded | Dynamically managed via `get_params()` / `set_params()` |
| Reusability | Depends on specific scene | Flexible through parameter changes |
| Code volume | More | Less |

## Summary

This tutorial covered the following topics:

1. Adding the **Franka Panda** manipulator robot to the scene
2. Implementing pick-and-place operations using the **PickPlaceController**
3. Modularizing tasks by inheriting from **BaseTask** and managing observations
4. Efficient implementation using the pre-built **PickPlace** task

## Next Steps

Proceed to the next tutorial to further develop your simulation environment.

!!! note "Note"
    The following tutorials continue to use the Extension Workflow for development. Converting to the Standalone Workflow follows the same approach as learned in [Hello World](01_hello_world.md).
