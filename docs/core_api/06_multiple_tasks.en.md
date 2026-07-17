---
title: Multiple Robot Scenarios
---

# Multiple Robot Scenarios

!!! note "About the former title, Multiple Tasks"
    In Isaac Sim 6.0, the official tutorial was renamed from "Multiple Tasks" to "Multiple Robot Scenarios", and its content was overhauled from a Task-class-based approach to scenario management with Python classes. This page has been updated accordingly.

## Learning Objectives

After completing this tutorial, you will have learned:

- How to organize robot scenarios into reusable Python classes
- How to position multiple scenarios in the world using an `offset` parameter
- How to run multiple scenarios in parallel with a simple loop
- Adding randomization to scenario parameters
- Best practices for managing multiple robot instances

## Getting Started

### Prerequisites

- Completed [Tutorial 5: Adding Multiple Robots](05_adding_multiple_robots.md)

### Estimated Time

Approximately 15–20 minutes

### Preparing the Source Code

In this tutorial, you continue editing `hello_world.py` from the Hello World example. If you are continuing from the previous tutorial, proceed as is. If you are resuming on another day, open the source code with the following steps.

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > General > Hello World**.
3. Click the **Open Source Code** button to open `hello_world.py` in Visual Studio Code.

For detailed steps, see the ["Opening the Hello World Example" section of Hello World](01_hello_world.md).

!!! warning "Caution"
    Pressing **STOP**, then **PLAY** might not reset the world properly. Use the **RESET** button instead when restarting the simulation.

## Organizing Robot Scenarios with Classes

When working with multiple robots performing similar tasks, it's helpful to encapsulate the robot setup and control logic into **reusable classes**. This approach allows you to easily create multiple instances with different parameters (like position offsets).

Organize the sequence from the previous tutorial ("the Jetbot pushes the cube to the Franka, which picks it up") into a `RobotScenario` class:

| Method | Role |
|---|---|
| `setup_scene()` | Creates the robots and cube for this scenario (taking `offset` into account) |
| `initialize()` | Creates the articulation handles after the scene loads |
| `step()` | Executes one step of the scenario logic (state machine) |
| `reset()` | Resets the scenario state |

