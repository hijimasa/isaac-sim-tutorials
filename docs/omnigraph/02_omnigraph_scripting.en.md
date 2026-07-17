---
title: OmniGraph via Python Scripting
---

# OmniGraph via Python Scripting

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

OmniGraph has Python scripting interfaces in addition to visual editing. This tutorial scripts an action graph purely with Python APIs.

## What you will learn

- **Create a graph** with `og.Controller.edit({...}, {keys.CREATE_NODES: [...], keys.SET_VALUES: [...], keys.CONNECT: [...]})` — e.g. an `OnTick` → `PrintText` "Hello World" graph (`logLevel` = Warning to see terminal output).
- **Edit a graph**: `og.Controller.attribute(path).get()/set()`, `og.Controller.create_node(...)`, `og.Controller.connect(...)`. Value changes take effect on the next tick.
- **Execution timing**: default is every frame; set `"pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND` (or `change_pipeline_stage(...)`) and trigger manually with `graph_handle.evaluate()`. See `standalone_examples/api/isaacsim.core.experimental.api/omnigraph_triggers.py` for physics/render callback examples.
