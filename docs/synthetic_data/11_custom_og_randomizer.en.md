---
title: Custom Replicator Randomization Nodes
---

# Custom Replicator Randomization Nodes

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Turn custom randomizations (random 3D points on / in / between spheres) into OmniGraph nodes integrated with Replicator's SDG pipeline, in three escalating stages:

1. **Plain Python functions** — spawn and randomize prims directly from the Script Editor.
2. **OmniGraph nodes** — `.ogn` definitions + Python implementations (`OgnSampleInSphere/OnSphere/BetweenSpheres`, shipped in the built-in `isaacsim.replicator.examples` extension; self-made nodes live in your extension, enable it under Third Party). Add nodes manually to the `/Replicator/SDGPipeline` graph and trigger via **Tools > Replicator > Preview / Step**.
3. **ReplicatorItems** — wrap the nodes with the `@ReplicatorWrapper` decorator so the Replicator API inserts them into the SDG graph automatically, usable like built-in randomizers. Replace the `create_node` path (`isaacsim.replicator.examples.OgnSampleInSphere`) if your nodes live in a different extension.

![Custom randomizer result](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_custom_og_randomizer_python.jpg)

## Next Steps

- [Tutorial 12: Modular Behavior Scripting](12_modular_scripting.md)