```python linenums="1" hl_lines="11-23 25-56 58-62 71-95 139-170"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.objects import Cube, DomeLight, GroundPlane
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationEvent, SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.robot.experimental.manipulators.examples.franka import Franka
from isaacsim.storage.native import get_assets_root_path


class RobotScenario:
    """Encapsulates a Jetbot + Franka + Cube scenario with an offset."""

    def __init__(self, name: str, offset: np.ndarray = np.array([0.0, 0.0, 0.0])):
        self.name = name
        self.offset = offset
        self.state = 0
        self.step_counter = 0
        self.pick_phase = 0
        self.jetbot = None
        self.franka = None
        self.cube = None
        self.cube_goal = np.array([1.2, 0.0, 0.0]) + offset

    def setup_scene(self):
        """Create the robots and cube for this scenario."""
        assets_root_path = get_assets_root_path()
        base_path = f"/World/{self.name}"

        # Add Jetbot
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path=f"{base_path}/Jetbot",
        )
        jetbot_xform = XformPrim(f"{base_path}/Jetbot")
        jetbot_xform.reset_xform_op_properties()
        jetbot_xform.set_world_poses(positions=self.offset.tolist())

        # Add cube in front of Jetbot
        cube_pos = self.offset + np.array([0.15, 0.0, 0.025])
        cube_shape = Cube(
            paths=f"{base_path}/Cube",
            positions=cube_pos.tolist(),
            sizes=1.0,
            scales=[0.05, 0.05, 0.05],
            colors="red",
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)

        # Add Franka
        franka_pos = self.offset + np.array([0.8, -0.3, 0.0])
        self.franka = Franka(robot_path=f"{base_path}/Franka", create_robot=True)
        franka_xform = XformPrim(f"{base_path}/Franka")
        franka_xform.reset_xform_op_properties()
        franka_xform.set_world_poses(positions=franka_pos.tolist())

    def initialize(self):
        """Initialize articulation handles after scene load."""
        base_path = f"/World/{self.name}"
        self.jetbot = Articulation(f"{base_path}/Jetbot")
        self.cube = RigidPrim(f"{base_path}/Cube")

    def reset(self):
        """Reset the scenario state."""
        self.state = 0
        self.step_counter = 0
        self.pick_phase = 0
        self.franka.reset_to_default_pose()

    def step(self):
        """Execute one step of the scenario logic."""
        if self.state == 0:
            # Jetbot pushes cube
            cube_pos = self.cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self.cube_goal[:2]) > 0.05:
                self.jetbot.set_dof_velocity_targets([10.0, 10.0])
            else:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 1
                self.step_counter = 0

        elif self.state == 1:
            # Jetbot backs up
            self.jetbot.set_dof_velocity_targets([-8.0, -8.0])
            self.step_counter += 1
            if self.step_counter > 100:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 2
                self.step_counter = 0
                self.franka.open_gripper()

        elif self.state == 2:
            # Franka pick-and-place
            self._franka_pick_place()

    def _franka_pick_place(self):
        """Execute Franka pick-and-place state machine."""
        cube_pos = self.cube.get_world_poses()[0].numpy()[0]
        down_orient = self.franka.get_downward_orientation()
        self.step_counter += 1

        if self.pick_phase == 0:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]), down_orient)
            if self.step_counter > 120:
                self.pick_phase = 1
                self.step_counter = 0
        elif self.pick_phase == 1:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]), down_orient)
            if self.step_counter > 100:
                self.pick_phase = 2
                self.step_counter = 0
        elif self.pick_phase == 2:
            self.franka.close_gripper()
            if self.step_counter > 100:
                self.pick_phase = 3
                self.step_counter = 0
        elif self.pick_phase == 3:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.08])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 4
        elif self.pick_phase == 4:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.01])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 5
        elif self.pick_phase == 5:
            self.franka.open_gripper()
            if self.step_counter > 150:
                self.step_counter = 0
                self.state = 6  # Done


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._scenarios = []

    def setup_scene(self):
        GroundPlane("/World/ground_plane")
        dome_light = DomeLight("/World/DomeLight")
        dome_light.set_intensities(1000)

        # Create a single scenario
        self._scenario = RobotScenario(name="scenario_0", offset=np.array([0.0, 0.0, 0.0]))
        self._scenario.setup_scene()

    async def setup_post_load(self):
        self._scenario.initialize()

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, event=SimulationEvent.PHYSICS_POST_STEP
        )

    def physics_step(self, dt, context):
        self._scenario.step()

    async def setup_post_reset(self):
        self._scenario.reset()

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

!!! note "Use unique prim paths per scenario"
    `RobotScenario` builds **unique prim paths** like `/World/scenario_0/Jetbot` from the scenario name. This prevents prim path collisions when adding multiple scenarios.

Press **Ctrl+S** to save, then run **File > New From Stage Template > Empty** → **LOAD**. One Jetbot + Franka pair performs the cube handover.

![Running a robot scenario](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_6_1.webp)

## Scaling to Multiple Scenarios

Now that the scenario is a class, you can run multiple instances in parallel simply by creating them in a loop. Apply the following changes.

Set the number of scenarios:

```python linenums="1"
        self._num_scenarios = 3  # Number of parallel scenarios
```

Create the scenarios:

```python linenums="1"
        # Create multiple scenarios with Y-axis offsets
        for i in range(self._num_scenarios):
            offset = np.array([0.0, (i - 1) * 2.0, 0.0])  # Spread along Y-axis
            scenario = RobotScenario(name=f"scenario_{i}", offset=offset, randomize=False)
            scenario.setup_scene()
            self._scenarios.append(scenario)
```

Initialize the scenarios:

```python linenums="1"
        # Initialize all scenarios
        for scenario in self._scenarios:
            scenario.initialize()
```

Step all scenarios:

```python linenums="1"
        # Step all scenarios
        for scenario in self._scenarios:
            scenario.step()
```

Reset all scenarios:

```python linenums="1"
        # Reset all scenarios
        for scenario in self._scenarios:
            scenario.reset()
