---
title: Hello Robot
---

# Hello Robot

## Learning Objectives

After completing this tutorial, you will have learned:

- How to load robot assets from a Nucleus Server into a simulation scene
- How to wrap robot primitives with the `Robot` class for high-level API access
- How to control articulation joints through velocity commands to move a robot
- How to use physics callbacks to continuously apply actions during simulation
- How to use the `WheeledRobot` class for simplified wheeled robot control

## Getting Started

### Prerequisites

- Complete [Tutorial 1: Hello World](01_hello_world.md) before starting this tutorial.
- A configured Omniverse Nucleus server with the `/Isaac` folder is required.

### Estimated Time

Approximately 10-15 minutes.

### Preparing the Source Code

This tutorial continues editing the `hello_world.py` file from the Hello World sample. If you are continuing from the previous tutorial, you can proceed as-is. If you are resuming on a different day, follow these steps to open the source code:

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > General > Hello World**.
3. Click the **Open Source Code** button to open `hello_world.py` in Visual Studio Code.

For detailed instructions, refer to the ["Opening the Hello World Sample" section](01_hello_world.md#opening-the-hello-world-sample) in Hello World.

## Adding a Robot to the Scene

In the previous tutorial, we added a cube to the scene. This time, we will add a robot. We will use NVIDIA's **Jetbot**, a two-wheeled differential drive robot.

??? info "Adding a robot via GUI (click to expand)"
    You can also add a robot to the scene by dragging and dropping from the Isaac Sim Assets browser, without writing any Python code.

    1. Click **Window > Browsers > Isaac Sim Assets** to enable the Isaac Sim Assets window.<br>
       ![Enable the Isaac Sim Assets window](images/09_isaac_sim_assets_browser.png)

        !!! warning "First launch note"
            When opening the Isaac Sim Assets window for the first time, asset data will be downloaded, which may take a significant amount of time. Depending on your network environment, this could take several minutes or more.

    2. Type "Jetbot" in the search bar and drag and drop the Jetbot asset into the viewport.<br>
       ![Drag and drop Jetbot](images/10_drag_and_drop_jetbot.webp)

    This method is convenient for quickly placing robots, but learning the Python API approach allows you to dynamically add and control robots programmatically. The following sections explain the Python API approach.

### Adding a Robot via Python API

Robot assets are stored on the Omniverse Nucleus server. We use `get_assets_root_path()` to get the root path of assets, and `add_reference_to_stage()` to load the asset into the USD Stage.

However, `add_reference_to_stage()` alone only places the robot's 3D model and physics properties on the Stage. It does not provide **robot-level control** such as querying joint positions or sending velocity commands. To do that, you would need to directly manipulate low-level USD or PhysX APIs.

To enable high-level control, we wrap the loaded robot prim with the `Robot` class and register it with `world.scene.add()`. The `Robot` class **only references** the existing prim — it does not copy or transform it. It creates a Python object that provides high-level APIs like `get_joint_positions()` and `apply_action()` for the same `/World/Fancy_Robot` prim.

| Operation | Role |
|---|---|
| `add_reference_to_stage()` | Creates the robot prim on the USD Stage |
| `Robot(prim_path=...)` | Creates a Python wrapper that references the existing prim and provides high-level APIs |
| `world.scene.add()` | Registers the wrapper with the Scene, enabling integration with the World lifecycle (reset/step) |

```python linenums="1" hl_lines="2-4 17-30 33-37"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path  # Get Nucleus asset path
from isaacsim.core.utils.stage import add_reference_to_stage   # Add asset to USD Stage
from isaacsim.core.api.robots import Robot                     # Robot high-level API class
import carb


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()

        # Get the root path of the /Isaac folder from the Nucleus server
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            # Use carb to log warnings, errors, and infos to the terminal
            carb.log_error("Could not find nucleus server with /Isaac folder")

        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        # Create a new XFormPrim that references the USD file
        # Similar to how pointers work in memory
        add_reference_to_stage(usd_path=asset_path, prim_path="/World/Fancy_Robot")

        # Wrap the Jetbot prim root with the Robot class and add it to the Scene
        # This enables high-level API access for setting/getting attributes
        # and initializing physics handles
        # Note: this call does NOT create the Jetbot in the stage
        #       it was already created by add_reference_to_stage
        jetbot_robot = world.scene.add(
            Robot(prim_path="/World/Fancy_Robot", name="fancy_robot")
        )

        # Before a reset, articulation information is not accessible (physics handles not initialized)
        # setup_post_load is called after the first reset, so we can access it there
        print("Num of degrees of freedom before first reset: " + str(jetbot_robot.num_dof))  # Prints None
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        # After the first reset, articulation information is accessible
        print("Num of degrees of freedom after first reset: " + str(self._jetbot.num_dof))  # Prints 2
        print("Joint Positions after first reset: " + str(self._jetbot.get_joint_positions()))
        return
```

!!! info "About References"
    `add_reference_to_stage()` adds the USD file as a **Reference** to the Stage. It maintains a link to the original file, so any changes to the asset are automatically reflected. While it is also possible to directly copy USD content into the Stage, the reference approach is standard practice for loading robot assets.

Save the code and verify the simulation:

1. Press **Ctrl+S** to save the code and hot-reload Isaac Sim.
2. Reopen the Hello World sample extension window.
3. Click **File > New From Stage Template > Empty** to create a new world, then click **LOAD**.
4. Check the terminal output.

### Important Note on Physics Handles

Notice that the `num_dof` (number of degrees of freedom) value differs between `setup_scene` and `setup_post_load`.

| Timing | `num_dof` Value | Reason |
|---|---|---|
| `setup_scene` (before reset) | `None` | Physics handles not initialized |
| `setup_post_load` (after reset) | `2` | Physics handles initialized (left and right wheels) |

!!! warning "Warning"
    Articulation properties (degrees of freedom, joint positions, etc.) cannot be accessed until the first reset is performed. Always query these properties in `setup_post_load` or later.

## Moving the Robot

Next, we will send velocity commands to the Jetbot's wheels to make it move.

Robot motion control uses the **ArticulationController**. It acts as an **implicit PD controller**, enabling PD gain settings, action application, and control mode switching.

??? info "What is an implicit PD controller? (click to expand)"
    On a real robot, when you specify a "target position" or "target velocity" to a motor, a controller inside the motor driver computes the current (torque) based on the error between the target and current values to move the joint.

    The physics engine in Isaac Sim (PhysX) has the same mechanism built in. When you specify target values via `joint_positions` or `joint_velocities`, PhysX internally performs **PD control (Proportional-Derivative control)** and automatically computes the forces needed to track the target.

    $$
    F = K_p \cdot (x_{\text{target}} - x_{\text{current}}) + K_d \cdot (\dot{x}_{\text{target}} - \dot{x}_{\text{current}})
    $$

    This PD controller is not explicitly implemented by the user but is **implicitly** built into the physics engine — hence the term "implicit PD controller." The gains $K_p$ (proportional) and $K_d$ (derivative) can be tuned through the `ArticulationController`.

`ArticulationAction` accepts the following three parameters:

| Parameter | Description |
|---|---|
| `joint_positions` | Target position for each joint |
| `joint_velocities` | Target velocity for each joint |
| `joint_efforts` | Torque/force applied to each joint |

Each parameter accepts `numpy` arrays, `list`s, or `None` (no command sent for that degree of freedom in this step).

```python linenums="1" hl_lines="2 30-33 36-37 39-47"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.types import ArticulationAction  # Data type for joint commands
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot
import numpy as np
import carb


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find nucleus server with /Isaac folder")
        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        add_reference_to_stage(usd_path=asset_path, prim_path="/World/Fancy_Robot")
        jetbot_robot = world.scene.add(
            Robot(prim_path="/World/Fancy_Robot", name="fancy_robot")
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        # Get the articulation controller (only callable after the first reset)
        # Used for setting PD gains and applying actions
        self._jetbot_articulation_controller = self._jetbot.get_articulation_controller()
        # Add a physics callback to apply actions at every physics step
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        return

    # Physics callback: called at each step to send actions to the robot
    def send_robot_actions(self, step_size):
        # apply_action takes an ArticulationAction and sends commands to each joint
        # Accepts joint_positions, joint_efforts, and joint_velocities
        # None means no command is sent to that degree of freedom in this step
        # The same operation can also be called via self._jetbot.apply_action(...)
        self._jetbot_articulation_controller.apply_action(
            ArticulationAction(
                joint_positions=None,
                joint_efforts=None,
                joint_velocities=5 * np.random.rand(2,)  # Random velocity for left and right wheels
            )
        )
        return
```

!!! note "Choosing between the two `apply_action` methods"
    As noted in the code comments, the same operation can be performed via `self._jetbot.apply_action(...)`. Here is a comparison:

    | Method | Characteristics |
    |---|---|
    | `robot.get_articulation_controller().apply_action()` | Provides access to detailed ArticulationController settings such as PD gain tuning and control mode switching |
    | `robot.apply_action()` | More concise. Internally calls the ArticulationController, so behavior is identical |

    If you don't need to adjust PD gains, `robot.apply_action()` is sufficient. The following tutorials will use this more concise form.

Save the code and verify the simulation:

1. Press **Ctrl+S** to save the code and hot-reload Isaac Sim.
2. Click **File > New From Stage Template > Empty** to create a new world, then click **LOAD**.
3. Press the **PLAY** button and observe the Jetbot moving around randomly.

![Jetbot moving randomly](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_2_2.webp)

Since random velocities (in the range 0-5) are applied to the left and right wheels at every step, the Jetbot moves erratically.

## Extra Practice

Try the following exercises to deepen your understanding of robot control.

**Exercise 1: Move backwards** — Make the Jetbot move in reverse.

??? tip "Hint (click to expand)"
    Set the wheel velocities to negative values.

**Exercise 2: Turn right** — Make the Jetbot turn to the right.

??? tip "Hint (click to expand)"
    Set different velocities for the left and right wheels (faster on the left, slower on the right).

**Exercise 3: Stop after 5 seconds** — Make the Jetbot stop 5 seconds after the simulation starts.

??? tip "Hint (click to expand)"
    Accumulate `step_size` each step to calculate elapsed time, and use a conditional to stop the robot.

## Using the WheeledRobot Class

So far, we have used the generic `Robot` class. Isaac Sim also provides specialized classes for specific robot types. For wheeled robots, the `WheeledRobot` class allows more concise code.

Let's compare the `Robot` class and `WheeledRobot` class:

| Feature | `Robot` Class | `WheeledRobot` Class |
|---|---|---|
| Asset loading | Two steps: `add_reference_to_stage` + `Robot()` | Single step with `WheeledRobot()` (`create_robot=True`) |
| Wheel joints | Specified by index | Can be specified by joint name |
| Action application | `get_articulation_controller().apply_action()` | Direct via `apply_wheel_actions()` |

```python linenums="1" hl_lines="3 15-23 30-31"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.robots import WheeledRobot  # Specialized class for wheeled robots
from isaacsim.core.utils.types import ArticulationAction
import numpy as np


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        # WheeledRobot handles both asset loading and Robot wrapper creation at once
        self._jetbot = world.scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Robot",
                name="fancy_robot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],  # Wheel joint names
                create_robot=True,       # Also load the USD asset
                usd_path=jetbot_asset_path,
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        return

    def send_robot_actions(self, step_size):
        # apply_wheel_actions applies actions directly to the wheels
        self._jetbot.apply_wheel_actions(
            ArticulationAction(
                joint_positions=None,
                joint_efforts=None,
                joint_velocities=5 * np.random.rand(2,)  # Random velocity for left and right wheels
            )
        )
        return
```

Key advantages of using `WheeledRobot`:

- No need to call `add_reference_to_stage` separately (`create_robot=True` handles asset loading)
- Wheel joint names can be explicitly specified via `wheel_dof_names`
- `apply_wheel_actions()` provides wheel-specific action application

## Summary

This tutorial covered the following topics:

1. Loading robot assets from the **Nucleus server** and adding them to the scene
2. Wrapping robot prims with the **Robot class** for high-level API access
3. Joint control using **ArticulationController** and **ArticulationAction**
4. Continuously applying actions during simulation using **physics callbacks**
5. Simplified wheeled robot control using the **WheeledRobot class**

## Next Steps

Proceed to the next tutorial, "[Adding a Controller](03_adding_a_controller.md)," to learn how to add controllers to your robot for more advanced motion.

!!! note "Note"
    The following tutorials continue to use the Extension Workflow for development. Converting to the Standalone Workflow follows the same approach as learned in [Hello World](01_hello_world.md#converting-to-a-standalone-application).
