---
title: Multiple Tasks
---

# Multiple Tasks

## Learning Objectives

After completing this tutorial, you will have learned:

- How to spatially position task assets using the `offset` parameter
- How to avoid name collisions using `find_unique_string_name()`
- How to manage offsets with `_task_objects` and `_move_task_objects_to_their_frame()`
- How to instantiate and run multiple instances of the same task in parallel

## Getting Started

### Prerequisites

- Complete [Tutorial 5: Adding Multiple Robots](05_adding_multiple_robots.md) before starting this tutorial.

### Estimated Time

Approximately 15-20 minutes.

### Preparing the Source Code

This tutorial continues editing the `hello_world.py` file from the Hello World sample. If you are continuing from the previous tutorial, you can proceed as-is. If you are resuming on a different day, follow these steps to open the source code:

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > General > Hello World**.
3. Click the **Open Source Code** button to open `hello_world.py` in Visual Studio Code.

For detailed instructions, refer to the ["Opening the Hello World Sample" section](01_hello_world.md) in Hello World.

!!! warning "Warning"
    Pressing **STOP** then **PLAY** may not properly reset the world. Use the **RESET** button to restart the simulation.

## Parameterizing Tasks

In the previous tutorial, we used a single `RobotsPlaying` task. To place multiple instances of the same task, we need to **offset the position** of each task's assets so they don't overlap.

`BaseTask` supports an `offset` parameter that translates all assets within the task by the specified amount. The key features are:

| Feature | Description |
|---|---|
| `offset` parameter | Passed to the task constructor, available as `self._offset` |
| `find_unique_string_name()` | Generates unique names to avoid name/path collisions |
| `self._task_objects` | A dictionary to register objects managed by the task |
| `_move_task_objects_to_their_frame()` | Applies the offset to all registered objects |

```python linenums="1" hl_lines="10-12 14 25-26 30-34 47-52 54 101"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.string import find_unique_string_name  # Generate unique names
from isaacsim.core.utils.prims import is_prim_path_valid         # Check prim path existence
from isaacsim.core.api.objects.cuboid import VisualCuboid
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name, offset=None):
        super().__init__(name=name, offset=offset)
        self._task_event = 0
        # Add offset so each task instance has a different goal position
        self._jetbot_goal_position = np.array([1.3, 0.3, 0]) + self._offset
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
            offset=offset,  # Propagate the same offset to the subtask
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        # Generate unique names to avoid collisions across multiple instances
        jetbot_name = find_unique_string_name(
            initial_name="fancy_jetbot", is_unique_fn=lambda x: not self.scene.object_exists(x)
        )
        jetbot_prim_path = find_unique_string_name(
            initial_name="/World/Fancy_Jetbot", is_unique_fn=lambda x: not is_prim_path_valid(x)
        )
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path=jetbot_prim_path,
                name=jetbot_name,
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        # ── (A) Register Jetbot in _task_objects (for offset application later) ──
        self._task_objects[self._jetbot.name] = self._jetbot

        # ── (B) Adjust position of Franka created by the subtask ──
        # PickPlace subtask already placed Franka, but shift X+1.0 to separate from Jetbot
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        current_position, _ = self._franka.get_world_pose()
        self._franka.set_world_pose(position=current_position + np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=current_position + np.array([1.0, 0, 0]))

        # ── (C) Apply offset to all objects registered in _task_objects ──
        self._move_task_objects_to_their_frame()
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
        # Place the task with an offset
        world.add_task(RobotsPlaying(name="awesome_task", offset=np.array([0, -1.0, 0])))
        # Place a visual cube at the origin as a position reference
        VisualCuboid(
            prim_path="/new_cube_1",
            name="visual_cube",
            position=np.array([1.0, 0, 0.05]),
            scale=np.array([0.1, 0.1, 0.1]),
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._franka = self._world.scene.get_object(task_params["franka_name"]["value"])
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
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
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[-8.0, -8.0]))
        elif current_observations["task_event"] == 2:
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
            actions = self._franka_controller.forward(
                picking_position=current_observations[self._cube_name]["position"],
                placing_position=current_observations[self._cube_name]["target_position"],
                current_joint_positions=current_observations[self._franka.name]["joint_positions"],
            )
            self._franka.apply_action(actions)
        if self._franka_controller.is_done():
            self._world.pause()
        return
```

