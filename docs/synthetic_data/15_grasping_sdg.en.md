---
title: Grasping Synthetic Data Generation
---

# Grasping Synthetic Data Generation

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

The `isaacsim.replicator.grasping` extension (+ UI, **Tools > Replicator > Grasping**) automates finding and evaluating grasp poses for a gripper–object pair: configuration → grasp pose sampling (antipodal sampler) → multi-step grasp phases (e.g. open, close, lift) → physics-based evaluation → YAML logging. Orchestrated by the **GraspingManager** API. Sample stage: **Samples > Replicator > Stage > sdg_grasping_xarm.usd**. Requires `libspatialindex` (`sudo apt-get install libspatialindex-dev`).

## UI Sections

- **Gripper** — root path, controlled (drive) joints with pre-grasp positions, and ordered Grasp Phases (target joint positions, dt, step count; individually simulatable).
- **Object** — target path; antipodal sampler parameters (orientations per grasp axis, standoff distance, max aperture, alignment axes, approach direction, lateral perturbation sigma, seed); pose generation/visualization; trimesh debug.
- **Workflow** — number of samples (-1 = all), output path (YAML results), overwrite flag, Start.
- **Simulation** — render each step (disable for speed), timeline vs direct physics stepping, optional isolated physics scene.
- **Config** — save/load the setup as YAML with selectable includes (gripper path, pre-grasp states, phases, object path, sampler params, poses).

## Code Example

```bash
./python.sh standalone_examples/api/isaacsim.replicator.grasping/grasping_workflow_sdg.py
```

## Next Steps

- [Tutorial 16: Data Generation with MobilityGen](16_mobility_gen.md)
