---
title: Adding Multiple Robots
---

# Adding Multiple Robots

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add different types of robots to the same simulation
- How to compose tasks using subtasks
- How to build program logic that switches between robot actions using task events
- How to implement a simulation where multiple robots work together

## Getting Started

### Prerequisites

- Complete [Tutorial 4: Adding a Manipulator Robot](04_adding_a_manipulator_robot.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Preparing the Source Code

This tutorial continues editing the `hello_world.py` file from the Hello World sample. If you are continuing from the previous tutorial, you can proceed as-is. If you are resuming on a different day, follow these steps to open the source code:

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > General > Hello World**.
3. Click the **Open Source Code** button to open `hello_world.py` in Visual Studio Code.

For detailed instructions, refer to the ["Opening the Hello World Sample" section](01_hello_world.md#opening-the-hello-world-sample) in Hello World.

!!! warning "Warning"
    Pressing **STOP** then **PLAY** may not properly reset the world. Use the **RESET** button to restart the simulation.

## Overview

In this tutorial, we will incrementally build a simulation where two robots — Jetbot and Franka — cooperate to perform the following sequence of actions:

1. **Jetbot** pushes a cube toward Franka
2. **Jetbot** reverses to give Franka working space
3. **Franka** picks up the cube and places it at a goal position

The code is developed in 4 incremental steps.

## Step 1: Creating the Scene

First, we place both the Jetbot and Franka in the scene. By reusing the `PickPlace` task from the previous tutorial as a **subtask**, we can set up Franka and the cube concisely.

```python linenums="1" hl_lines="2-5 9-13 21-22 27-37 39-42"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        # Reuse the PickPlace task as a subtask
        # Customize the cube's initial position and target position
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        # Call the subtask's set_up_scene to place Franka and the cube
        self._pick_place_task.set_up_scene(scene)
        # Add the Jetbot
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        # Get Franka from the subtask's parameters and change its position
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        return observations

    def get_params(self):
        # Dynamically retrieve parameters to avoid hard-coding names
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.add_task(RobotsPlaying(name="awesome_task"))
        return
```

!!! info "The Subtask Pattern"
    The `RobotsPlaying` task internally calls `PickPlace`'s `set_up_scene`. By incorporating existing tasks as subtasks, you avoid reimplementing the same logic.

!!! note "Difference between `set_world_pose` and `set_default_state`"
    Two methods are used to change Franka's position because they serve different purposes:

    | Method | Purpose |
    |---|---|
    | `set_world_pose()` | Immediately moves the robot's position in the **current frame** |
    | `set_default_state()` | Registers the position to **return to on reset** |

    If you omit `set_default_state()`, pressing the RESET button will cause Franka to return to its original position (near the origin) set internally by the PickPlace task, resulting in an overlap with Jetbot.

Save the code and verify the simulation:

1. Press **Ctrl+S** to save, then do **File > New From Stage Template > Empty** and click **LOAD**.
2. Verify that both the Jetbot and Franka appear in the scene.

## Step 2: Moving the Jetbot

Next, we add a controller to the Jetbot so it pushes the cube toward Franka. We reuse the `WheelBasePoseController` from Tutorial 3.

```python linenums="1" hl_lines="6-7 79-89 95-96 98-104"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.add_task(RobotsPlaying(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        # Initialize the Jetbot controller
        self._jetbot_controller = WheelBasePoseController(
            name="cool_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_control",
                wheel_radius=0.03,
                wheel_base=0.1125,
            ),
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._jetbot_controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        # Move the Jetbot toward the goal position
        self._jetbot.apply_wheel_actions(
            self._jetbot_controller.forward(
                start_position=current_observations[self._jetbot.name]["position"],
                start_orientation=current_observations[self._jetbot.name]["orientation"],
                goal_position=current_observations[self._jetbot.name]["goal_position"],
            )
        )
        return
```

Save and press **PLAY** to observe the Jetbot pushing the cube toward Franka.

## Step 3: Adding Task Events

Currently, the Jetbot keeps moving even after delivering the cube. We introduce task events (`_task_event`) to manage three phases:

| Event | Action |
|---|---|
| `0` | Jetbot pushes the cube toward Franka |
| `1` | Jetbot reverses to give Franka working space |
| `2` | Jetbot stops (Franka is ready to work) |

```python linenums="1" hl_lines="8 16 51-52 65-73 76 80-81 103-115"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.utils.types import ArticulationAction
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        self._task_event = 0  # Task event: manages which phase is active
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            "task_event": self._task_event,
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def pre_step(self, control_index, simulation_time):
        if self._task_event == 0:
            # Check if the Jetbot has reached the goal position
            current_jetbot_position, _ = self._jetbot.get_world_pose()
            if np.mean(np.abs(current_jetbot_position[:2] - self._jetbot_goal_position[:2])) < 0.04:
                self._task_event += 1
                self._cube_arrive_step_index = control_index
        elif self._task_event == 1:
            # After 200 steps of reversing, advance to the next phase
            if control_index - self._cube_arrive_step_index == 200:
                self._task_event += 1
        return

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        self._task_event = 0
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.add_task(RobotsPlaying(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        self._jetbot_controller = WheelBasePoseController(
            name="cool_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_control",
                wheel_radius=0.03,
                wheel_base=0.1125,
            ),
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._jetbot_controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        if current_observations["task_event"] == 0:
            # Phase 0: Jetbot pushes the cube
            self._jetbot.apply_wheel_actions(
                self._jetbot_controller.forward(
                    start_position=current_observations[self._jetbot.name]["position"],
                    start_orientation=current_observations[self._jetbot.name]["orientation"],
                    goal_position=current_observations[self._jetbot.name]["goal_position"],
                )
            )
        elif current_observations["task_event"] == 1:
            # Phase 1: Jetbot reverses
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[-8, -8]))
        elif current_observations["task_event"] == 2:
            # Phase 2: Stop the Jetbot
            # Note: target joint velocities persist unless explicitly changed
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
        return
```

Save and press **PLAY** to observe the Jetbot delivering the cube, reversing, and stopping.

## Step 4: Franka Pick and Place

Finally, we add Franka's controller so that after the Jetbot clears the area, Franka picks up the cube and places it at the goal position.

```python linenums="1" hl_lines="8 55-56 88-92 99-100 115-121 123-124"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.core.utils.types import ArticulationAction
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        self._task_event = 0
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            "task_event": self._task_event,
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        # Merge subtask observations
        observations.update(self._pick_place_task.get_observations())
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def pre_step(self, control_index, simulation_time):
        if self._task_event == 0:
            current_jetbot_position, _ = self._jetbot.get_world_pose()
            if np.mean(np.abs(current_jetbot_position[:2] - self._jetbot_goal_position[:2])) < 0.04:
                self._task_event += 1
                self._cube_arrive_step_index = control_index
        elif self._task_event == 1:
            if control_index - self._cube_arrive_step_index == 200:
                self._task_event += 1
        return

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        self._task_event = 0
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.add_task(RobotsPlaying(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._franka = self._world.scene.get_object(task_params["franka_name"]["value"])
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        # Add Franka controller
        self._franka_controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,
            robot_articulation=self._franka,
        )
        self._jetbot_controller = WheelBasePoseController(
            name="cool_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_control",
                wheel_radius=0.03,
                wheel_base=0.1125,
            ),
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._franka_controller.reset()
        self._jetbot_controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        if current_observations["task_event"] == 0:
            self._jetbot.apply_wheel_actions(
                self._jetbot_controller.forward(
                    start_position=current_observations[self._jetbot.name]["position"],
                    start_orientation=current_observations[self._jetbot.name]["orientation"],
                    goal_position=current_observations[self._jetbot.name]["goal_position"],
                )
            )
        elif current_observations["task_event"] == 1:
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[-8, -8]))
        elif current_observations["task_event"] == 2:
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
            # Franka picks up the cube and places it
            actions = self._franka_controller.forward(
                picking_position=current_observations[self._cube_name]["position"],
                placing_position=current_observations[self._cube_name]["target_position"],
                current_joint_positions=current_observations[self._franka.name]["joint_positions"],
            )
            self._franka.apply_action(actions)
        # Pause simulation when Franka's pick-and-place is complete
        if self._franka_controller.is_done():
            self._world.pause()
        return
```

!!! note "Using `control_index` in `pre_step`"
    The `control_index` in `pre_step(control_index, simulation_time)` is an index that auto-increments with each physics step (see [Tutorial 4](04_adding_a_manipulator_robot.md)). In this code, the `control_index` at the moment the Jetbot reaches the goal is saved to `_cube_arrive_step_index`, and the end of the reversing phase is determined by checking whether 200 steps have elapsed since then.

Save the code and verify the simulation:

1. Press **Ctrl+S** to save, then do **File > New From Stage Template > Empty** and click **LOAD**.
2. Press the **PLAY** button and observe the following sequence:
    - Jetbot pushes the cube toward Franka
    - Jetbot reverses to clear the area
    - Franka picks up the cube and places it at the goal position
    - The simulation pauses after completion

![Multiple robots cooperating](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## Summary

This tutorial covered the following topics:

1. Placing two types of robots — **Jetbot** and **Franka** — in the same scene
2. Reusing the existing `PickPlace` task as a **subtask**
3. Managing phase transitions between robot actions using **task events**
4. Merging subtask observations via `observations.update()`

## Next Steps

Proceed to the next tutorial, "[Multiple Tasks](06_multiple_tasks.md)," to learn how to spatially arrange and run multiple instances of the same task in parallel.

!!! note "Note"
    The following tutorials continue to use the Extension Workflow for development. Converting to the Standalone Workflow follows the same approach as learned in [Hello World](01_hello_world.md#converting-to-a-standalone-application).