```

Clean up:

```python linenums="1"
        self._scenarios = []
```

The complete code is as follows (the `RobotScenario` class also gains a `randomize` parameter used in the next section):

```python linenums="1" hl_lines="14 19 26-31 152-154 161-168 171-175 182-186 189-193 200-201"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.objects import Cube, DomeLight, GroundPlane
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationEvent, SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.robot.experimental.manipulators.examples.franka import Franka
from isaacsim.storage.native import get_assets_root_path


class RobotScenario:
    """Encapsulates a Jetbot + Franka + Cube scenario with an offset."""

    def __init__(self, name: str, offset: np.ndarray = np.array([0.0, 0.0, 0.0]), randomize: bool = False):
        self.name = name
        self.offset = offset
        self.state = 0
        self.step_counter = 0
        self.randomize = randomize
        self.pick_phase = 0
        self.jetbot = None
        self.franka = None
        self.cube = None
        self.cube_goal = np.array([1.2, 0.0, 0.0]) + offset

        # Randomize cube goal position if enabled
        if self.randomize:
            random_x = np.random.uniform(1.0, 1.6)
            self.cube_goal = np.array([random_x, 0.0, 0.0]) + offset
        else:
            self.cube_goal = np.array([1.2, 0.0, 0.0]) + offset

    def setup_scene(self):
        """Create the robots and cube for this scenario."""
        assets_root_path = get_assets_root_path()
        base_path = f"/World/{self.name}"

        # Add Jetbot
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path=f"{base_path}/Jetbot",
        )
        jetbot_xform = XformPrim(f"{base_path}/Jetbot")
        jetbot_xform.reset_xform_op_properties()
        jetbot_xform.set_world_poses(positions=self.offset.tolist())

        # Add cube in front of Jetbot
        cube_pos = self.offset + np.array([0.15, 0.0, 0.025])
        cube_shape = Cube(
            paths=f"{base_path}/Cube",
            positions=cube_pos.tolist(),
            sizes=1.0,
            scales=[0.05, 0.05, 0.05],
            colors="red",
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)

        # Add Franka
        franka_pos = self.offset + np.array([0.8, -0.3, 0.0])
        self.franka = Franka(robot_path=f"{base_path}/Franka", create_robot=True)
        franka_xform = XformPrim(f"{base_path}/Franka")
        franka_xform.reset_xform_op_properties()
        franka_xform.set_world_poses(positions=franka_pos.tolist())

    def initialize(self):
        """Initialize articulation handles after scene load."""
        base_path = f"/World/{self.name}"
        self.jetbot = Articulation(f"{base_path}/Jetbot")
        self.cube = RigidPrim(f"{base_path}/Cube")

    def reset(self):
        """Reset the scenario state."""
        self.state = 0
        self.step_counter = 0
        self.pick_phase = 0
        self.franka.reset_to_default_pose()

    def step(self):
        """Execute one step of the scenario logic."""
        if self.state == 0:
            # Jetbot pushes cube
            cube_pos = self.cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self.cube_goal[:2]) > 0.05:
                self.jetbot.set_dof_velocity_targets([10.0, 10.0])
            else:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 1
                self.step_counter = 0

        elif self.state == 1:
            # Jetbot backs up
            self.jetbot.set_dof_velocity_targets([-8.0, -8.0])
            self.step_counter += 1
            if self.step_counter > 100:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 2
                self.step_counter = 0
                self.franka.open_gripper()

        elif self.state == 2:
            # Franka pick-and-place
            self._franka_pick_place()

    def _franka_pick_place(self):
        """Execute Franka pick-and-place state machine."""
        cube_pos = self.cube.get_world_poses()[0].numpy()[0]
        down_orient = self.franka.get_downward_orientation()
        self.step_counter += 1

        if self.pick_phase == 0:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]), down_orient)
            if self.step_counter > 120:
                self.pick_phase = 1
                self.step_counter = 0
        elif self.pick_phase == 1:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]), down_orient)
            if self.step_counter > 100:
                self.pick_phase = 2
                self.step_counter = 0
        elif self.pick_phase == 2:
            self.franka.close_gripper()
            if self.step_counter > 100:
                self.pick_phase = 3
                self.step_counter = 0
        elif self.pick_phase == 3:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.08])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 4
        elif self.pick_phase == 4:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.01])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 5
        elif self.pick_phase == 5:
            self.franka.open_gripper()
            if self.step_counter > 150:
                self.step_counter = 0
                self.state = 6  # Done


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._scenarios = []
        # -- Begin setting scenario number -- #
        self._num_scenarios = 3  # Number of parallel scenarios
        # -- End of setting scenario number -- #

    def setup_scene(self):
        GroundPlane("/World/ground_plane")
        dome_light = DomeLight("/World/DomeLight")
        dome_light.set_intensities(1000)

        # -- Begin creating scenarios -- #
        # Create multiple scenarios with Y-axis offsets
        for i in range(self._num_scenarios):
            offset = np.array([0.0, (i - 1) * 2.0, 0.0])  # Spread along Y-axis
            scenario = RobotScenario(name=f"scenario_{i}", offset=offset, randomize=False)
            scenario.setup_scene()
            self._scenarios.append(scenario)
        # -- End of creating scenarios -- #

    async def setup_post_load(self):
        # -- Begin initializing scenarios -- #
        # Initialize all scenarios
        for scenario in self._scenarios:
            scenario.initialize()
        # -- End of initializing scenarios -- #

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, event=SimulationEvent.PHYSICS_POST_STEP
        )

    def physics_step(self, dt, context):
        # -- Begin stepping scenarios -- #
        # Step all scenarios
        for scenario in self._scenarios:
            scenario.step()
        # -- End of stepping scenarios -- #

    async def setup_post_reset(self):
        # -- Begin resetting scenarios -- #
        # Reset all scenarios
        for scenario in self._scenarios:
            scenario.reset()
        # -- End of resetting scenarios -- #

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
        # -- Begin remove all scenarios -- #
        self._scenarios = []
        # -- End of remove all scenarios -- #
