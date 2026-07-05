# Provenance & Attribution

This Elden Ring Archipelago world is **derived from the Elden Ring apworld
originally created by lBedrockl (GitHub: [fswap](https://github.com/fswap))**,
distributed under the MIT License as part of the Archipelago project.

A substantial portion of the foundational code — item and location definitions,
the base world scaffolding, and much of the region data — originates from that
work and is used here under the terms of the MIT License. See the accompanying
[`LICENSE`](./LICENSE) file, which retains the original copyright notice.

## What is original to this fork

Layered on top of the original apworld, the following systems were authored for
this project:

- **`num_regions`** — the rolled variable-region "archipelago-ification" mode
  (the marquee feature; not present in the upstream apworld).
- The **region-lock spine** and first-class region locks.
- **Boss locks** (generator-placed boss-drop keys).
- The **`slot_data` client contract** (`apIdsToItemIds`, `locationFlags`, and the
  region-lock / scaling tables) that couples this world to its runtime client.

## Assets

This distribution contains **only Python source**. It includes no FromSoftware
game assets. Elden Ring and its assets are the property of FromSoftware /
Bandai Namco.

## Thanks

With thanks to lBedrockl / fswap for the original Elden Ring apworld that this
work builds on.
