---
title: Adding Multiple Robots
---

# Adding Multiple Robots

## Learning Objectives

After completing this tutorial, you will have learned:

- How to add different types of robots (a mobile robot and a manipulator) to the same simulation
- How to create pushable objects with `Cube`, `GeomPrim`, and `RigidPrim`
- How to control different robot types with the `Articulation` class
- How to coordinate robot actions using state machine logic
- IK-based end-effector control and gripper operations with the `Franka` class

## Getting Started

### Prerequisites

- Completed [Tutorial 4: Adding a Manipulator Robot](04_adding_a_manipulator_robot.md)

### Estimated Time

Approximately 15–20 minutes

### Preparing the Source Code

In this tutorial, we return to the Extension Workflow and edit `hello_world.py` from the Hello World example. Open the source code with the following steps.

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > General > Hello World**.
3. Click the **Open Source Code** button to open `hello_world.py` in Visual Studio Code.

For detailed steps, see the ["Opening the Hello World Example" section of Hello World](01_hello_world.md#opening-the-hello-world-example).

!!! warning "Caution"
    Pressing **STOP**, then **PLAY** might not reset the world properly. Use the **RESET** button instead when restarting the simulation.

## Overall Flow

In this tutorial, you incrementally build a simulation where the Jetbot and Franka work together to perform the following sequence:

1. The **Jetbot** pushes a cube close to the Franka
2. The **Jetbot** backs up to give the Franka working space
3. The **Franka** picks up the cube and places it at a target position

The code is implemented in three stages.

## Step 1: Creating the Scene

First, place the Jetbot, Franka, and cube from the previous tutorials in the scene. Load the robot assets with `stage_utils.add_reference_to_stage()` and adjust the Franka's position with `XformPrim`.

```python linenums="1" hl_lines="14-54 56-63"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

    # -- Begin setup_scene -- #
    def setup_scene(self):
        assets_root_path = get_assets_root_path()

        # Add ground plane
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Add Jetbot mobile robot
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path="/World/Jetbot",
        )

        # Add a cube in front of Jetbot for it to push
        visual_material = PreviewSurfaceMaterial("/World/Materials/red")
        visual_material.set_input_values("diffuseColor", [1.0, 0.0, 0.0])
        cube_shape = Cube(
            paths="/World/Cube",
            positions=np.array([[0.15, 0.0, 0.025]]),  # In front of Jetbot
            sizes=[1.0],
            scales=np.array([[0.05, 0.05, 0.05]]),
            reset_xform_op_properties=True,
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)
        cube_shape.apply_visual_materials(visual_material)

        # Add Franka manipulator at a position the Jetbot will push the cube to
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
            path="/World/Franka",
        )

        # Position Franka so the cube will be pushed into its workspace
        franka_xform = XformPrim("/World/Franka")
        franka_xform.set_world_poses(positions=np.array([[0.8, -0.5, 0.0]]))

    # -- End of setup_scene -- #

    async def setup_post_load(self):
        # Create Articulation handles for both robots
        self._jetbot = Articulation("/World/Jetbot")
        self._franka = Articulation("/World/Franka")

        # Print robot info
        print(f"Jetbot DOFs: {self._jetbot.num_dofs}, names: {self._jetbot.dof_names}")
        print(f"Franka DOFs: {self._franka.num_dofs}, names: {self._franka.dof_names}")
```

Key points of this code:

| Operation | Description |
|---|---|
| `stage_utils.add_reference_to_stage()` | Places USD assets on the stage, regardless of robot type |
| `XformPrim.set_world_poses()` | Sets the world pose of a prim (used here to place the Franka) |
| `Articulation` | Both the Jetbot (2 DOFs) and the Franka (9 DOFs) can be wrapped and controlled with the same class |

Press **Ctrl+S** to save, then run **File > New From Stage Template > Empty** → **LOAD** to see both robots and the cube in the scene.

## Step 2: Controlling Multiple Robots

Next, add physics callbacks to control both robots simultaneously. Start simple: the Jetbot pushes the cube forward and stops after a fixed number of steps.

The control logic is as follows:

```python linenums="1"
        self._step_counter += 1
        if self._step_counter < 300:
            # Drive Jetbot forward to push the cube
            self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
        else:
            # Stop the Jetbot after pushing
            self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
```

The complete code is as follows:

```python linenums="1" hl_lines="6 14-15 57-61 63-68 70-79 81-84"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._step_counter = 0

    def setup_scene(self):
        assets_root_path = get_assets_root_path()

        # Add ground plane
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Add Jetbot mobile robot
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path="/World/Jetbot",
        )

        # Add a cube in front of Jetbot for it to push
        visual_material = PreviewSurfaceMaterial("/World/Materials/red")
        visual_material.set_input_values("diffuseColor", [1.0, 0.0, 0.0])
        cube_shape = Cube(
            paths="/World/Cube",
            positions=np.array([[0.15, 0.0, 0.025]]),
            sizes=[1.0],
            scales=np.array([[0.05, 0.05, 0.05]]),
            reset_xform_op_properties=True,
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)
        cube_shape.apply_visual_materials(visual_material)

        # Add Franka manipulator
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
            path="/World/Franka",
        )

        # Position Franka forward and to the right of Jetbot's path
        franka_xform = XformPrim("/World/Franka")
        franka_xform.set_world_poses(positions=np.array([[0.8, -0.5, 0.0]]))

    async def setup_post_load(self):
        # Create Articulation handles
        self._jetbot = Articulation("/World/Jetbot")
        self._franka = Articulation("/World/Franka")
        self._cube = RigidPrim("/World/Cube")
        self._step_counter = 0

        # Register physics callback
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, IsaacEvents.POST_PHYSICS_STEP
        )

    def physics_step(self, dt, context):
        # -- Begin control Jetbot -- #
        self._step_counter += 1
        if self._step_counter < 300:
            # Drive Jetbot forward to push the cube
            self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
        else:
            # Stop the Jetbot after pushing
            self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
        # -- End of control Jetbot -- #

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

Save the code and run **LOAD** to watch the Jetbot push the cube towards the Franka.

![Jetbot pushing the cube](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_5_1.webp)

## Step 3: Adding State Machine Logic

Finally, create a state machine to coordinate the two robots: first the Jetbot pushes the cube towards the Franka, then backs up to give space, and finally the Franka executes a full pick-and-place sequence using the `Franka` class (see Tutorial 4) for IK-based end-effector control.

The state transitions are as follows:

| State | Action | Transition condition |
|---|---|---|
| `0` | Jetbot pushes the cube to the goal position | Once the cube is close enough to the goal, go to `1` |
| `1` | Jetbot backs up | After 100 steps, go to `2` (open the gripper) |
| `2` | Franka executes pick-and-place | Subdivided by `_pick_phase` (0–5) |

The core of the state machine is as follows:

```python linenums="1"
        if self._state == 0:
            # Jetbot pushes cube to Franka
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self._cube_goal[:2]) > 0.05:
                self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
            else:
                self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
                print("Cube delivered! Backing up...")
                self._state = 1
                self._step_counter = 0

        elif self._state == 1:
            # Jetbot backs up
            self._jetbot.set_dof_velocity_targets([[-8.0, -8.0]])
            self._step_counter += 1
            if self._step_counter > 100:
                self._jetbot.set_dof_velocity_targets(np.array([[0.0, 0.0]]))
                print("Franka starting pick-and-place...")
                self._state = 2
                self._step_counter = 0
                self._franka.open_gripper()

        elif self._state == 2:
            # Franka pick-and-place sequence using step counter
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            down_orient = self._franka.get_downward_orientation()
            self._step_counter += 1

            if self._pick_phase == 0:
                # Move above cube (wait 120 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]]), down_orient
                )
                if self._step_counter > 120:
                    self._pick_phase = 1
                    self._step_counter = 0
            elif self._pick_phase == 1:
                # Lower to cube (wait 100 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]]), down_orient
                )
                if self._step_counter > 100:
                    self._franka.close_gripper()
                    self._pick_phase = 2
                    self._step_counter = 0
            elif self._pick_phase == 2:
                # Close the gripper (wait 50 steps)
                self._franka.close_gripper()
                if self._step_counter > 50:
                    self._pick_phase = 3
                    self._step_counter = 0
            elif self._pick_phase == 3:
                # Lift cube (wait 100 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.25]]), down_orient
                )
                if self._step_counter > 100:
                    self._pick_phase = 4
                    self._step_counter = 0
            elif self._pick_phase == 4:
                # Move to target (wait 150 steps)
                self._franka.set_end_effector_pose(np.array([[0.3, 0.3, 0.15]]), down_orient)
                if self._step_counter > 150:
                    self._franka.open_gripper()
                    self._pick_phase = 5
                    self._step_counter = 0
            elif self._pick_phase == 5:
                # Lift the arm (wait 150 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.5]]), down_orient
                )
                if self._step_counter > 150:
                    self._step_counter = 0