```

Save the code and check the simulation:

1. Press **Ctrl+S** to save, then run **File > New From Stage Template > Empty** → **LOAD**.
2. Watch three Jetbot + Franka pairs operate side by side simultaneously.

![Multiple scenarios running in parallel](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_6_2.webp)

## Adding Randomization

To make simulations more interesting, you can add **randomization** to the scenario parameters. When the `randomize` constructor parameter is enabled, `RobotScenario` randomly samples the cube goal position. Set `randomize=True` when creating each scenario in `setup_scene`:

```python linenums="1"
for i in range(self._num_scenarios):
    offset = np.array([0.0, (i - 1) * 2.0, 0.0])  # Spread along Y-axis
    scenario = RobotScenario(name=f"scenario_{i}", offset=offset, randomize=True)
    scenario.setup_scene()
    self._scenarios.append(scenario)
```

This changes how far each Jetbot pushes its cube, so you can see the scenarios progress differently.

## Best Practices for Scaling

When creating large-scale multi-robot simulations:

- **Use unique paths**: Each scenario should use unique USD prim paths to avoid conflicts. The `RobotScenario` class uses the scenario name to create unique paths like `/World/scenario_0/Jetbot`.
- **Manage state independently**: Each scenario instance maintains its own state variables, allowing scenarios to progress independently.
- **Clean up properly**: The `physics_cleanup` method ensures callbacks are deregistered and scenario lists are cleared when the simulation is stopped.
- **Consider performance**: With many scenarios, consider reducing physics step frequency or using GPU-accelerated simulation for better performance.

## Summary

This tutorial covered the following topics:

1. Organizing robot scenarios into **reusable Python classes**
2. Using the `offset` parameter to **position multiple scenarios** in the world
3. **Scaling to multiple parallel scenarios** with a simple loop
4. Adding **randomization** to scenario parameters
5. **Best practices** for managing multiple robot instances

## Next Steps

Continue to the next tutorial, [Adding Props](07_adding_props.md), to learn how to configure physics attributes on objects via the GUI.

!!! note "Note"
    The following tutorials also mainly use the Extension Workflow for development. Converting to the Standalone Workflow follows the same steps you learned in [Hello World](01_hello_world.md).
