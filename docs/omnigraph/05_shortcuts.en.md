---
title: Commonly Used OmniGraph Shortcuts
---

# Commonly Used OmniGraph Shortcuts

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim provides shortcuts under **Tools > Robotics > Omnigraph Controllers** that populate common controller graphs from a minimal set of parameters: **Joint Position Controller**, **Joint Velocity Controller**, **Differential Controller**, and **Open Loop Gripper Controller**. No duplicate-graph validation is done; graphs are freely editable after creation. Click the icon next to **Python Script for Graph Generation** to view the generating script (creation happens in `make_graph()`).

## Controller graphs

- **Articulation Controllers** (Position/Velocity): issue commands directly to each joint. Set Robot Prim and Graph Path (default `/Graph/{type}_controller`). Drive via the **JointCommandArray** node in the Property tab.
- **Differential Controller**: converts linear/angular velocities to wheel velocities. Set Wheel Radius, Distance between wheels, optional Right/Left Joint Names or Indices, and optional WASD keyboard control (tune the **ScaleLinear**/**ScaleAngular** nodes).
- **Gripper Controller**: for end-effectors with one DOF per finger. Set Parent Robot, Gripper Root, Gripper Speed, comma-separated Gripper Joint Names, optional Open/Close Position Limits, and optional O/C/N keyboard control. Assumes open-limit > close-limit (auto-corrects if flipped); only uniform speed/limits via the shortcut.
