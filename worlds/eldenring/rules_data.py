"""Elden Ring — declarative region access rules (rule_builder migration).

Geographic ``"Go To {region}"`` entrance rules, migrated out of the imperative
``EldenRingRules.set_rules`` into a declarative table consumed via ``self.set_rule``.
See ``SPEC-region-rules-rulebuilder.md``.

Scope of the table (Phase 1): **only** regions gated by a single static clause that are
NOT co-gated by ``_region_lock`` / ``_key_rules`` and do NOT use option-valued counts.
Multi-clause, dynamic-count, and region-locked entrances stay on the imperative
``_add_entrance_rule`` path until their dedicated phases (they need per-region aggregation).

The **grace-warp** environment (``"Warp To {region}"``) is deliberately NOT here — it lives in
its own builder (SPEC §4h). The one seam between the two environments is ``can_go_to`` below.
"""
from __future__ import annotations

from rule_builder.rules import Rule, Has

from .rules_predicates import can_go_to  # single source of the geographic/warp bridge


# region name -> access Rule for the entrance "Go To {region}". Geographic graph only.
region_rules_table: dict[str, Rule] = {
    # --- pure item gates ---
    "Carian Study Hall (Inverted)": Has("Carian Inverted Statue"),
    "Hinterland":                   Has("O Mother"),
    "Lamenter's Gaol (Upper)":      Has("Gaol Upper Level Key"),
    "Lamenter's Gaol (Lower)":      Has("Gaol Lower Level Key"),
    # --- item / geographic-reach (can_go_to bridge) ---
    "Deeproot Depths Upper":        can_go_to("Frenzied Flame Proscription"),
    "Wailing Dunes":                can_go_to("Altus Plateau"),
    "Volcano Manor":                Has("Drawing-Room Key") | can_go_to("Volcano Manor Dungeon"),
    "Belurat Swamp":                Has("Well Depths Key") | can_go_to("Enir Ilim"),
    "Cathedral of Manus Metyr": (
        Has("Hole-Laden Necklace")
        & can_go_to("Finger Ruins of Rhia")
        & can_go_to("Finger Ruins of Dheo")
    ),
}
