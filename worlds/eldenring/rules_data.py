"""Elden Ring — declarative region access rules (rule_builder migration).

Geographic ``"Go To {region}"`` entrance rules migrated out of the imperative
``EldenRingRules.set_rules``. See ``SPEC-region-rules-rulebuilder.md``.

* ``region_rules_table`` — static single-clause gates (Phase 1): regions gated by one option-free
  clause, not co-gated by ``_region_lock`` / ``_key_rules``.
* ``build_region_rules(world)`` — the FULL geographic rule set (Phase 5): seeds from the static
  table, then applies every option-guarded gate, AND-combining per region exactly as the legacy
  ``_add_entrance_rule`` (add_rule) stacking did. Reads ``world.options`` for guards + dynamic counts.

The **grace-warp** environment (``"Warp To {region}"``) is deliberately NOT here — it lives in
``warp_rules.py`` (SPEC §4h). The one seam between the two environments is ``can_go_to``.
"""
from __future__ import annotations

from rule_builder.rules import Rule, Has, HasAll

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


def build_region_rules(world) -> dict[str, Rule]:
    """Full geographic ``"Go To {region}"`` access rules — faithful transcription of the imperative
    entrance-rule logic in ``EldenRingRules.set_rules`` (rules_mixin.py).

    Seeds from ``region_rules_table`` above, then applies each option-guarded gate, AND-combining
    per region exactly as the legacy ``_add_entrance_rule`` / ``add_rule`` stacking did. Reads
    ``world.options`` for the guards and for dynamic counts (great runes, messmer kindling).

    Option branches are NOT flattened. E.g. the Four Belfries imbued gate is ``imbued >= 4`` under
    ``enable_dlc`` and ``imbued >= 3`` otherwise: these are logically nested (>=4 implies >=3), but
    they live in the mutually-exclusive ``enable_dlc`` if/else, so each is added only in its own
    branch — never AND-ed together (which would wrongly force >=4 on a no-DLC seed).

    The rejoin consumes this via ``add_rule`` so region-lock / warp clauses still stack independently.
    """
    from .rules_predicates import (
        can_get, has_enough_great_runes, has_enough_imbued, bell_bearings_required,
    )
    o = world.options
    rules: dict[str, Rule] = dict(region_rules_table)

    def add(region: str, clause: Rule) -> None:
        rules[region] = clause if region not in rules else (rules[region] & clause)

    # --- world_logic < 3 (set_rules L62-90) ---
    if o.world_logic < 3:
        if o.soft_logic:
            add("Caelid", can_go_to("Altus Plateau"))
            add("Mohgwyn Palace", Has("Liurnia Lock"))
        add("Altus Plateau", HasAll("Dectus Medallion (Left)", "Dectus Medallion (Right)"))

    # --- unconditional geographic gates (L162-198) ---
    add("Raya Lucaria Academy", Has("Academy Glintstone Key"))
    add("Nokron, Eternal City Start",
        can_get("CL/(WD): Remembrance of the Starscourge - mainboss drop"))
    add("Moonlight Altar", Has("Dark Moon Ring"))

    # deathless_routing option REMOVED 2026-07-02 (v0.1 one-sound-mode): the default branch is
    # hardcoded. VM Dungeon is reachable via the RLA Abductor Virgin death-grab (deterministic
    # scripted route) or from Volcano Manor itself; the Drawing-Room-Key-only variant is gone.
    add("Volcano Manor Dungeon",
        can_go_to("Raya Lucaria Academy Main") | can_go_to("Volcano Manor"))

    add("Leyndell, Royal Capital", has_enough_great_runes(o.great_runes_required.value))
    add("Erdtree", has_enough_great_runes(o.great_runes_final_boss.value))
    add("Mountaintops of the Giants",
        has_enough_great_runes(o.great_runes_mountaintops.value))
    # "Hidden Path to the Haligtree" medallion-halves gate DELETED 2026-07 (region-spine
    # surgery): the medallions are unpooled; Hidden Path now rides Snowfield Lock's
    # always-on entrance clause (region_lock_data.py, Track A).

    # --- smithing/somber bell-bearing gates (L209-219) ---
    if o.smithing_bell_bearing_option.value == 1 and not o.soft_progression.value:
        add("Altus Plateau", bell_bearings_required(1, False))
        add("Capital Outskirts", bell_bearings_required(2, False))
        add("Flame Peak", bell_bearings_required(3, False))
        add("Farum Azula Main", bell_bearings_required(4, False))
        add("Dragonbarrow", bell_bearings_required(1, True))
        add("Capital Outskirts", bell_bearings_required(2, True))
        add("Flame Peak", bell_bearings_required(3, True))
        add("Farum Azula Main", bell_bearings_required(4, True))
        add("Leyndell, Ashen Capital", bell_bearings_required(5, True))

    # --- early legacy dungeons (L221-224) ---
    if o.early_legacy_dungeons:
        add("Liurnia of The Lakes", Has("Rusty Key"))
        add("Caelid", Has("Rusty Key"))
        add("Altus Plateau", Has("Academy Glintstone Key"))

    # --- DLC (L227-290) ---
    if o.enable_dlc:
        # Gravesite Plain geographic entry-condition machinery DELETED 2026-07 (region-spine
        # surgery, spec SS3.5 audit rider): the dlc_timing==2 medallion+remembrance gate and
        # the else-branch remembrance-only gate are both gone. Gravesite Plain's entry gate
        # is its lock ALONE now (Gravesite Lock, added unconditionally in
        # region_lock_data.py under enable_dlc -- Track A). The lock IS the timing; no
        # medallion clause, no Mohg/Radahn remembrance entry gates. dlc_timing itself is
        # NOT deleted here (a follow-up pass owns removing the option), but its
        # Gravesite-Plain-gating effect is gone in both branches.
        if o.dlc_timing != 2:
            add("Mohgwyn Palace",
                Has("Pureblood Knight's Medal") | can_go_to("Consecrated Snowfield"))
            if o.dlc_timing == 0:
                add("Altus Plateau", Has("Pureblood Knight's Medal"))
                add("Caelid", Has("Pureblood Knight's Medal"))
        if o.messmer_kindle:
            add("Enir Ilim",
                Has("Messmer's Kindling Shard",
                    count=min(o.messmer_kindle_required.value, o.messmer_kindle_max.value)))
        else:
            add("Enir Ilim", Has("Messmer's Kindling"))
        add("The Four Belfries (Chapel of Anticipation)", has_enough_imbued(4))
        add("The Four Belfries (Nokron)", has_enough_imbued(4))
        add("The Four Belfries (Farum Azula)", has_enough_imbued(4))
        add("Rauh Ruins Limited",
            has_enough_imbued(4) | can_go_to("Ancient Ruins of Rauh"))
    else:
        add("The Four Belfries (Chapel of Anticipation)", has_enough_imbued(3))
        add("The Four Belfries (Nokron)", has_enough_imbued(3))
        add("The Four Belfries (Farum Azula)", has_enough_imbued(3))

    return rules
