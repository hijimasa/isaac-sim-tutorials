---
title: Running a Reinforcement Learning Policy through ROS 2
---

# Running a Reinforcement Learning Policy through ROS 2 and Isaac Sim

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Run the H1 flat terrain locomotion policy with inference in an external ROS 2 node: Isaac Sim publishes observations (IMU, joint states) and receives actions (joint commands). Requires PyTorch, the `h1_fullbody_controller` package from IsaacSim-ros_workspaces, and a robot rigged per [Rig a Legged Robot](../robot_setup/13_rig_legged_robot.md) (env file angles are radians; the GUI expects degrees) — or skip rigging with the preconfigured `Isaac Sim/Samples/Rigging/H1/h1_rigged.usd` asset. The policy walks forward and turns; it does not support backward or sideways motion.

## Setup

1. **IMU** — create an Imu Sensor under `/h1/pelvis` (data from other links must be transformed to the pelvis frame).
2. **On-demand graphs** — create ActionGraphs (ROS_Imu, ROS_Joint_States, ROS_Clock) under a `/h1/Graph` scope with `pipelineStage = pipelineStageOnDemand`, triggered by **On Physics Step** so they run at the physics rate:
    - ROS_Imu: Isaac Read IMU Node (imuPrim `/h1/pelvis/Imu_Sensor`, uncheck Read Gravity) → ROS2 Publish IMU (Frame ID `pelvis_imu`); Read Simulation Time with Reset on Stop checked.
    - ROS_Joint_States: Publish Joint State (target `/h1`, topic `/joint_states`), Subscribe Joint State (`/joint_command`) → Articulation Controller (target `/h1`).
    - ROS_Clock: Read Simulation Time → ROS2 Publish Clock.
3. **Scenario** — warehouse environment, robot at Z = 1.0, Root Layer **Time Codes Per Second 200**, Physics Scene with **Time Steps Per Second 200**; if using PhysX, GPU Dynamics off and Broadphase MBP (CPU physics for a single robot).

Preconfigured assets: `Isaac Sim/Samples/ROS2/Robots/h1_ROS.usd` and `Scenario/h1_ros_locomotion_policy_tutorial.usd`.

## Run

```bash
ros2 launch h1_fullbody_controller h1_fullbody_controller.launch.py   # start BEFORE pressing Play, or the robot falls
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keys: i forward, u/o forward+turn, j/l turn, k stand. Backward keys (m , .) make the robot fall; speeds above 0.75 exceed the policy limits; slow drift with no command is expected.

## Next Steps

- [Isaac Lab tutorials](../isaac_lab/index.md) and the native [Policy Deployment](../isaac_lab/01_policy_deployment.md) method.
