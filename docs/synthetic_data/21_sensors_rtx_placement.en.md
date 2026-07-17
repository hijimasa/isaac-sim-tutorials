---
title: RTX Sensors Placement and Calibration (ISP)
---

# RTX Sensors Placement and Calibration (ISP)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

Isaac Sim provides two separate extensions: **Camera Placement** (`isaacsim.sensors.rtx.placement`) optimizes camera placement in a stage based on coverage requirements and scene layout; **Camera Calibration** (`isaacsim.sensors.rtx.calibration`, split out of the placement extension in 6.0) extracts calibration data (direction, location, FOV polygon) saved to JSON. Requires meters as stage unit, Z-up, and a baked NavMesh.

## Camera Placement (`Tools > Sensors > Camera Placement`)

Set **Output Path**, **Total Camera Number** (`-1` = auto), camera range (height, distance, look-down angle), stage processing (patch size, ground height), and tuning params (**Coverage Density**, **Target Coverage Ratio**, border checking, on-navmesh, **Random Seed** for deterministic placement, **Stage Scope** X/Y bounds for edge cases without a valid NavMesh, etc.). Click **Place Cameras** to auto-place, then **Show all Camera Coverage** (or **Show Selected Camera Coverage**) to visualize coverage (N colors for N density; outputs `camera_info_payload.json`).

## Camera Calibration (`Tools > Sensors > Camera Calibration`)

Set **Place Info** (`city=.../building=.../room=...`), **Scene Root Prim Path**, floor/ceiling height, then **Create** a top-view camera (orthographic, rotation [0,0,0], vertical). Set **Raycast Density**, output path, then **Create Dot Prims** (6 dots per camera under `/World/Cameras`), **Generate Calibration File** (`calibration.json`), and **Generate Top View Image** (with FOV polygons under `Debug/fieldOfViewPolygon`).
