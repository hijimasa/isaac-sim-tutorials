---
title: Data Logging
---

# Data Logging

## Learning Objectives

After completing this tutorial, you will have learned:

- How to record simulation data using the `DataLogger` class
- How to save recorded data to a JSON file
- How to load and replay saved data (trajectory replay and scene replay)

## Getting Started

### Prerequisites

- Complete [Tutorial 4: Adding a Manipulator Robot](04_adding_a_manipulator_robot.md) before starting this tutorial.

### Estimated Time

Approximately 10-15 minutes.

### Overview

In robotics simulation, recording robot joint states, control inputs, and positions of objects in the environment is useful for debugging and analysis. Isaac Sim provides the **`DataLogger`** class to record simulation data at each physics step and save it as a JSON file.

In this tutorial, we use the Follow Target sample, where a Franka robot follows a target, to record and replay data.

## Recording Data

### Loading the Sample

1. Activate **Windows > Examples > Robotics Examples** to open the Robotics Examples tab.
2. Click **Robotics Examples > Manipulation > Follow Target Task**.
3. Press the **LOAD** button to load the world. A Franka robot and a target cube are placed in the scene.

### Performing the Recording

4. In the Follow Target menu's **Data Logging** section, specify the **Output Directory** for the JSON file.
5. Click the **Follow Target** button under **Task Controls** to start the task.
6. Click the **START LOGGING** button to begin recording.
7. Move the target cube in the viewport and observe the Franka following it.
8. After a few seconds, click the **SAVE DATA** button to save the data.
9. Create a new stage via **File > New From Stage Template > Empty**.

### Code Overview

Let's examine the Follow Target sample code to understand how to use the DataLogger.

!!! tip "Source Code Location"
    The Follow Target sample source code is located at:
    `<Isaac Sim Install Directory>/exts/isaacsim.examples.interactive/isaacsim/examples/interactive/follow_target/follow_target.py`

#### Registering the Logging Function

With `DataLogger`, you register a **logging function called at every physics step** to define the data to record.

```python linenums="1"
def _on_logging_event(self, val):
    world = self.get_world()
    data_logger = world.get_data_logger()
    if not world.get_data_logger().is_started():
        robot_name = self._task_params["robot_name"]["value"]
        target_name = self._task_params["target_name"]["value"]

        # Define the logging function called at every physics step
        def frame_logging_func(tasks, scene):
            return {
                "joint_positions": scene.get_object(robot_name)
                    .get_joint_positions().tolist(),
                "applied_joint_positions": scene.get_object(robot_name)
                    .get_applied_action().joint_positions.tolist(),
                "target_position": scene.get_object(target_name)
                    .get_world_pose()[0].tolist(),
            }

        data_logger.add_data_frame_logging_func(frame_logging_func)
    if val:
        data_logger.start()
    else:
        data_logger.pause()
    return
```

`frame_logging_func` takes `tasks` and `scene` as arguments and returns a dictionary. The dictionary keys are data item names, and the values are the data to record. This function is automatically called at every physics step while the DataLogger is started.

| Data Item | Description |
|---|---|
| `joint_positions` | Current joint positions of the robot |
| `applied_joint_positions` | Joint positions commanded by the controller |
| `target_position` | World coordinates of the target |

#### Saving Data

```python linenums="1"
def _on_save_data_event(self, log_path):
    world = self.get_world()
    data_logger = world.get_data_logger()
    data_logger.save(log_path=log_path)
    data_logger.reset()
    return
```

`save()` writes to a JSON file, and `reset()` clears the internal state.

### Data Format

The saved JSON file has the following structure:

```json
{
  "Isaac Sim Data": [
    {
      "current_time": 1.483,
      "current_time_step": 89,
      "data": {
        "joint_positions": [0.075, -1.231, 0.113, ...],
        "applied_joint_positions": [0.072, -1.220, 0.119, ...],
        "target_position": [0.0, 10.0, 70.0]
      }
    },
    ...
  ]
}
```

Metadata automatically added to each frame:

| Field | Description |
|---|---|
| `current_time` | Elapsed time since simulation start (seconds) |
| `current_time_step` | Frame index |
| `data` | Dictionary returned by `frame_logging_func` |

