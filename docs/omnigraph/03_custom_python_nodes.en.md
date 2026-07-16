---
title: Custom Python Nodes
---

# Custom Python Nodes

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

A custom OmniGraph node is defined by two files: a `.ogn` JSON file (structure — inputs, outputs, parameters) and a function file (Python or C++). Node files are prefixed with `Ogn`.

## What you will learn

- **`.ogn` definition**: JSON with `version`, `categories`, `language: "python"`, `metadata.uiName`, `inputs`, `outputs`. The special `execIn` (type `execution`) input triggers the node in an **Action Graph**; in a **Push Graph** nodes run every frame and `execIn` is unnecessary.
- **Function**: a class matching the node/file name with a static `compute(db)` that reads `db.inputs.*`, writes `db.outputs.*`, and returns `True`/`False`. Use "internal state" to persist data between ticks.
- **Using it**: drop the `.py`/`.ogn` into an existing extension's node directory, or create your own extension.
- **Examples**: hover a node in the editor to see its extension name, then browse `exts/isaacsim.<ext_name>/isaacsim/<ext_name>/ogn/python/nodes/` (note: `Ogn<node>Database.py` files are generated, not the source).