Note that `set_up_scene` deals with **two categories** of offset application:

| Target | How Offset is Applied | Description |
|---|---|---|
| Subtask objects (Franka, cube) | Pass `offset` to `PickPlace` **(done in the constructor)** | The subtask applies the offset internally via its own `_task_objects` and `_move_task_objects_to_their_frame()` |
| This task's objects (Jetbot) | Register in `_task_objects` → `_move_task_objects_to_their_frame()` **(A, C)** | Objects you add yourself must be registered and offset by yourself |

Step **(B)** is separate from offset application — it shifts Franka an additional 1.0 along the X axis so it doesn't overlap with Jetbot. This is an extra adjustment on top of the offset already applied by the subtask.

Save the code and verify the simulation:

1. Press **Ctrl+S** to save, then do **File > New From Stage Template > Empty** and click **LOAD**.
2. Press **PLAY** to observe the robots operating at a position offset by -1.0 along the Y axis.
3. Compare with the white cube near the origin to verify the task assets are offset.

## Running Multiple Tasks in Parallel

Now that the task is parameterized with `offset`, we can instantiate multiple copies and run them in parallel. Here we place 3 `RobotsPlaying` tasks side by side along the Y axis.

Key points when handling multiple tasks:

- **Make task event keys unique** — Prefix with the task name (`self.name + "_event"`) so observations from different tasks don't collide
- **Manage controllers in lists** — Store controllers corresponding to each task in lists
- **`world_cleanup()`** — Initialize lists during hot reload

