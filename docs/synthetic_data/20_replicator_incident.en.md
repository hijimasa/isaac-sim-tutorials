---
title: Physical Space Event Generation (IRI)
---

# Physical Space Event Generation (IRI)

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

`Isaacsim.Replicator.Incident` (IRI) generates events in urban simulation scenes and integrates with [IRA](17_replicator_agent.md). Supported spontaneous events: **box toppling**, **fire and smoke**, and **liquid spills**.

## Workflow

1. **Tag** items with the **Event Scene Tagger** (`Tools > Action and Event Data Generation > Event Scene Tagger`) as loose / spillable / flammable items.
2. **Save** the scene (required for IRA use; sample at `.../Samples/Replicator/Incidents/full_warehouse_with_incident_tags.usd`).
3. **Configure events** via the **Event Config File** window (standalone) or the **Actor SDG** Events panel (IRA integration).
4. **Run** with Play, **Record Events** (standalone), or **Start Data Generation** (IRA).

## Details

- **Loose items** topple with a force direction: **random**, **navmesh** (toward the nearest walkable edge), or **closest waypoint** (add waypoints via **Add Waypoint Prim**).
- **Flammable items** need a visible mesh as fuel; **spillable items** spawn liquid on prims tagged **Spillable Area Floor** beneath them.
- **Event config (YAML)**: `ToppleEvent` (`topple_item`, `topple_nearby_radius`), `FireEvent` (`flammable_item`), `SpillEvent` (`leakable_item`, `target_size`, `leak_duration`), each with a `trigger` (e.g. `type: time`). Items receive semantic labels `incident_toppled_item` / `incident_flaming_item` / `incident_leaking_item` / `incident_liquid_spill`.
- **Agent responses** (IRA `response` section): `CommandResponse` with `pick_agent`, `commands` (e.g. `GoToResponse`, `LookAround`), and a `trigger` of `type: physical_event` referencing `event_name`.
