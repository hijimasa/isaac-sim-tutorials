---
title: Adding a Controller
---

# Adding a Controller

## Learning Objectives

After completing this tutorial, you will have learned:

- How to create a custom controller by inheriting from `BaseController`
- The basics of robot control using a unicycle model (differential drive kinematics)
- How to use the built-in controllers available in Isaac Sim

## Getting Started

### Prerequisites

- Complete [Tutorial 2: Hello Robot](02_hello_robot.md) before starting this tutorial.

### Estimated Time

Approximately 10 minutes.

### Preparing the Source Code

This tutorial continues editing the `hello_world.py` file from the Hello World sample. If you are continuing from the previous tutorial, you can proceed as-is. If you are resuming on a different day, follow these steps to open the source code:

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > General > Hello World**.
3. Click the **Open Source Code** button to open `hello_world.py` in Visual Studio Code.

For detailed instructions, refer to the ["Opening the Hello World Sample" section](01_hello_world.md#opening-the-hello-world-sample) in Hello World.

## Creating a Custom Controller

In the previous tutorial, we moved the robot by directly specifying velocities for each wheel. In practice, however, you usually want to control the robot with high-level commands such as "forward velocity" and "angular velocity."

A **controller** performs this conversion. Controllers in Isaac Sim inherit from `BaseController`. The only method you need to implement is `forward`, which must return an `ArticulationAction`.

### The Unicycle Model

For differential drive robots (two-wheeled robots like the Jetbot), the **unicycle model** is commonly used to calculate each wheel's velocity from a forward velocity $v$ and angular velocity $\omega$.

The formulas are as follows:

| Variable | Description |
|---|---|
| $v$ | Forward velocity (`command[0]`) |
| $\omega$ | Angular velocity (`command[1]`) |
| $r$ | Wheel radius (`wheel_radius`) |
| $L$ | Distance between left and right wheels = tread (`wheel_base`)[^1] |

[^1]: Strictly speaking, the distance between the left and right wheels is called the "tread" (or "track width"), but the Isaac Sim API uses the parameter name `wheel_base`.

$$
v_{\text{left}} = \frac{2v - \omega L}{2r}, \quad v_{\text{right}} = \frac{2v + \omega L}{2r}
$$

### Full Code

The following code implements the unicycle model in a `CoolController` class, specifying a forward velocity of 0.20 m/s and an angular velocity of π/4 rad/s to make the Jetbot drive in an arc.

```python linenums="1" hl_lines="5 8-22 52-53 56-58"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.api.controllers import BaseController  # Base class for controllers
import numpy as np


class CoolController(BaseController):
    def __init__(self):
        super().__init__(name="my_cool_controller")
        # An open-loop controller based on the unicycle model
        self._wheel_radius = 0.03    # Wheel radius [m]
        self._wheel_base = 0.1125    # Distance between left and right wheels (tread) [m]
        return

    def forward(self, command):
        # command[0]: forward velocity, command[1]: angular velocity (yaw only)
        joint_velocities = [0.0, 0.0]
        joint_velocities[0] = ((2 * command[0]) - (command[1] * self._wheel_base)) / (2 * self._wheel_radius)
        joint_velocities[1] = ((2 * command[0]) + (command[1] * self._wheel_base)) / (2 * self._wheel_radius)
        # A controller must return an ArticulationAction
        return ArticulationAction(joint_velocities=joint_velocities)


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        world.scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Robot",
                name="fancy_robot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        # Initialize the controller after load and the first reset
        self._my_controller = CoolController()
        return

    def send_robot_actions(self, step_size):
        # Apply the actions calculated by the controller
        self._jetbot.apply_action(
            self._my_controller.forward(command=[0.20, np.pi / 4])
        )
        return
```

Save the code and verify the simulation:

1. Press **Ctrl+S** to save the code and hot-reload Isaac Sim.
2. Click **File > New From Stage Template > Empty** to create a new world, then click **LOAD**.
3. Press the **PLAY** button and observe the Jetbot driving in an arc.

![Arc driving with custom controller](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_3_1.webp)

!!! warning "Warning"
    Pressing **STOP** then **PLAY** may not properly reset the world. Use the **RESET** button to restart the simulation.

### Key Points for Custom Controllers

- Inherit from `BaseController` and implement the `forward` method
- The `forward` method must return an `ArticulationAction`
- Manage robot-specific parameters (wheel radius, wheel base, etc.) within the controller
- The controller's role is to convert high-level commands (forward velocity, angular velocity) into low-level joint commands

## Using the Built-in Controllers

Isaac Sim provides **built-in controllers** for commonly used robot control patterns. By leveraging these, you can avoid implementing kinematics calculations yourself.

Here we combine two controllers:

| Controller | Type | Description |
|---|---|---|
| `WheelBasePoseController` | Generic controller | Guides the robot toward a goal position. Works with multiple robot types |
| `DifferentialController` | Robot-specific controller | For differential drive robots. Converts forward/angular velocity to wheel velocities |

`WheelBasePoseController` uses `DifferentialController` internally to compute the path to the goal position. Unlike the custom controller in the previous section, you simply specify the **robot's current position and a goal position**, and the controller automatically guides the robot.

```python linenums="1" hl_lines="5-8 44-48 51-55"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
# Generic controller usable with multiple robot types
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
# Robot-specific controller for differential drive
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
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
        world.scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Robot",
                name="fancy_robot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        # Initialize WheelBasePoseController with DifferentialController
        self._my_controller = WheelBasePoseController(
            name="cool_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_control",
                wheel_radius=0.03,      # Wheel radius [m]
                wheel_base=0.1125       # Distance between left and right wheels (tread) [m]
            ),
            is_holonomic=False  # Jetbot is non-holonomic (cannot move sideways)
        )
        return

    def send_robot_actions(self, step_size):
        # Get the robot's current position and orientation
        position, orientation = self._jetbot.get_world_pose()
        # Simply pass the current pose and goal position; the controller computes the path
        self._jetbot.apply_action(
            self._my_controller.forward(
                start_position=position,
                start_orientation=orientation,
                goal_position=np.array([0.8, 0.8])  # Goal position [x, y]
            )
        )
        return
```

Save the code and verify the simulation:

1. Press **Ctrl+S** to save the code and hot-reload Isaac Sim.
2. Click **File > New From Stage Template > Empty** to create a new world, then click **LOAD**.
3. Press the **PLAY** button and observe the Jetbot autonomously moving toward the goal position (0.8, 0.8).

![Moving to goal position with built-in controllers](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_3_2.webp)

## Summary

This tutorial covered the following topics:

1. Creating a custom controller by inheriting from **BaseController**
2. Differential drive robot kinematics using the **unicycle model**
3. Autonomous navigation to a goal position using **WheelBasePoseController** and **DifferentialController**

## Next Steps

Proceed to the next tutorial, "[Adding a Manipulator Robot](04_adding_a_manipulator_robot.md)," to learn how to add a manipulator robot to the simulation.

!!! note "Note"
    The following tutorials continue to use the Extension Workflow for development. Converting to the Standalone Workflow follows the same approach as learned in [Hello World](01_hello_world.md#converting-to-a-standalone-application).
