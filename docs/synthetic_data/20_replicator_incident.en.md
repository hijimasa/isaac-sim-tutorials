---
title: Physical Space Event Generation (IRI)
---

# Physical Space Event Generation (IRI)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

`Isaacsim.Replicator.Incident` (IRI) generates events in urban simulation scenes. Supported spontaneous events: **box toppling**, **fire and smoke**, and **liquid spills**. In Isaac Sim 6.0 the Event Scene Tagger window and the IRA response integration were removed; tagging moved to the property **+ Add > Incident Tagging** menu, and event details are written as a standardized **incident report JSON**.

## Workflow

1. **Tag** items via right-click (or the Property tab) **+ Add > Incident Tagging** as loose / spillable / flammable items (visualize with the viewport eye icon → Show By Type > Incident Scene Tags; untag by removing `isaacsim_replicator_incident_attr:` Raw USD properties).
2. **Save** the scene to USD to persist tags (sample at `.../Samples/Replicator/Incidents/full_warehouse_with_incident_tags.usd`).
3. **Configure events** via the **Event Config File** window (the YAML config is saved/loaded separately from the USD scene) and press **Set Up Events**.
4. **Run** with Play or **Record Events**; an incident report is written as JSON (default `incidents_report.json`).

## Details

- **Loose items** topple with a force direction: **random**, **navmesh** (toward the nearest walkable edge), or **closest waypoint** (create waypoints via **Create > Incident/Topple > Topple Destination**).
- **Flammable items** need a visible mesh as fuel; **spillable items** spawn liquid on prims tagged as **spillable area** beneath them. If fire effects render incorrectly, launch with `--/rtx/hydra/supportMultiTickRate=false`.
- **Event config (YAML)**: `ToppleEvent` (`topple_item`, `topple_nearby_radius`), `FireEvent` (`flammable_item`), `SpillEvent` (`leakable_item`, `target_size`, `leak_duration`), each with a `trigger`: `time` (seconds), `carb_event` (`event_name`, the main way to integrate with other extensions), or `physical_event` (`incident_name` of another IRI event). Items receive semantic labels `incident_toppled_item` / `incident_flaming_item` / `incident_leaking_item` / `incident_liquid_spill`.
- **Incident report JSON** (`IncidentReport.start_recording` in `isaacsim.replicator.incident.core`): top-level keys are event names; entries may contain `event_data`, `trigger_data` (trigger `type`/`priority`/`time` in seconds), and `simulation_data` in **frame indices** (topple/spill: `start_time`+`end_time`; fire: `start_time`+`fire_prim` only).
- **Python API**: enable `isaacsim.replicator.incident.core`; use `get_instance().get_incident_manager()`, `TriggersManager` (`omni.metropolis.pipeline.triggers`), tag commands (`ApplyLooseItemTagCommand`, ...), and `create_topple/pyro/spill_event_manager()`.
