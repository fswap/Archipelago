"""Progressive stone bell-bearing grant table (SPEC-progressive-stone-bells.md).

Single source of truth for the two progressive items. Each list is ORDERED: index K
(0-based) = the (K+1)th copy the player receives. Per copy:
  - "goods":  EquipParamGoods id of the real Miner's Bell Bearing tier to grant as a
              COSMETIC inventory record. The shop unlock does NOT depend on this.
  - "flags":  ShopLineupParam.eventFlag_forStock values to SET so the Twin Maidens stone
              rows for that rung appear (setting the flag IS the unlock, no hand-over).
              Extracted from vanilla_er/ShopLineupParam.csv (Twin Maiden shop IDs 1018xx).
              Each bell tier unlocks two stone tiers (except Somber [5] = Somber [9] only).

Stone goods ids: Smithing [1]-[8] = 10100-10107; Somber [1]-[8] = 10160-10167, [9] = 10200.

fill_slot_data emits this as "progressiveGrants" (keyed by item name); the client keeps a
per-item receipt counter and, on the Kth copy, grants goods[K] and sets flags[K]. Copies
beyond the tier count are silent no-ops client-side (the k < tiers.size() guard). The counter
advances across last_received_index on reconnect; idempotent flag-sets make that safe.
"""

PROGRESSIVE_SMITHING_BELL = "Progressive Smithing-Stone Miner's Bell Bearing"
PROGRESSIVE_SOMBER_BELL = "Progressive Somberstone Miner's Bell Bearing"

STONE_BELL_GRANTS = {
    PROGRESSIVE_SMITHING_BELL: [
        {"goods": 8951, "flags": [280080, 280090]},  # Smithing Stone [1],[2]
        {"goods": 8952, "flags": [280110, 280120]},  # Smithing Stone [3],[4]
        {"goods": 8953, "flags": [280140, 280150]},  # Smithing Stone [5],[6]
        {"goods": 8954, "flags": [280160, 280170]},  # Smithing Stone [7],[8]
    ],
    PROGRESSIVE_SOMBER_BELL: [
        {"goods": 8955, "flags": [280180, 280190]},  # Somber [1],[2]
        {"goods": 8956, "flags": [280200, 280210]},  # Somber [3],[4]
        {"goods": 8957, "flags": [280230, 280240]},  # Somber [5],[6]
        {"goods": 8958, "flags": [280250, 280260]},  # Somber [7],[8]
        {"goods": 8959, "flags": [280280]},          # Somber [9]
    ],
}

# Grant-tier counts (= len of each list above): copies that actually DO something. Membership only.
PROGRESSIVE_BELL_COUNTS = {k: len(v) for k, v in STONE_BELL_GRANTS.items()}

# How many copies of each progressive bell to put in the POOL, decoupled from the grant tiers.
# Copies beyond the tier count are SILENT no-ops client-side (the receive handler's
# `k < tiers.size()` guard grants nothing) -- they spread the ladder across more checks so the
# upgrade ramp comes online earlier. Keep modest: in dlc_only these inject as mandatory
# progression and eat into the tight injection budget. Tune here.
PROGRESSIVE_BELL_POOL_COUNT = {
    PROGRESSIVE_SMITHING_BELL: 15,
    PROGRESSIVE_SOMBER_BELL: 15,
}

# Copies of each progressive bell to FORCE into sphere-1 (no-item-reachable) locations in
# dlc_only via early_items, so the upgrade ladder opens near the start. Keep SMALL: dlc_only
# sphere 1 = Gravesite Plain only, already carrying scadu_frontload -- forcing all copies early
# would overcommit it. Because the item is progressive, 1-2 early copies guarantees an early
# first rung; the rest distribute normally. 0 to disable.
PROGRESSIVE_BELL_EARLY_COUNT = {
    PROGRESSIVE_SMITHING_BELL: 4,
    PROGRESSIVE_SOMBER_BELL: 4,
}
