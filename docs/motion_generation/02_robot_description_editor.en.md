---
title: Lula Robot Description and XRDF Editor
---

# Lula Robot Description and XRDF Editor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

!!! warning "Deprecated in Isaac Sim 6.0"
    The official page is marked Deprecated in Isaac Sim 6.0; the Robot Motion (Experimental) API is the recommended successor. The editor and Lula still work in 6.0.

## Overview

The **Robot Description Editor** (`Tools > Robotics > Lula Robot Description Editor`) generates config files supplementing a robot's URDF, used by **Lula** (`robot_description.yaml`) and **cuMotion** (`.xrdf`).

## Key concepts

- **C-space (active/fixed joints)**: Active joints are directly controlled by Lula; fixed joints are treated as fixed at their "default configuration". Lula moves toward the default when untargeted and biases null-space resolution toward it. Choose sensible fixed positions (e.g. gripper open). At least one joint must be active.
- **Collision spheres**: roughly cover the robot surface; Lula prevents them from intersecting obstacles. Only needed for collision-avoiding algorithms (not the Kinematics Solver; RMPflow works without them but can't avoid obstacles).
- **XRDF vs Robot Description**: XRDF (cuMotion) is a superset of the Lula robot description file.

## Workflow

Play the stage, select the Articulation and links, **Set Joint Properties** (position + active/fixed status), then add collision spheres per link (**Add Sphere**, **Connect Spheres**, **Generate Spheres** from a water-tight mesh). Export via **Export To File** (`.yaml` for Lula, `.yaml`/`.xrdf` for cuMotion — a dropdown selects XRDF version 1.0 (`collision`) or 2.0 (`world_collision`) — with optional **Merge With Existing XRDF**); import via **Import From File** (overwrites editor state; XRDF import supports both 1.0 and 2.0). Not compatible with Instanceable Assets (though generated files still work on them) — uncheck the **Instanceable** checkbox on all geometry prims before use.