```

The complete code is as follows:

```python linenums="1" hl_lines="8 16 47-50 52-57 66-141 143-147"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.robot.experimental.manipulators.examples.franka import Franka
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._state = 0

    def setup_scene(self):
        assets_root_path = get_assets_root_path()

        # Add ground plane
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Add Jetbot at origin
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path="/World/Jetbot",
        )

        # Add cube in front of Jetbot
        visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
        visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])
        cube_shape = Cube(
            paths="/World/Cube",
            positions=np.array([[0.15, 0.0, 0.0258]]),
            sizes=[1.0],
            scales=np.array([[0.05, 0.05, 0.05]]),
            reset_xform_op_properties=True,
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)
        cube_shape.apply_visual_materials(visual_material)

        # Add Franka using Franka for IK and gripper control
        self._franka = Franka(robot_path="/World/Franka", create_robot=True)
        franka_xform = XformPrim("/World/Franka")
        franka_xform.set_world_poses(positions=[[0.8, -0.3, 0.0]])

    async def setup_post_load(self):
        self._jetbot = Articulation("/World/Jetbot")
        self._cube = RigidPrim("/World/Cube")
        self._cube_goal = np.array([1.2, 0.0, 0.0])  # Target: Franka reaches from the side
        self._step_counter = 0
        self._pick_phase = 0

        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, IsaacEvents.POST_PHYSICS_STEP
        )
        self._state = 0

    def physics_step(self, dt, context):
        # -- Begin state machine -- #
        if self._state == 0:
            # Jetbot pushes cube to Franka
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self._cube_goal[:2]) > 0.05:
                self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
            else:
                self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
                print("Cube delivered! Backing up...")
                self._state = 1
                self._step_counter = 0

        elif self._state == 1:
            # Jetbot backs up
            self._jetbot.set_dof_velocity_targets([[-8.0, -8.0]])
            self._step_counter += 1
            if self._step_counter > 100:
                self._jetbot.set_dof_velocity_targets(np.array([[0.0, 0.0]]))
                print("Franka starting pick-and-place...")
                self._state = 2
                self._step_counter = 0
                self._franka.open_gripper()

        elif self._state == 2:
            # Franka pick-and-place sequence using step counter
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            down_orient = self._franka.get_downward_orientation()
            self._step_counter += 1

            if self._pick_phase == 0:
                # Move above cube (wait 120 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]]), down_orient
                )
                if self._step_counter > 120:
                    self._pick_phase = 1
                    self._step_counter = 0
            elif self._pick_phase == 1:
                # Lower to cube (wait 100 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]]), down_orient
                )
                if self._step_counter > 100:
                    self._franka.close_gripper()
                    self._pick_phase = 2
                    self._step_counter = 0
            elif self._pick_phase == 2:
                # Close the gripper (wait 50 steps)
                self._franka.close_gripper()
                if self._step_counter > 50:
                    self._pick_phase = 3
                    self._step_counter = 0
            elif self._pick_phase == 3:
                # Lift cube (wait 100 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.25]]), down_orient
                )
                if self._step_counter > 100:
                    self._pick_phase = 4
                    self._step_counter = 0
            elif self._pick_phase == 4:
                # Move to target (wait 150 steps)
                self._franka.set_end_effector_pose(np.array([[0.3, 0.3, 0.15]]), down_orient)
                if self._step_counter > 150:
                    self._franka.open_gripper()
                    self._pick_phase = 5
                    self._step_counter = 0
            elif self._pick_phase == 5:
                # Lift the arm (wait 150 steps)
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.5]]), down_orient
                )
                if self._step_counter > 150:
                    self._step_counter = 0
        # -- End of state machine -- #

    async def setup_post_reset(self):
        self._state = 0
        self._step_counter = 0
        self._pick_phase = 0
        self._franka.reset_to_default_pose()

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

