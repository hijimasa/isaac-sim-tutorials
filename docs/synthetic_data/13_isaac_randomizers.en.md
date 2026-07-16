---
title: Randomization Snippets
---

# Randomization Snippets

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough; full code is on the official page.

USD / Isaac Sim API randomization snippets for cases the built-in Replicator randomizers don't cover (all support `write_data=True`):

- **Randomizing Light Sources** — spawn N lights and randomize selected attributes over frames.
- **Randomizing Textures** — randomize textures then restore the original materials; includes creating and binding a new material.
- **Sequential Randomizations** — chained randomizations where each step depends on the previous (dome texture cycle → pallet moved → bin placed fully on the pallet → camera stepped over near-equidistant sphere points looking at the bin).
- **Physics-based Randomized Volume Filling** — spawn pallets, drop physics boxes inside temporary collision walls, nudge and pull boxes toward the pallet center with temporarily reduced friction, then remove the walls.
- **SimReady Assets SDG Example** — search and spawn [SimReady Assets](https://developer.nvidia.com/omniverse/simready-assets); async-only and requires the SimReady Explorer window:

    ```bash
    ./python.sh standalone_examples/api/isaacsim.replicator.examples/simready_assets_sdg.py
    ```

## Next Steps

- [Tutorial 14: Useful Snippets](14_isaac_snippets.md)
