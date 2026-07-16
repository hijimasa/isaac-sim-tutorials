---
title: Isaac Lab Tutorials
---

# Isaac Lab Tutorials

<span class="badge badge-intermediate">Intermediate</span>

Tutorials on deploying Isaac Lab trained policies in Isaac Sim and building RL-scale scenes (environment cloning and memory optimization).

## Overview

**Isaac Lab** is the official robot learning framework for Isaac Sim, providing APIs and examples for reinforcement learning, imitation learning, and more. Its core features include a modular configuration-driven system, flexible workflows, a suite of robot learning environments, support for multiple RL/IL libraries, peripheral device support for demonstrations, and custom actuator models for sim-to-real transfer.

!!! note "Scope of this section"
    Training itself is covered by the [Isaac Lab documentation](https://isaac-sim.github.io/IsaacLab). This section covers the Isaac Sim side: deploying trained policies and efficiently building large RL scenes.

## Tutorials

!!! example "[Isaac Lab Setup (Linux / Windows)](00_setup.md)"
    Pip-based installation of Isaac Lab for both platforms. Only needed when you train policies yourself — the demos run with Isaac Sim alone.

!!! example "[Tutorial 1: Policy Deployment](01_policy_deployment.md)"
    Deploy a policy trained in Isaac Lab: H1/Spot demos, reading env.yaml, the Policy Controller class, and debugging tips.

!!! example "[Tutorial 2: Getting Started with Cloner](02_cloner.md)"
    Clone environments with Cloner/GridCloner, access clones with vectorized APIs, and speed up parsing with physics replication.

!!! example "[Tutorial 3: Instanceable Assets](03_instanceable_assets.md)"
    Reduce memory usage of massively cloned scenes with instanceable assets, via importer options or conversion utilities.

## Suggested Related Tutorials

- Robot preparation: [Import URDF](../importer_exporter/01_import_urdf.md), [Import MJCF](../importer_exporter/03_import_mjcf.md)
- Rigging for policy inference: [Rig a Legged Robot](../robot_setup/13_rig_legged_robot.md)
- Python scripting: [Core API Tutorials](../core_api/index.md)

## Isaac Lab Resources

- [Isaac Lab Repository](https://github.com/isaac-sim/IsaacLab)
- [Isaac Lab Documentation](https://isaac-sim.github.io/IsaacLab)

## Deprecated Frameworks

Isaac Lab replaces the previously released frameworks [IsaacGymEnvs](https://github.com/isaac-sim/IsaacGymEnvs), [OmniIsaacGymEnvs](https://github.com/isaac-sim/OmniIsaacGymEnvs), and [Orbit](https://isaac-orbit.github.io). Migration guides: [from IsaacGymEnvs](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_from_isaacgymenvs.html), [from OmniIsaacGymEnvs](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_from_omniisaacgymenvs.html), [from Orbit](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_from_orbit.html).