!!! note "When to use Articulation vs. the Franka class"
    The Jetbot only needs velocity commands, so it is wrapped with the generic `Articulation` class. The Franka needs IK and gripper control, so it uses the `Franka` class (a derivative of `Articulation`) covered in Tutorial 4. Also, resetting the state variables and calling `reset_to_default_pose()` in `setup_post_reset` allows you to restart from the beginning with the **RESET** button.

Save the code and check the simulation:

1. Press **Ctrl+S** to save, then run **File > New From Stage Template > Empty** → **LOAD**.
2. Verify the following sequence of actions:
    - The Jetbot pushes the cube close to the Franka
    - The Jetbot backs up out of the way
    - The Franka picks up the cube and places it at the target position

![Multiple robots working together](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_5_2.webp)

## Summary

This tutorial covered the following topics:

1. Adding **multiple robots and objects (cube)** to the same scene
2. **Creating pushable objects** with `Cube`, `GeomPrim`, and `RigidPrim`
3. Controlling different robot types with the **Articulation class**
4. Having a mobile robot (Jetbot) **push objects** towards a manipulator (Franka)
5. Building **state machine logic** to coordinate pushing, backing up, and picking
6. IK-based end-effector control and gripper operations with the **Franka class**

## Next Steps

Continue to the next tutorial, [Multiple Robot Scenarios](06_multiple_tasks.md), to learn how to organize robot scenarios into classes and run multiple instances in parallel.
