---
title: Policy Deployment
---

# Deploying Policies in Isaac Sim

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

- Run the H1 (humanoid) and Spot (quadruped) flat terrain policy demos
- Train and export policies in Isaac Lab
- Read the environment parameter files (`env.yaml` / `agent.yaml`)
- Understand the Policy Controller class structure
- Convert position outputs to torque controls (actuator network)
- Debug common deployment failures
- Get started with Sim-to-Real deployment

## Demos

Activate **Window > Examples > Robotics Examples**, then:

- **Unitree H1**: Robotics Examples > POLICY > Humanoid, press LOAD. Drive with arrow keys (forward / turn left / turn right).
- **Boston Dynamics Spot**: Robotics Examples > POLICY > Quadruped, press LOAD. Drive with arrow keys plus N / M for turning.

![H1 walk demo](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_lab_h1_walk_demo.gif)

## Training and Exporting Policies in Isaac Lab

Train with (Isaac Lab 2.0, RSL-RL):

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

Export with:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Velocity-Flat-H1-v0 --num_envs 32
```

The exported files are generated in the `exported` folder.

## Understanding the Environment Parameter File

`agent.yaml` (network parameters) and `env.yaml` (environment/robot configuration) are generated under `logs/rsl_rl/<task_name>/<time>/params/`. The `env.yaml` sections to match on the Isaac Sim side:

- **sim** — physics dt (e.g. 0.005 s = 200 Hz) and gravity
- **scene: robot: init_state** — initial pose and default joint positions/velocities (joint names are regex patterns)
- **actuators** — effort/velocity limits, stiffness, damping per joint group
- **observations / actions** — tensor structure and scale factors (e.g. action scale 0.5)
- **commands** — command type and valid ranges

## Policy Controller Class

The robot definition class spawns the robot USD, loads the policy and `env.yaml`, matches robot configuration to the policy in `initialize()`, builds the observation tensor in `_compute_observation()` (override required), and applies actions in `forward()` (override required), respecting the `decimation` parameter and action scale.

!!! warning
    For position-based controls, do not use `set_joint_position()` — it teleports joints. Use `apply_action()`.

## Position to Torque Controls

If the robot requires torque input, convert the policy's position output using an actuator network (see `LstmSeaNetwork` in `isaacsim.robot.policy.examples`), then apply torques with `set_joint_efforts()`.

## Debugging Tips

Check in this order:

1. **Verify the policy** by playing it in Isaac Lab.
2. **Joint order** — compare `prim.dof_names` between the Isaac Sim asset and the training asset; they must match exactly.
3. **Default joint positions** — wrong values cause distorted gaits (e.g. the H1 "moonwalk").
4. **Joint properties** — compare `prim.dof_properties` with the actuators section of `env.yaml`.
5. **Physics scene** — Time Steps Per Second must equal 1/dt from `env.yaml`; match the physx section as well.
6. **Observation/action tensors** — structure, data, scales, and ordering.

## Sim To Real Deployment

See the NVIDIA blog article [Closing the Sim-to-Real Gap: Training Spot Quadruped Locomotion with NVIDIA Isaac Lab](https://developer.nvidia.com/blog/closing-the-sim-to-real-gap-training-spot-quadruped-locomotion-with-nvidia-isaac-lab/).

## Next Steps

- [Tutorial 2: Getting Started with Cloner](02_cloner.md)
