---
title: Isaac Sim OmniGraph Tutorial
---

# Isaac Sim OmniGraph Tutorial

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

OmniGraph is Omniverse's visual programming framework, and the main engine in Isaac Sim for Replicators, the ROS 2 bridge, sensor access, controllers, and UI. This tutorial builds an **action graph** to drive the JetBot.

## What you will learn

- **Set up the stage**: add a Ground Plane and `Isaac Sim/Robots/NVIDIA/Jetbot/jetbot.usd` at `/World/jetbot`.
- **Build the graph** (`Window > Graph Editors > Action Graph > New Action Graph`): add an **Articulation Controller** (set `robotPath` / `targetPrim` to the JetBot) and a **Differential Controller** (`wheelDistance` 0.1125, `wheelRadius` 0.03, `maxAngularSpeed` 0.2).
- **Joint names**: two **Constant Token** nodes (`left_wheel_joint`, `right_wheel_joint`) → **Make Array** (`token[]`, size 2) → Articulation Controller's Joint Names.
- **Event**: **On Playback Tick** → both controllers' Exec In; Differential Controller Velocity Command → Articulation Controller Velocity Command.
- **Shortcuts**: `Tools > Robotics > OmniGraph Controllers > Differential Controller` generates the graph in a few clicks; enable **Use Keyboard Control (WASD)** to drive with the keyboard.
