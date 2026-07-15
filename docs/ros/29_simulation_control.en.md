---
title: ROS2 Simulation Control
---

# ROS2 Simulation Control

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough and all command examples.

## Learning Objectives

Control Isaac Sim itself over ROS 2 using the standard [simulation_interfaces](https://github.com/ros-simulation/simulation_interfaces) package (`sudo apt install ros-<distro>-simulation-interfaces`) — enabling simulator-agnostic automated-testing workflows.

Enable the extension with `./isaac-sim.sh --/isaac/startup/ros_sim_control_extension=True` or via the Extension Manager (`isaacsim.ros2.sim_control`).

## Capabilities

- **Simulation state** — `/set_simulation_state` (0 stopped / 1 playing / 2 paused / 3 quitting), `/get_simulation_state`, `/step_simulation` (must be paused; blocks until done), and the `/simulate_steps` action (per-step feedback, cancelable).
- **Entities** — `/get_entities` (POSIX-regex filter over prim paths), `/get_entity_info`, `/get_entity_state` / `/get_entities_states` (pose always; velocities only with RigidBodyAPI; acceleration always zero), `/spawn_entity` (URI → USD reference, empty URI → Xform; spawned prims get a `simulationInterfacesSpawned` attribute), `/delete_entity`, `/set_entity_state` (world frame only), `/reset_simulation` (removes all spawned prims and restarts the timeline).
- **Worlds** — `/load_world` (USD formats only; not while playing), `/unload_world`, `/get_current_world`, `/get_available_worlds` (searches /Isaac/Environments and /Isaac/Samples/ROS2/Scenario; supports TagsFilter, additional_sources, offline_only).

Example:

```bash
ros2 service call /set_simulation_state simulation_interfaces/srv/SetSimulationState "{state: {state: 1}}"
ros2 service call /get_entities simulation_interfaces/srv/GetEntities "{filters: {filter: '^/World'}}"
ros2 action send_goal /simulate_steps simulation_interfaces/action/SimulateSteps "{steps: 20}" --feedback
```

Implementation: a singleton ROS2ServiceManager (single node, thread-safe spinning independent of Action Graph) and a SimulationControl class over `omni.timeline`; extend both to add services.

This completes the ROS 2 tutorial series.