```python linenums="1" hl_lines="14 21 64 97-105 108-111 113-128 134-138 141-162 164-170"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.string import find_unique_string_name
from isaacsim.core.utils.prims import is_prim_path_valid
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name, offset=None):
        super().__init__(name=name, offset=offset)
        self._task_event = 0
        self._jetbot_goal_position = np.array([np.random.uniform(1.2, 1.6), 0.3, 0]) + self._offset
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
            offset=offset,
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        jetbot_name = find_unique_string_name(
            initial_name="fancy_jetbot", is_unique_fn=lambda x: not self.scene.object_exists(x)
        )
        jetbot_prim_path = find_unique_string_name(
            initial_name="/World/Fancy_Jetbot", is_unique_fn=lambda x: not is_prim_path_valid(x)
        )
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path=jetbot_prim_path,
                name=jetbot_name,
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        # (A) Register Jetbot in _task_objects
        self._task_objects[self._jetbot.name] = self._jetbot
        # (B) Shift Franka created by subtask X+1.0 to separate from Jetbot
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        current_position, _ = self._franka.get_world_pose()
        self._franka.set_world_pose(position=current_position + np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=current_position + np.array([1.0, 0, 0]))
        # (C) Apply offset to all objects registered in _task_objects
        self._move_task_objects_to_their_frame()
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            # Use task name as prefix to avoid key collisions across multiple tasks
            self.name + "_event": self._task_event,
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
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
        # Manage controllers and objects for each task in lists
        self._tasks = []
        self._num_of_tasks = 3
        self._franka_controllers = []
        self._jetbot_controllers = []
        self._jetbots = []
        self._frankas = []
        self._cube_names = []
        return

    def setup_scene(self):
        world = self.get_world()
        # Place 3 tasks offset along the Y axis
        for i in range(self._num_of_tasks):
            world.add_task(RobotsPlaying(name="my_awesome_task_" + str(i), offset=np.array([0, (i * 2) - 3, 0])))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        for i in range(self._num_of_tasks):
            self._tasks.append(self._world.get_task(name="my_awesome_task_" + str(i)))
            task_params = self._tasks[i].get_params()
            self._frankas.append(self._world.scene.get_object(task_params["franka_name"]["value"]))
            self._jetbots.append(self._world.scene.get_object(task_params["jetbot_name"]["value"]))
            self._cube_names.append(task_params["cube_name"]["value"])
            self._franka_controllers.append(
                PickPlaceController(
                    name="pick_place_controller",
                    gripper=self._frankas[i].gripper,
                    robot_articulation=self._frankas[i],
                    events_dt=[0.008, 0.002, 0.5, 0.1, 0.05, 0.05, 0.0025, 1, 0.008, 0.08],
                )
            )
            self._jetbot_controllers.append(
                WheelBasePoseController(
                    name="cool_controller",
                    open_loop_wheel_controller=DifferentialController(
                        name="simple_control",
                        wheel_radius=0.03,
                        wheel_base=0.1125,
                    ),
                )
            )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        for i in range(len(self._tasks)):
            self._franka_controllers[i].reset()
            self._jetbot_controllers[i].reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        # Process all tasks in a loop
        for i in range(len(self._tasks)):
            if current_observations[self._tasks[i].name + "_event"] == 0:
                self._jetbots[i].apply_wheel_actions(
                    self._jetbot_controllers[i].forward(
                        start_position=current_observations[self._jetbots[i].name]["position"],
                        start_orientation=current_observations[self._jetbots[i].name]["orientation"],
                        goal_position=current_observations[self._jetbots[i].name]["goal_position"],
                    )
                )
            elif current_observations[self._tasks[i].name + "_event"] == 1:
                self._jetbots[i].apply_wheel_actions(ArticulationAction(joint_velocities=[-8.0, -8.0]))
            elif current_observations[self._tasks[i].name + "_event"] == 2:
                self._jetbots[i].apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
                actions = self._franka_controllers[i].forward(
                    picking_position=current_observations[self._cube_names[i]]["position"],
                    placing_position=current_observations[self._cube_names[i]]["target_position"],
                    current_joint_positions=current_observations[self._frankas[i].name]["joint_positions"],
                )
                self._frankas[i].apply_action(actions)
        return

    def world_cleanup(self):
        # Initialize lists during hot reload
        self._tasks = []
        self._franka_controllers = []
        self._jetbot_controllers = []
        self._jetbots = []
        self._frankas = []
        self._cube_names = []
        return
```

!!! note "Explicitly specifying `events_dt`"
    As explained in [Tutorial 4](04_adding_a_manipulator_robot.md), `events_dt` is a list that controls the execution speed of each state in `PickPlaceController`. When multiple Frankas operate simultaneously, the default values may cause timing mismatches and unstable behavior, so here we explicitly specify the values to synchronize the motion speed across all robots.

Save the code and verify the simulation:

1. Press **Ctrl+S** to save, then do **File > New From Stage Template > Empty** and click **LOAD**.
2. Press the **PLAY** button and observe 3 sets of Jetbot + Franka operating simultaneously side by side.

![Multiple tasks running in parallel](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## Summary

This tutorial covered the following topics:

1. **Spatial positioning** of tasks using the `offset` parameter
2. **Name collision avoidance** with `find_unique_string_name()`
3. **Offset management** with `_task_objects` and `_move_task_objects_to_their_frame()`
4. **Parallel management** of controllers and tasks using lists
5. **Hot reload support** with `world_cleanup()`

!!! tip "Further Reading"
    For an example of combining different types of tasks, refer to the standalone sample included with Isaac Sim: `standalone_examples/api/isaacsim.robot.manipulators/universal_robots/multiple_tasks.py`.

## Next Steps

Proceed to the next tutorial, "[Adding Props](07_adding_props.md)", to learn how to configure physics attributes on objects via the GUI.

!!! note "Note"
    The following tutorials continue to use the Extension Workflow for development. Converting to the Standalone Workflow follows the same approach as learned in [Hello World](01_hello_world.md).