## Replaying Data

Use the recorded data to reproduce robot motion.

### Loading the Sample

1. Click **Robotics Examples > Manipulation > Replay Follow Target Task**.
2. Press the **LOAD** button to load the world.
3. In the **Data Replay** section, specify the path to the previously saved JSON file in the **Data File** field.

### Trajectory Replay

Trajectory replay applies recorded joint position commands to the robot to reproduce its motion. The target position is not updated.

4. Click the **Replay Trajectory** button.

!!! tip "Source Code Location"
    The Replay Follow Target sample source code is located at:
    `<Isaac Sim Install Directory>/exts/isaacsim.examples.interactive/isaacsim/examples/interactive/replay_follow_target/replay_follow_target.py`

#### Trajectory Replay Code

```python linenums="1"
async def _on_replay_trajectory_event_async(self, data_file):
    self._data_logger.load(log_path=data_file)
    world = self.get_world()
    await world.play_async()
    world.add_physics_callback("replay_trajectory", self._on_replay_trajectory_step)
    return

def _on_replay_trajectory_step(self, step_size):
    if self._world.current_time_step_index < self._data_logger.get_num_of_data_frames():
        data_frame = self._data_logger.get_data_frame(
            data_frame_index=self._world.current_time_step_index
        )
        self._articulation_controller.apply_action(
            ArticulationAction(
                joint_positions=data_frame.data["applied_joint_positions"]
            )
        )
    return
```

Replay workflow:

1. `load()` reads data from the JSON file
2. Register a physics callback
3. At each physics step, use `get_data_frame()` to retrieve the frame data corresponding to the current step
4. Apply the `applied_joint_positions` as an `ArticulationAction`

### Scene Replay

Scene replay updates the target position in addition to joint angles, fully reproducing the recorded scene.

5. After replay completes, press the **Reset** button.
6. Click the **Replay Scene** button.

#### Scene Replay Code

```python linenums="1"
def _on_replay_scene_step(self, step_size):
    if self._world.current_time_step_index < self._data_logger.get_num_of_data_frames():
        target_name = self._task_params["target_name"]["value"]
        data_frame = self._data_logger.get_data_frame(
            data_frame_index=self._world.current_time_step_index
        )
        self._articulation_controller.apply_action(
            ArticulationAction(
                joint_positions=data_frame.data["applied_joint_positions"]
            )
        )
        self._world.scene.get_object(target_name).set_world_pose(
            position=np.array(data_frame.data["target_position"])
        )
    return
```

The difference from trajectory replay is that `set_world_pose()` also restores the target's position. This enables complete replay including the environmental state at the time of recording.

7. Create a new stage via **File > New From Stage Template > Empty**.

## DataLogger API Reference

| Method | Description |
|---|---|
| `world.get_data_logger()` | Retrieve the DataLogger instance from World |
| `add_data_frame_logging_func(func)` | Register a logging function called at each physics step |
| `start()` | Start data recording |
| `pause()` | Pause data recording |
| `is_started()` | Return whether recording is in progress |
| `save(log_path=path)` | Save recorded data to a JSON file |
| `reset()` | Clear internal state |
| `load(log_path=path)` | Load data from a JSON file |
| `get_num_of_data_frames()` | Get the number of recorded frames |
| `get_data_frame(data_frame_index=i)` | Retrieve frame data at the specified index |

## Summary

This tutorial covered the following topics:

1. **Recording simulation data** with `DataLogger`
2. **Defining custom data items** using `frame_logging_func`
3. **Saving data in JSON format** and understanding the data structure
4. **Trajectory replay** (joint angles only) and **Scene replay** (complete replay including environment state)

!!! tip "Advanced Usage"
    `DataLogger` can also be used for recording reinforcement learning episode data or quantitative evaluation of simulation results. By recording custom data through `frame_logging_func`, you can support a wide variety of analyses.

!!! note "Note"
    The following tutorials continue to use the Extension Workflow for development. Converting to the Standalone Workflow follows the same approach as learned in [Hello World](01_hello_world.md).
