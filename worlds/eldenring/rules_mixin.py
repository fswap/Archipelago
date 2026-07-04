"""Elden Ring apworld — rules layer (mixin).

Extracted verbatim from ``__init__.py`` on 2026-07-01 as pure code motion: the
``set_rules`` method plus its rule-predicate helpers and the ``_add_*_rule`` attach
wrappers were lifted out of the ``EldenRing`` world class into this mixin to shrink
``__init__.py`` (which had grown large enough to truncate on read/write). No logic
was changed. ``EldenRing(EldenRingRules, World)`` inherits these methods; each still
binds to the world instance through ``self``. The mixin is listed first so its
``set_rules`` overrides ``World``'s default.
"""
from __future__ import annotations

from typing import List, Set, Union

from BaseClasses import CollectionState, Entrance, ItemClassification, LocationProgressType
from worlds.generic.Rules import CollectionRule, ItemRule, add_rule, add_item_rule

from . import region_spine
from .grace_data import REGION_LOCK_ITEM
from .items import item_table
from .locations import location_tables, location_dictionary
from .merchant_bells import resolve_merchant_bells
from .stone_bells import PROGRESSIVE_SMITHING_BELL, PROGRESSIVE_SOMBER_BELL
from .rules_data import region_rules_table, build_region_rules
from .region_lock_data import build_region_lock_rules, build_region_lock_location_rules
from .warp_rules import build_warp_rules


class EldenRingRules:
    """Rule-building methods for :class:`EldenRing` (see module docstring)."""

    def set_rules(self) -> None: #MARK: Rules
        # [key-gates] collect + EXCLUDE the key/heart-gated checks added by these two dedicated methods
        # (every rule in them uses _has_enough_keys / _has_enough_hearts). The flag drives
        # _add_location_rule / _add_entrance_rule to mark the gated check (or whole region) filler-only.
        self._collecting_key_gates = True  # v0.1 single mode: key gates always soft
        self._key_rules() # make option to choose master or normal rules
        #self._master_key_rules()

        self._dragon_communion_rules()
        self._collecting_key_gates = False
        # imbued keys gate the Four Belfries teleport sub-regions: always EXCLUDED
        # (v0.1 single mode -- entrance rules stay as plain always-true gates below)
        for _r in ("The Four Belfries (Chapel of Anticipation)", "The Four Belfries (Nokron)", "The Four Belfries (Farum Azula)"):
            self._exclude_region(_r)
        self._add_shop_rules()
        self._add_npc_rules()
        self._add_remembrance_rules()
        self._add_equipment_of_champions_rules()
        self._add_allow_useful_location_rules()
        
        # indirect connections

        self.multiworld.register_indirect_condition(self.get_region("Altus Plateau"), self.get_entrance("Go To Wailing Dunes"))
        self.multiworld.register_indirect_condition(self.get_region("Caelid"), self.get_entrance("Go To Sellia Crystal Tunnel"))
        self.multiworld.register_indirect_condition(self.get_region("Deeproot Depths Upper"), self.get_entrance("Go To Deeproot Depths"))
        self.multiworld.register_indirect_condition(self.get_region("Deeproot Depths"), self.get_entrance("Go To Ainsel River Main"))
        self.multiworld.register_indirect_condition(self.get_region("Deeproot Depths"), self.get_entrance("Go To Leyndell, Royal Capital"))
        self.multiworld.register_indirect_condition(self.get_region("Volcano Manor"), self.get_entrance("Go To Volcano Manor Dungeon"))
        self.multiworld.register_indirect_condition(self.get_region("Volcano Manor Dungeon"), self.get_entrance("Go To Volcano Manor"))
        
        # World Logic
        if self.options.world_logic < 3:
            self._region_lock()
            self._region_lock_warp_access()
            if self.options.soft_logic:
                self.multiworld.register_indirect_condition(self.get_region("Altus Plateau"), self.get_entrance("Go To Caelid"))
                # Soft-order (#13): keep the early Varré/Pureblood-medal rush to Mohgwyn
                # out of sphere 1. Mohgwyn is reachable from Limgrave via the sending gate,
                # so a sphere-1 Mohgwyn Lock + medal could open a tier-5 region immediately.
                # Item check only (no _can_go_to chaining, which recurses — see deathless note);
                # mirrors the region_boss "Liurnia Bosses" gate. Cannot deadlock: nothing on the
                # path to Liurnia needs Mohgwyn, and the DLC entry (Mohgwyn→Gravesite) is meant
                # to be mid-game.
           
            # "BS: Stonesword Key - behind wooden platform" # in limgrave rn
            # "BS: Smithing Stone [1] x3 - corpse hanging off edge" # on Bridge of Sacrifice idk where wall for WP will be
            
            # if haligtree region lock adds a key to the evergaol these items would require it
            # "CS/(OLT): Ghost Glovewort [9] - enemy drop in evergaol, NW side of town middle of buildings"
            # "CS/(OLT): Ghost Glovewort [9] - enemy drop in evergaol, S side of town by fog wall"
            # "CS/(OLT): Ghost Glovewort [9] - enemy drop in evergaol, up stairs from where the grace would be"
            # "CS/(OLT): Ghost Glovewort [9] - enemy drop in evergaol, under stairs to haligtree seal"
            
            # only in region lock since it can be bypassed by ruin-strewn precipice

        # Custom Rules
        
        # Removed 2026-06-14: the "funny shackle rule" gated Stormveil Castle on Margit's Shackle and
        # Mohgwyn Palace on Mohg's Shackle (enemy_rando-off only). Neither shackle is required to ENTER
        # those regions in vanilla -- each only staggers its boss, not the entrance. False gates, dropped.

        # Item Rules
            
        # Paintings
        self._add_location_rule("LG/SR: Incantation Scarab - \"Homing Instinct\" Painting reward to NW", "\"Homing Instinct\" Painting")
        self._add_location_rule("DB/MEE: Ash of War: Rain of Arrows - \"Redmane\" Painting reward down hidden cliff E of MEE", "\"Redmane\" Painting")
        self._add_location_rule("WP/CP: Warhawk Ashes - \"Prophecy\" Painting reward to N", "\"Prophecy\" Painting")
        self._add_location_rule([
            "LL/BCM: Juvenile Scholar Cap - \"Resurrection\" Painting reward to S by graves",
            "LL/BCM: Juvenile Scholar Robe - \"Resurrection\" Painting reward to S by graves",
            "LL/BCM: Larval Tear - \"Resurrection\" Painting reward to S by graves",
            ], "\"Resurrection\" Painting")
        self._add_location_rule("AP/RP: Harp Bow - \"Champion's Song\" Painting reward to S top of grave steps", "\"Champion's Song\" Painting")
        self._add_location_rule("AP/(DMV): Fire's Deadly Sin - \"Flightless Bird\" Painting reward S from boss","\"Flightless Bird\" Painting")
        self._add_location_rule("MotG/SR: Greathood - Painting reward NW of SR on bridge", "\"Sorcerer\" Painting")
        
        # LL/CFT, gesture + glint crown items
        self._add_location_rule([
            "LL/(CFT): Cannon of Haima - in chest atop tower, requires using Erudition gesture while wearing any Glintstone Crown",
            "LL/(CFT): Gavel of Haima - in chest atop tower, requires using Erudition gesture while wearing any Glintstone Crown",
            ],lambda state: state.has("Erudition", self.player) and
            (state.has("Twinsage Glintstone Crown", self.player) or state.has("Olivinus Glintstone Crown", self.player) or
             state.has("Lazuli Glintstone Crown", self.player) or state.has("Karolos Glintstone Crown", self.player) or
             state.has("Witch's Glintstone Crown", self.player)))
        
        self._add_location_rule("LL/(CT): Memory Stone - top of tower, requires Erudition gesture", "Erudition")
        
        # vm drawing room, stuff that needs key
        self._add_location_rule([ 
                "VM/VM: Recusant Finger - on the table in the drawing room",
                "VM/VM: Letter from Volcano Manor (Istvan) - on the table in the drawing room",
                "VM/VM: Perfume Bottle - in the first room on the right",
                "VM/VM: Budding Horn x3 - behind the illusory wall in the right room, next to the stairs",
                "VM/VM: Fireproof Dried Liver - behind the illusory wall in the right room, down the stairs",
                "VM/VM: Nomadic Warrior's Cookbook [21] - behind the illusory wall in the right room, all the way around down the dead-end",
                "VM/VM: Depraved Perfumer Carmaan - behind the illusory wall in the right room, all the way around down the dead-end behind the illusory wall",
                "VM/VM: Bloodhound Claws - enemy drop behind the illusory wall in the right room, down the stairs"
            ], "Drawing-Room Key")
        
        if not self.options.royal_access:
            for location in location_tables["Leyndell, Royal Capital"]:
                location.missable = True
        
        # MotG/SR spirit summon item
        self._add_location_rule(["MotG/(SR): Primal Glintstone Blade - in chest underground behind jellyfish seal"
            ], lambda state: state.has("Spirit Jellyfish Ashes", self.player) and state.has("Spirit Calling Bell", self.player))

        # CS/AR spirit summon item
        self._add_location_rule(["CS/(AR): Graven-Mass Talisman - top of rise, use Fanged Imp Ashes or bewitching branch to make spirit enemies fight"
            ], lambda state: state.has("Fanged Imp Ashes", self.player) and state.has("Spirit Calling Bell", self.player))

        # Region Rules
        
        # Stormveil Castle (Rampart Tower -> Secluded Cell/Godrick) is reached via the KEYLESS
        # rampart route in vanilla; the Rusty Key only opens an optional shortcut door, and the key
        # itself is found in Stormveil Start (before this gate). Gating the region on it falsely
        # walls off Godrick + the Stormveil grace bundle in shuffled seeds. Removed 2026-06-14.
        # self._add_entrance_rule("Stormveil Castle", "Rusty Key")
        # [rule_builder migration] geographic entrance rules from the declarative table
        # (rules_data.region_rules_table). Single-clause, non-region-locked regions only;
        # multi-clause / dynamic / region-locked entrances stay on _add_entrance_rule below.
        # [rule_builder migration — Phase 5] full geographic entrance rules from the
        # declarative builder (rules_data.build_region_rules). AND-attached via add_rule so
        # region-lock / warp clauses still stack. Replaces the Phase-1 set_rule table loop
        # and every imperative _add_entrance_rule below (now neutralized).
        for _rb_region, _rb_rule in build_region_rules(self).items():
            if _rb_region in self.created_regions:
                _rb_resolved = _rb_rule.resolve(self)
                self.register_rule_dependencies(_rb_resolved)
                add_rule(self.multiworld.get_entrance(f"Go To {_rb_region}", self.player), _rb_resolved)

        
        # festival // altus grace touch or ranni quest stuff
        self._add_location_rule([
            "CL/(RC): Smithing Stone [6] - in church during festival",
        ], lambda state: self._can_go_to(state, "Altus Plateau"))
        
        
           
                
        # also from RLA side you can get back into main hall through imp statue
        
        # Great Runes to access the final boss: gate the Erdtree (Radagon / Elden Beast).
        # Default 0 = no extra requirement.
        
        
        
        # Smithing bell bearing rules
        # soft_progression demotes ALL "Bell Bearing" items (incl. the Progressive Smithing /
        # Somberstone bells) progression -> useful (see ~L309). These entrance rules gate Altus /
        # Capital Outskirts / Flame Peak / Farum on those bells, but can_beat_game() collects only
        # 'advancement' items -- so once demoted the gate is unsatisfiable and the seed reports
        # "unbeatable" (fill precollects useful items and still passes: the fill-OK/unbeatable
        # split). The progression-randomize feature only makes sense while the bells stay
        # progression, so skip the gate when soft_progression has pulled them down to useful.
        # (patch_apworld_softprog_bellgate_fix.py)
        
        
        # DLC Rules
        if self.options.enable_dlc:
                
            
            self.multiworld.register_indirect_condition(self.get_region("Ancient Ruins of Rauh"), self.get_entrance("Go To Rauh Ruins Limited"))
            self.multiworld.register_indirect_condition(self.get_region("Shadow Keep, Church District"), self.get_entrance("Go To Shadow Keep Storehouse"))
            
            # MARK: DLC Rules
            
            # dlc paintings
            self._add_location_rule("GP/BG: Serpent Crest Shield - painting reward SE of BG", "\"Incursion\" Painting")
            self._add_location_rule("RB/NNM: Spiraltree Seal - \"The Sacred Tower\" Painting reward SW of NNM", 
                                    lambda state: state.has("\"The Sacred Tower\" Painting", self.player) and self._can_go_to(state, "Enir Ilim"))
            self._add_location_rule("JP/JPM: Rock Heart - \"Domain of Dragons\" Painting reward, after first spirit spring head down return path", "\"Domain of Dragons\" Painting")
            
            # dlc imbued
            
            # furnace golem / Hefty Furnace Pot
            self._add_location_rule([
                "RR/(RU): Bloodsucking Cracked Tear - inactive furnace golem, use Hefty Furnace Pot",
                "RR/(RU): Furnace Visage - inactive furnace golem, use Hefty Furnace Pot",
                "RR/(RU): Giant Golden Arc - in chest within building behind inactive furnace golem",
                "SA/BLV: Cerulean-Sapping Cracked Tear - furnace golem to NE along path",
                "SA/BLV: Furnace Visage - furnace golem to NE along path",
                "CHG/CHG: Glovewort Crystal Tear - furnace golem to W above river",
                "CHG/CHG: Furnace Visage - furnace golem to W above river"
                ], lambda state: state.has("Crafting Kit", self.player) 
                    and state.has("Greater Potentate's Cookbook [2]", self.player) and state.has("Hefty Cracked Pot", self.player))
                
            # DLC region rules
            
            
            
            
            # the funny gaol
                    
        
        if self.options.ending_condition == 4:
            # Capital goal: beat Morgott (Leyndell Royal Capital mainboss). Reachability is the
            # great-rune gate on Leyndell, Royal Capital (set above) -- nothing past it is required.
            self.multiworld.completion_condition[self.player] = \
                lambda state: self._can_get(state, region_spine.MORGOTT_GOAL_LOCATION)
        elif self.options.ending_condition == 5:
            # DLC mini-campaign: beat Messmer (the kept front-half ends here; everything past
            # it is sealed, so this single drop = victory).
            self.multiworld.completion_condition[self.player] = \
                lambda state: self._can_get(state, region_spine.MESSMER_GOAL_LOCATION)
        elif self.options.ending_condition == 6:
            # Godrick mini-campaign: beat Godrick the Grafted (the kept front three steps end
            # here; everything past Stormveil is sealed, so this single drop = victory).
            self.multiworld.completion_condition[self.player] = \
                lambda state: self._can_get(state, region_spine.GODRICK_GOAL_LOCATION)
        elif self.options.ending_condition <= 1:
            if self.options.enable_dlc and self.options.ending_condition == 0:
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "EI/GD: Circlet of Light - interact with memory after mainboss")
            else:
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "ET: Elden Remembrance - mainboss drop")
                # make this the mend the elden ring event, idk how todo that rn
        elif self.options.ending_condition == 2:
            if self.options.enable_dlc:
                self._add_location_rule("Victory", lambda state: self._can_get_all(state, (self.location_name_groups["Remembrance"] | self.location_name_groups["Remembrance DLC"])))
                self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
            else:
                self._add_location_rule("Victory", lambda state: self._can_get_all(state, self.location_name_groups["Remembrance"]))
                self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
        else:
            if self.options.enable_dlc:
                self._add_location_rule("Victory", lambda state: self._can_get_all(state, (self.location_name_groups["Boss Reward"] | self.location_name_groups["Boss Reward DLC"])))
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "Victory")
            else:
                self._add_location_rule("Victory", lambda state: self._can_get_all(state, self.location_name_groups["Boss Reward"]))
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "Victory")
        
        # SPELL_SHOP_FILL_PATCH REMOVED 2026-07-03 (Alaric): spell_shop_spells_only deleted --
        # a solo-rando idea that doesn't fit AP, and its spell-only rule repeatedly starved fill
        # (filler-replacement / pool_builder converting spells -> runes). Shops take any item now.

        # dungeon_sweep reachability modeling (patch_dungeon_sweep_logic 2026-07-02): runs
        # AFTER every other rule attachment so the OR wraps each member's final rule.
        self._apply_dungeon_sweep_logic()

        # self.visualize_world()
        
    def _apply_dungeon_sweep_logic(self) -> None:
        """dungeon_sweep members are auto-CHECKED at runtime the moment their trigger fires
        (client `dungeonSweeps` consumer), so in PRACTICE a member is obtainable whenever its
        trigger is reachable. Mirror that here: OR each member's access rule with its trigger's
        reachability. Strictly LOOSENING -- the runtime grants the member regardless of its own
        rule, so this can never create a softlock; it relieves accessibility:full pressure and
        lets fill legally use swept members once the trigger is in logic. grace_sweep is NOT
        modeled (it unlocks traversal graces; the region-lock abstraction already covers
        movement). MUST run last in set_rules: the OR wraps each member's FINAL rule (anything
        AND-attached afterwards would wrongly bind outside the OR)."""
        if not self.options.dungeon_sweep.value:
            return
        _sweeps, _groups = self._compute_dungeon_sweeps()
        _n = 0
        for _trigger, _members in _groups:
            for _member in _members:
                if _member is _trigger or _member.address is None:
                    continue
                add_rule(_member,
                         lambda state, _t=_trigger: _t.can_reach(state),
                         combine="or")
                _n += 1
        if _n:
            from logging import warning
            warning(f"{self.player_name}: dungeon_sweep logic: {_n} member checks are also "
                    f"in-logic via their sweep trigger.")

    def _can_get_all(self, state: CollectionState, locations: Set) -> bool:
        """Can get all locations."""
        for location in locations:
            if not self._can_get(state, location):
                return False
        return True
    
    def _region_lock_warp_access(self) -> None:
        """Create the grace-warp entrances from the declarative builder (warp_rules.build_warp_rules).

        Behaviour-preserving port of the former imperative body (SPEC-region-rules-rulebuilder.md
        §4h): additive "Warp To {region}" entrances gated on each region\'s own lock. Inert when
        region_access != warp (the builder returns no edges)."""
        warp = build_warp_rules(self)
        hub = self.get_region(warp["hub"])
        for edge in warp["edges"]:
            entrance = Entrance(self.player, edge.name, hub)
            hub.exits.append(entrance)
            entrance.connect(self.get_region(edge.target))
            resolved = edge.rule.resolve(self)
            self.register_rule_dependencies(resolved)
            add_rule(entrance, resolved)

    def _region_lock(self) -> None:
        """Apply region-lock ACCESS clauses from the declarative builder (region_lock_data).

        Behaviour-preserving port of the former imperative body (SPEC-region-rules-rulebuilder.md
        §4e): ANDs each region\'s Has(lock)/chokepoint clause onto its "Go To {region}" entrance,
        plus the Godrick goal-location lock. Inert under world_logic == region_bosses (the builder
        returns {}). Attaching via resolve + register_rule_dependencies + add_rule mirrors what
        World.set_rule does for cache registration, but AND-stacks onto any existing geographic clause
        instead of replacing it."""
        for region, rule in build_region_lock_rules(self).items():
            # Regions with no geographic "Go To" entrance (Limgrave: the star center is only
            # ever ENTERED via its hub warp edge under the Roundtable re-root) carry their lock
            # on the "Warp To {region}" edge instead (_region_lock_warp_access attaches
            # edge.rule = Has(lock) there). Skipping here is correct, not lenient: there is no
            # geographic entrance to gate. SPEC-region-spine-surgery.md SS3.1.
            try:
                entrance = self.multiworld.get_entrance(f"Go To {region}", self.player)
            except KeyError:
                continue
            resolved = rule.resolve(self)
            self.register_rule_dependencies(resolved)
            add_rule(entrance, resolved)
        for location, rule in build_region_lock_location_rules(self).items():
            loc = self.multiworld.get_location(location, self.player)
            resolved = rule.resolve(self)
            self.register_rule_dependencies(resolved)
            add_rule(loc, resolved)
                
                # TODO entrance rules          
    
    def _key_rules(self) -> None: # MARK: SSK Rules
        # in order from early game to late game each rule needs to include the last count for an area
        
        # limgrave
        self._add_entrance_rule("Fringefolk Hero's Grave", lambda state: self._has_enough_keys(state, 3)) # 2
        self._add_location_rule("LG/(SWV): Green Turtle Talisman - behind imp statue", lambda state: self._has_enough_keys(state, 3)) # 1
        
        #self._add_entrance_rule("Roundtable Hold", lambda state: self._has_enough_keys(state, 3))
        # roundtable
        self._add_location_rule([
            "RH: Crepus's Black-Key Crossbow - behind imp statue in chest", "RH: Black-Key Bolt x20 - behind imp statue in chest", # 1
            "RH: Assassin's Prayerbook - behind second imp statue in chest", # 2
            ], lambda state: self._has_enough_keys(state, 6))
        
        #self._add_entrance_rule("Weeping Peninsula", lambda state: self._has_enough_keys(state, 6))
        # weeping
        self._add_location_rule([
            "WP/(TCC): Nomadic Warrior's Cookbook [9] - behind imp statue", # 1
            "WP/(WE): Radagon's Scarseal - boss drop Evergaol", # 1
            ], lambda state: self._has_enough_keys(state, 8))
        
        #self._add_entrance_rule("Stormveil Castle", lambda state: self._has_enough_keys(state, 8))
        # stormveil
        self._add_location_rule([
            "SV/LC: Godslayer's Seal - left chest behind imp statue in storeroom SE of massive courtyard", # 1a
            "SV/LC: Godskin Prayerbook - right chest behind imp statue in storeroom SE of massive courtyard", # 1a
            "SV/RT: Iron Whetblade - shortcut elevator to SE, to N through door, behind imp statue", # 1b
            "SV/RT: Hawk Crest Wooden Shield - shortcut elevator to SE, to N through door, behind imp statue", # 1b
            "SV/RT: Miséricorde - shortcut elevator to SE, to N through door, behind imp statue", # 1b
            ], lambda state: self._has_enough_keys(state, 10))
        
        #self._add_entrance_rule("Siofra River", lambda state: self._has_enough_keys(state, 10))
        # siofra
        # for leaving siofra to caelid ravine
        self._add_location_rule([
            "CL/DSW: Spiked Palisade Shield - to W follow ravine",
            "CL/DSW: Stonesword Key - to S",
            "CL/CCO: Great-Jar's Arsenal - beat Great Jar's knights",
            ], lambda state: self._has_enough_keys(state, 12) and 
            self._can_go_to(state, "Siofra River")) # 2
        
        #self._add_entrance_rule("Liurnia of The Lakes", lambda state: self._has_enough_keys(state, 12))
        # liurnia
        self._add_location_rule([
            "LL/(BKC): Rosus' Axe - behind imp statue near boss door", # 1a
            "LL/(CC): Nox Mirrorhelm - behind imp statue, in SW corner", # 1b
            ], lambda state: self._has_enough_keys(state, 16))
        self._add_entrance_rule("Academy Crystal Cave", lambda state: self._has_enough_keys(state, 16)) # 2
        
        #self._add_entrance_rule("Altus Plateau", lambda state: self._has_enough_keys(state, 16))
        # altus
        self._add_location_rule([
            "AP/(SHG): Crimson Seed Talisman - behind imp statue", # 1a
            "AP/(SHG): Dragoncrest Shield Talisman +1 - ride up first cleaver, behind imp statue", # 1b
            "AP/WhR: Pearldrake Talisman +1 - in chest underground behind a imp statue", # 1c
            "AP/GLE: Godfrey Icon - boss drop Evergaol", # 1d
            ], lambda state: self._has_enough_keys(state, 22))
        self._add_entrance_rule("Old Altus Tunnel", lambda state: self._has_enough_keys(state, 22)) # 2
        
        #self._add_entrance_rule("Caelid", lambda state: self._has_enough_keys(state, 22))
        # caelid
        self._add_entrance_rule("Gaol Cave", lambda state: self._has_enough_keys(state, 25)) # 2
        self._add_location_rule("CL/(FR): Sword of St. Trina - in chest underground behind imp statue", 
                                lambda state: self._has_enough_keys(state, 25)) # 1
        
        #self._add_entrance_rule("Nokron, Eternal City Start", lambda state: self._has_enough_keys(state, 25))
        # nokron
        self._add_location_rule([
            "NR/(NSG): Mimic Tear Ashes - in chest behind imp statue upper interior", # 1a
            "NR/(NSG): Smithing Stone [3] - behind imp statue upper interior", # 1a
            ], lambda state: self._has_enough_keys(state, 26))
        
        #self._add_entrance_rule("Mt. Gelmir", lambda state: self._has_enough_keys(state, 26))
        # mt gelmir
        self._add_location_rule([
            "MtG/(WC): Lightning Scorpion Charm - behind imp statue", # 1
            ], lambda state: self._has_enough_keys(state, 29))
        self._add_entrance_rule("Seethewater Cave", lambda state: self._has_enough_keys(state, 29)) # 2
        
        #self._add_entrance_rule("Volcano Manor Entrance", lambda state: self._has_enough_keys(state, 29))
        # volcano
        self._add_location_rule([
            "VM/PTC: Crimson Amber Medallion +1 - behind imp statue W of town", # 1
            "VM/TE: Seedbed Curse - NW of shortcut elevator, after imp statue, lower part of big cage room to SW", # 2a
            "VM/TE: Ash of War: Royal Knight's Resolve - NW of shortcut elevator, after imp statue, lower part of big cage room to NE", # 2a
            "VM/TE: Somber Smithing Stone [7] - NW of shortcut elevator, after imp statue, lower part of big cage room outside to SW", # 2a
            "VM/TE: Dagger Talisman - NW of shortcut elevator, after imp statue, drop to hidden path top item", # 2a
            "VM/TE: Rune Arc - NW of shortcut elevator, after imp statue, drop to hidden path lower item", # 2a
            ], lambda state: self._has_enough_keys(state, 32))
        
        #self._add_entrance_rule("Capital Outskirts", lambda state: self._has_enough_keys(state, 32))
        # capital outskirts
        self._add_location_rule([
            "CO/(AHG): Golden Epitaph - behind imp statue", # 1
            ], lambda state: self._has_enough_keys(state, 33))
        
        #self._add_entrance_rule("Ainsel River Main", lambda state: self._has_enough_keys(state, 33))
        # nokstella
        self._add_location_rule([
            "NS/NEC: Nightmaiden & Swordstress Puppets - in chest behind imp statue to W up stairs, left before bridge", # 1
            ], lambda state: self._has_enough_keys(state, 34))
        
        #self._add_entrance_rule("Moonlight Altar", lambda state: self._has_enough_keys(state, 34))
        # moonlight altar
        self._add_location_rule([
            "MA/(LER): Cerulean Amber Medallion +2 - in chest under illusory floor behind imp statue", # 1
            ], lambda state: self._has_enough_keys(state, 35))
        
        #self._add_entrance_rule("Mountaintops of the Giants", lambda state: self._has_enough_keys(state, 35))
        # mountaintops
        self._add_location_rule([
            "FP/(GCHG): Flame, Protect Me - behind imp statue", # 1a
            "FP/(GCHG): Cranial Vessel Candlestand - upper room after fire spitter, behind imp statue", # 1b
            ], lambda state: self._has_enough_keys(state, 39))
        self._add_entrance_rule("Spiritcaller Cave", lambda state: self._has_enough_keys(state, 39)) # 2
        
        #self._add_entrance_rule("Farum Azula", lambda state: self._has_enough_keys(state, 39))
        # farum
        self._add_location_rule([ # entire area behind a imp staute lol
            "FA/DTL: Lord's Rune - to SE in fountain", # 2
            "FA/DTL: Nascent Butterfly x2 - to SE down left stairs by tree", # 2
            "FA/DTL: Golden Seed - seedtree to SE up right path", # 2
            "FA/DTL: Rune Arc - to SE up right path beside seedtree", # 2
            "FA/DTL: Smithing Stone [8] - to SE up right path, E of seedtree behind gazebo", # 2
            "FA/DTL: Golden Rune [12] - to SE up right path, E of seedtree left of gazebo by tree", # 2
            "FA/DTL: Smithing Stone [7] - to SE up right path, E of seedtree left of gazebo on ledge", # 2
            "FA/DTL: Golden Lightning Fortification - scarab to SE up right path, SW of seedtree", # 2
            "FA/DTL: Smithing Stone [8] - to SE up right path, SW of seedtree", # 2
            "FA/DTL: Golden Rune [12] - to SE up right path, W of seedtree on platform after crossing building", # 2
            "FA/DTL: Smithing Stone [7] - to SE up right path, W of seedtree on second platform after crossing building", # 2
            "FA/DTL: Ancient Dragon Apostle's Cookbook [4] - to SE up right path, W of seedtree, far end of path in building", # 2
            "FA/DTL: Somber Smithing Stone [8] - to SE up right path, W of seedtree, far end of path left of building", # 2
            "FA/DTL: Smithing Stone [8] - to SE up right path, W of seedtree, far end of path drop down left of building", # 2
            "FA/DTL: Dragonwound Grease x2 - to S under fallen building", # 2
            "FA/DTL: Shard of Alexander - fight Alexander to SW", # 2
            "FA/DTL: Alexander's Innards - fight Alexander to SW", # 2
            ], lambda state: self._has_enough_keys(state, 41))
        
        #self._add_entrance_rule("Consecrated Snowfield", lambda state: self._has_enough_keys(state, 41))
        # snowfield
        self._add_entrance_rule("Cave of the Forlorn", lambda state: self._has_enough_keys(state, 43)) # 2
        
        #self._add_entrance_rule("Miquella's Haligtree", lambda state: self._has_enough_keys(state, 43))
        # haligtree +3
        self._add_location_rule([
            "EBH/PR: Triple Rings of Light - drop down to E, in chest behind imp statue", # 1
            "EBH/EIW: Marika's Soreseal - to SE past the imp statue in lower section", # 2
            ], lambda state: self._has_enough_keys(state, 46))
        
    def _dragon_communion_rules(self) -> None: # MARK: Dragon Rules
        """Rules for dragon communion"""
        self._add_location_rule([
            "LG/(CDC): Dragonfire - Dragon Communion", # 1
            "LG/(CDC): Dragonclaw - Dragon Communion", # 1
            "LG/(CDC): Dragonmaw - Dragon Communion", # 1
            ], lambda state: self._has_enough_hearts(state, 3)) 
        
        # caelid dragon communion
        self._add_location_rule([
            "CL/(CDC): Glintstone Breath - Dragon Communion", # 1
            "CL/(CDC): Rotten Breath - Dragon Communion", # 1
            "CL/(CDC): Dragonice - Dragon Communion", # 1
            "CL/(CDC): Agheel's Flame - Dragon Communion, kill boss in LG, NW of DBR", # 2
            "CL/(CDC): Greyoll's Roar - Dragon Communion, kill enemy in CL, W of FF", # 3
            "CL/(CDC): Ekzykes's Decay - Dragon Communion, kill boss to NW of here", # 2
            ], lambda state: self._has_enough_hearts(state, 13)) 
        
        self._add_location_rule("CL/(CDC): Smarag's Glintstone Breath - Dragon Communion, kill boss in LL, SW of ACC", 
            lambda state: self._has_enough_hearts(state, 15) and self._can_go_to(state, "Liurnia of The Lakes")) # 2
        self._add_location_rule("CL/(CDC): Magma Breath - Dragon Communion, kill boss in MtG, S of FL", 
            lambda state: self._has_enough_hearts(state, 16) and self._can_go_to(state, "Mt. Gelmir")) # 1
        self._add_location_rule("CL/(CDC): Borealis's Mist - Dragon Communion, kill boss in MotG, N of FCM", 
            lambda state: self._has_enough_hearts(state, 18) and self._can_go_to(state, "Mountaintops of the Giants")) # 2
        self._add_location_rule("CL/(CDC): Theodorix's Magma - Dragon Communion, kill boss in CS, SE of CF", 
            lambda state: self._has_enough_hearts(state, 20) and self._can_go_to(state, "Consecrated Snowfield")) # 2
        
        if self.options.enable_dlc: # dlc
            self._add_location_rule("JP/GADC: Ghostflame Breath - Grand Dragon Communion", lambda state: self._has_enough_hearts(state, 23)) # 3
    
    def _has_enough_great_runes(self, state: CollectionState, runes_required: int) -> bool:
        """Returns whether the given state has enough great runes."""
        return (state.count_from_list([
            "Godrick's Great Rune","Rykard's Great Rune","Radahn's Great Rune",
            "Morgott's Great Rune","Mohg's Great Rune","Malenia's Great Rune",
            "Great Rune of the Unborn"], self.player) >= runes_required)
    
    def _has_enough_keys(self, state: CollectionState, req_keys: int) -> bool:
        """Always True (v0.1 single sound mode): counting found keys cannot model
        SPENDING them, so key gates are open in logic and their checks EXCLUDED."""
        return True
        
    
    def _has_bloody_finger(self, state: CollectionState) -> bool:
        """Returns whether the given state has any bloody fingers"""
        return (state.count_from_list([
            "Festering Bloody Finger", "Festering Bloody Finger x2", "Festering Bloody Finger x3",
            "Festering Bloody Finger x5", "Festering Bloody Finger x6", "Festering Bloody Finger x8",
            "Festering Bloody Finger x10"], self.player) >= 1)
    
    def _has_enough_hearts(self, state: CollectionState, req_hearts: int) -> bool:
        """Always True (v0.1 single sound mode) -- see _has_enough_keys."""
        return True
    

    def _add_shop_rules(self) -> None:
        """Adds rules for items unlocked in shops."""

        # Scrolls
        scrolls = [
            ("Academy Scroll", ["Great Glintstone Shard", "Swift Glintstone Shard"]),
            ("Conspectus Scroll", ["Glintstone Cometshard", "Star Shower"]),
            ("Royal House Scroll", ["Glintblade Phalanx", "Carian Slicer"])
        ]

        # Prayerbooks
        books = [
            ("Two Fingers' Prayerbook", ["Lord's Heal", "Lord's Aid"]),
            ("Assassin's Prayerbook", ["Assassin's Approach", "Darkness"]),
            ("Golden Order Principia", ["Radagon's Rings of Light", "Law of Regression"]),
            ("Dragon Cult Prayerbook", ["Lightning Spear", "Honed Bolt", "Electrify Armament"]),
            ("Ancient Dragon Prayerbook", ["Ancient Dragons' Lightning Spear", "Ancient Dragons' Lightning Strike"]),
            ("Fire Monks' Prayerbook", ["O, Flame!", "Surge, O Flame!"]),
            ("Giant's Prayerbook", ["Giantsflame Take Thee", "Flame, Fall Upon Them"]),
            ("Godskin Prayerbook", ["Black Flame", "Black Flame Blade"])
        ]

        for (scroll, scroll_items) in scrolls:
            self._add_location_rule([f"LG/(WR): {s_item} - {scroll}" for s_item in scroll_items], scroll)
        for (book, book_items) in books:
            self._add_location_rule([f"RH: {b_item} - {book}" for b_item in book_items], book)

        # Merchant bell-bearing gate (opt-in): require the merchant's Bell Bearing to
        # buy/check their wares. Resolved against the live shop-location table.
        if self.options.merchant_bell_logic.value == 1:
            for _bell, _locs in resolve_merchant_bells(
                    location_dictionary, bool(self.options.enable_dlc)).items():
                self._add_location_rule(_locs, _bell)
                
    def _add_npc_rules(self) -> None: # MARK: NPC Rules
        """Adds rules for items accessible via NPC quests.

        We list missable locations here even though they never contain progression items so that the
        game knows what sphere they're in.

        Generally, for locations that can be accessed early by killing NPCs, we set up requirements
        assuming the player _doesn't_ so they aren't forced to start killing allies to advance the
        quest.
        """
        # MARK: Varré
        
        self._add_location_rule([ "LL/(RC): Festering Bloody Finger x5 - talk to Varré after beating SV mainboss",
        ], lambda state: self._can_get(state, "SV/SeC: Remembrance of the Grafted - mainboss drop"))
        
        self._add_location_rule([ 
            "AP/(WbR): Great Stars - invade Magus",
            "AP/(WbR): Somber Smithing Stone [6] - invade Magus"
        ], lambda state: self._has_bloody_finger(state))
        
        self._add_location_rule([ "LL/(RC): Lord of Blood's Favor - talk to Varré after invading Magnus in AP",
        ], lambda state: self._can_get(state, "AP/(WbR): Great Stars - invade Magus"))
        
        self._add_location_rule([ 
            "LL/(RC): Pureblood Knight's Medal - talk to Varré after invading Magnus in AP and returning the bloodsoaked Lord of Blood's Favor",
            "LL/(RC): Bloody Finger - talk to Varré after invading Magnus in AP and returning the bloodsoaked Lord of Blood's Favor"
        ], lambda state: self._can_get(state, "AP/(WbR): Great Stars - invade Magus") and state.has("Lord of Blood's Favor", self.player))
        
        self._add_location_rule([ 
            "MP/(MDM): Festering Bloody Finger x6 - invade Varré near DMM grace",
            "MP/(MDM): Varré's Bouquet - invade Varré near DMM grace"
        ], lambda state: self._can_get(state, "LL/(RC): Bloody Finger - talk to Varré after invading Magnus in AP and returning the bloodsoaked Lord of Blood's Favor"))
        
        # MARK: Hyetta
        
        self._add_location_rule([
            "FFP/FFP: Frenzied Flame Seal - given by Hyetta at end of her quest",
            "FFP/FFP: Frenzyflame Stone x5 - given by Hyetta at end of her quest"
        ], lambda state: ( state.has("Shabriri Grape", self.player, 3) and state.has("Fingerprint Grape", self.player)
            and self._can_get(state, "LL/(RS): Shabriri Grape - kill invader Edgar")))
        
        # MARK: Edgar
        
        self._add_location_rule([ 
            "LL/(RS): Raw Meat Dumpling x5 - kill invader Edgar",
            "LL/(RS): Shabriri Grape - kill invader Edgar",
            "LL/(RS): Raw Meat Dumpling 1 - in shack when Edgar invades",
            "LL/(RS): Raw Meat Dumpling 2 - in shack when Edgar invades",
            "LL/(RS): Raw Meat Dumpling 3 - in shack when Edgar invades",
            "LL/(RS): Raw Meat Dumpling 4 - in shack when Edgar invades",
            "LL/(RS): Raw Meat Dumpling 5 - in shack when Edgar invades",
            "WP/BS: Banished Knight's Halberd - kill Edgar at Irina's body or at LL/RS"
        ], lambda state: ( self._can_get(state, "WP/(CM): Grafted Blade Greatsword - boss drop") and self._can_go_to(state, "Liurnia of The Lakes")
            and state.has("Irina's Letter", self.player)))
        
        # MARK: Roderika
        
        self._add_location_rule([ 
            "LG/(SS): Golden Seed - give Roderika Chrysalids' Memento then talk to her at RH, or after SV mainboss item is at SS",
            "SV/RT: Crimson Hood - shortcut elevator to SE, to SE under dead troll, after Roderika becomes a spirit tuner",
        ], "Chrysalids' Memento")
        
        # MARK: Ensha
        
        self._add_location_rule([
            "RH: Clinging Bone - dropped by Ensha, after getting half of secret medallion",
            "RH: Royal Remains Helm - Ensha's spot, after getting half of secret medallion",
            "RH: Royal Remains Armor - Ensha's spot, after getting half of secret medallion",
            "RH: Royal Remains Gauntlets - Ensha's spot, after getting half of secret medallion",
            "RH: Royal Remains Greaves - Ensha's spot, after getting half of secret medallion"
        ], "Snowfield Lock")  # medallions unpooled (SPEC-region-spine-surgery.md SS3.5): both halves are
        # granted IN-GAME on Snowfield Lock receipt (lockGrantItems), so the Ensha invasion fires
        # exactly when the lock arrives -- the AP-logic gate follows the same item.
        
        # MARK: Sellen
        
        self._add_location_rule([ "LG/(WR): Sellian Sealbreaker - given by Sellen after you show her Comet Azur",
        ], lambda state: ( self._can_go_to(state, "Mt. Gelmir")))
        
        self._add_location_rule([ "DB/(SH): Stars of Ruin - lower first big room N side, need Sellian Sealbreaker, given by Lusat",
        ], "Sellian Sealbreaker")
        
        self._add_location_rule([ "LG/(WR): Starlight Shards - given by Sellen after you show her Stars of Ruin",
        ], lambda state: ( self._can_get(state, "DB/(SH): Stars of Ruin - lower first big room N side, need Sellian Sealbreaker, given by Lusat") 
                          and self._can_get(state, "LG/(WR): Sellian Sealbreaker - given by Sellen after you show her Comet Azur")))
        
        self._add_location_rule([ "WP/(WR): Sellen's Primal Glintstone - talk to Sellen",
        ], lambda state: ( self._can_get(state, "LG/(WR): Starlight Shards - given by Sellen after you show her Stars of Ruin")))
        
        self._add_location_rule([ 
            "RLA/RLGL: Glintstone Kris - given by Sellen after siding with her",
            "RLA/RLGL: Shard Spiral - side with Sellen, sold in shop",
            "RLA/RLGL: Witch's Glintstone Crown - side with either",
            "RLA/RLGL: Ancient Dragon Smithing Stone - side with Jerren",
            "RLA/RLGL: Eccentric's Hood - side with Sellen",
            "RLA/RLGL: Eccentric's Armor - side with Sellen",
            "RLA/RLGL: Eccentric's Manchettes - side with Sellen",
            "RLA/RLGL: Eccentric's Breeches - side with Sellen",
            
            # idk if you NEED to side with sellen for these
            "DB/(SH): Lusat's Glintstone Crown - side with Sellen, lower first big room N side, where Lusat was",
            "DB/(SH): Lusat's Robe - side with Sellen, lower first big room N side, where Lusat was",
            "DB/(SH): Lusat's Manchettes - side with Sellen, lower first big room N side, where Lusat was",
            "DB/(SH): Old Sorcerer's Legwraps - side with Sellen, lower first big room N side, where Lusat was",
            "MtG/PSA: Azur's Glintstone Crown - side with Sellen, where Azur was",
            "MtG/PSA: Azur's Glintstone Robe - side with Sellen, where Azur was",
            "MtG/PSA: Azur's Manchettes - side with Sellen, where Azur was"
        ], lambda state: ( self._can_get(state, "WP/(WR): Sellen's Primal Glintstone - talk to Sellen") 
                          and self._can_go_to(state, "Raya Lucaria Academy Library") and state.has("Sellen's Primal Glintstone", self.player)))
        
        # MARK: Thops
        
        self._add_location_rule([ 
            "RLA/SC: Academy Glintstone Staff - on Thops body just outside",
            "RLA/SC: Thops's Barrier - on Thops body just outside",
            "LL/(CIr): Ash of War: Thops's Barrier - scarab in church after Thops moves"
        ], lambda state: ( state.has("Academy Glintstone Key (Thops)", self.player) and self._can_go_to(state, "Raya Lucaria Academy Main")))
        
        # MARK: Corhyn / Goldmask

        self._add_location_rule([ 
            "LRC|LAC/RC: Immutable Shield - Brother Corhyn shop after using Law of Regression and telling Goldmask",
            "LRC|LAC/RC: Flail - kill Brother Corhyn", # goldmask doesnt need corhyn alive
            "LRC|LAC/RC: Corhyn's Robe - kill Brother Corhyn"
        ], "Law of Regression")
        
        self._add_location_rule([ 
            "LAC/RC: Mending Rune of Perfect Order - on Goldmask's body",
            "LAC/RC: Goldmask's Rags - on Goldmask's body",
            "LAC/RC: Gold Bracelets - on Goldmask's body",
            "LAC/RC: Gold Waistwrap - on Goldmask's body"
        ], lambda state: self._can_get(state, "LRC|LAC/RC: Immutable Shield - Brother Corhyn shop after using Law of Regression and telling Goldmask"))
        
        
        # MARK: Enia
        
        self._add_location_rule([ "RH: Talisman Pouch - talk to Enia at 2 great runes or Twin Maiden after farum boss",
        ], lambda state: ( self._has_enough_great_runes(state, 2)))
        
        # MARK: Yura
        
        self._add_location_rule([ 
            "AP/(SCM): Nagakiba - on Yura after RLA invasion",
            "AP/(SCM): Purifying Crystal Tear - invader drop, requires Yura death",
            "AP/(SCM): Eleonora's Poleblade - invader drop, requires Yura death"
        ], lambda state: ( self._can_get(state, "RLA/MAG: Ash of War: Raptor of the Mists - beat invasion at RLA to NE")))
        
        # MARK: Latenna

        self._add_location_rule([ "LL/(SWS): Latenna the Albinauric - talk to Latenna after talking to Albus",
        ], "Snowfield Lock") # medallions unpooled -- Right half granted in-game on Snowfield Lock receipt (lockGrantItems); gate follows the lock
        
        self._add_location_rule([ "CS/(AD): Somber Ancient Dragon Smithing Stone - summon Latenna at her sister and talk to her",
        ], lambda state: ( self._can_get(state, "LL/(SWS): Latenna the Albinauric - talk to Latenna after talking to Albus"))
            and self._can_go_to(state, "Mountaintops of the Giants")) # do you need the ashes? its a prompt summon so idk
        
        # MARK: D
        
        self._add_location_rule([
            "RH: Litany of Proper Death - D shop, after talking to Gurraq",
            "RH: Order's Blade - D shop, after talking to Gurraq",
        ], lambda state: ( self._can_go_to(state, "Dragonbarrow")))
        
        # MARK: D, Twin
        # IDK IF THE WHOLE SET IS NEEDED, OR A SINGLE PIECE, just doing all to be sure
        self._add_location_rule(["DD/AR: Inseparable Sword - kill D Twin at NEC if you killed D, or at end of Fia's quest", 
        ], lambda state: ( 
            (state.has("Twinned Helm", self.player) and state.has("Twinned Armor", self.player)
            and state.has("Twinned Gauntlets", self.player) and state.has("Twinned Greaves", self.player))
            and self._can_get(state, "DD/PDT: Mending Rune of the Death-Prince - on Fia after mainboss")))
        
        # MARK: Rogier
        
        self._add_location_rule(["RH: Rogier's Letter - after giving Black Knifeprint, talk to Ranni, talk to Rogier again", 
        ], lambda state: ( self._can_go_to(state, "Stormveil Castle") and self._can_go_to(state, "Liurnia of The Lakes")
                          and state.has("Black Knifeprint", self.player)))
        
        self._add_location_rule([
            "RH: Spellblade's Pointed Hat - found on Rogier's body",
            "RH: Spellblade's Traveling Attire - found on Rogier's body",
            "RH: Spellblade's Gloves - found on Rogier's body",
            "RH: Spellblade's Trousers - found on Rogier's body",
            "RH: Rogier's Rapier - talk Rogier after beating SV mainboss or on his body after he dies"
        ], lambda state: ( self._can_go_to(state, "Stormveil Castle") and state.has("Cursemark of Death", self.player)))
        
        # MARK: Fia
        
        self._add_location_rule(["RH: Knifeprint Clue - talk to Fia multiple times", 
        ], lambda state: ( self._can_go_to(state, "Stormveil Castle")))
        
        self._add_location_rule(["RH: Sacrificial Twig - talk to Fia after giving Black Knifeprint to Rogier", 
        ], lambda state: ( state.has("Black Knifeprint", self.player) and self._can_go_to(state, "Stormveil Castle")))
        
        self._add_location_rule(["RH: Weathered Dagger - talk to Fia after reaching altus", 
        ], lambda state: ( self._can_go_to(state, "Altus Plateau")))
        
        self._add_location_rule([
            "RH: Twinned Helm - on D's body after giving him Weather Dagger during Fia's quest",
            "RH: Twinned Armor - on D's body after giving him Weather Dagger during Fia's quest",
            "RH: Twinned Gauntlets - on D's body after giving him Weather Dagger during Fia's quest",
            "RH: Twinned Greaves - on D's body after giving him Weather Dagger during Fia's quest"
        ], lambda state: ( state.has("Weathered Dagger", self.player) and self._can_go_to(state, "Altus Plateau")))
        
        self._add_location_rule([
            "DD/PDT: Remembrance of the Lichdragon - mainboss drop", 
            "DD/PDT: Mending Rune of the Death-Prince - on Fia after mainboss",
            "DD/PDT: Fia's Hood - kill Fia or after mainboss",
            "DD/PDT: Fia's Robe - kill Fia or after mainboss",
        ], lambda state: ( state.has("Cursemark of Death", self.player) and self._can_get(state, "RH: Weathered Dagger - talk to Fia after reaching altus")))
        
        # MARK: Dung Eater
        
        self._add_location_rule(["RH: Sewer-Gaol Key - talk to Dung Eater while having a Seedbed Curse", 
        ], lambda state: ( state.has("Seedbed Curse", self.player) and self._can_go_to(state, "Altus Plateau")))
        
        self._add_location_rule([ # boggart seedbed here
            "SSG/UR: Sword of Milos - kill Dung Eater or kill him during his invasion in CO",
            "CO/AHG: Seedbed Curse - on Boggart's body after becoming Dung Eater's victim",
        ], lambda state: ( self._can_go_to(state, "Capital Outskirts") and state.has("Sewer-Gaol Key", self.player)
            and self._can_get(state, "RH: Sewer-Gaol Key - talk to Dung Eater while having a Seedbed Curse")))
        
        self._add_location_rule(["SSG/UR: Mending Rune of the Fell Curse - give Dung Eater 5 seedbed curses", 
        ], lambda state: ( self._can_get(state, "SSG/UR: Sword of Milos - kill Dung Eater or kill him during his invasion in CO")
            and state.has("Seedbed Curse", self.player, 5)))
        
        self._add_location_rule([
            "SSG/UR: Omen Helm - kill Dung Eater or finish his quest",
            "SSG/UR: Omen Armor - kill Dung Eater or finish his quest",
            "SSG/UR: Omen Gauntlets - kill Dung Eater or finish his quest",
            "SSG/UR: Omen Greaves - kill Dung Eater or finish his quest"
        ], lambda state: ( self._can_get(state, "SSG/UR: Mending Rune of the Fell Curse - give Dung Eater 5 seedbed curses")))
  
        # MARK: Nepheli
        
        self._add_location_rule(["RH: Arsenal Charm - talk to Nepheli before and after defeating SV mainboss"
        ], lambda state: ( self._can_get(state, "SV/SeC: Remembrance of the Grafted - mainboss drop")))
        
        self._add_location_rule([
            "SV/GG: Ancient Dragon Smithing Stone - Gostoc shop after finishing Nepheli and Kenneth Haight's quests",
            "SV/GG: Ancient Dragon Smithing Stone - talk to Nepheli in SV after her and Kenneth's questlines",
            "SV/GG: Stormhawk Axe - kill Nepheli"
        ], lambda state: ( self._can_get(state, "LRC/QB: Morgott's Great Rune - mainboss drop")
                          and state.has("The Stormhawk King", self.player)))
        
        # MARK: Gideon
        
        self._add_location_rule([
            "RH: Fevor's Cookbook [3] - talk to Gideon after reaching MP",
            "RH: Law of Causality - talk to Gideon after beating MP mainboss"
        ], lambda state: self._can_go_to(state, "Mohgwyn Palace"))
        
        self._add_location_rule([
            "RH: Black Flame's Protection - talk to Gideon after reaching MH",
            "RH: Lord's Divine Fortification - talk to Gideon after beating EBH mainboss"
        ], lambda state: self._can_go_to(state, "Miquella's Haligtree"))
        
        # MARK: Gurraq
        
        self._add_location_rule([
            "DB/(BS): Clawmark Seal - Gurranq, deathroot reward 1",
            "DB/(BS): Beast Eye - Gurranq, deathroot reward 1 or kill Gurranq",
        ], "Deathroot")
        
        self._add_location_rule(["DB/(BS): Bestial Sling - Gurranq, deathroot reward 2",
        ], lambda state: ( state.has("Deathroot", self.player, 2)))
        
        self._add_location_rule(["DB/(BS): Bestial Vitality - Gurranq, deathroot reward 3",
        ], lambda state: ( state.has("Deathroot", self.player, 3)))
        
        self._add_location_rule(["DB/(BS): Ash of War: Beast's Roar - Gurranq, deathroot reward 4",
        ], lambda state: ( state.has("Deathroot", self.player, 4)))
        
        self._add_location_rule(["DB/(BS): Beast Claw - Gurranq, deathroot reward 5",
        ], lambda state: ( state.has("Deathroot", self.player, 5)))
        
        self._add_location_rule(["DB/(BS): Stone of Gurranq - Gurranq, deathroot reward 6",
        ], lambda state: ( state.has("Deathroot", self.player, 6)))
        
        self._add_location_rule(["DB/(BS): Beastclaw Greathammer - Gurranq, deathroot reward 7",
        ], lambda state: ( state.has("Deathroot", self.player, 7)))
        
        self._add_location_rule(["DB/(BS): Gurranq's Beast Claw - Gurranq, deathroot reward 8",
        ], lambda state: ( state.has("Deathroot", self.player, 8)))
        
        self._add_location_rule(["DB/(BS): Ancient Dragon Smithing Stone - Gurranq, deathroot reward 9 or kill Gurranq",
        ], lambda state: ( state.has("Deathroot", self.player, 9)))
        
        # MARK: Gowry
        
        self._add_location_rule([ 
            "CL/(GS): Sellia's Secret - talk to Gowry with needle",
            "CL/(GS): Unalloyed Gold Needle (Fixed) - talk to Gowry after giving needle",
        ], "Unalloyed Gold Needle (Broken)")
        
        self._add_location_rule([
            "CL/(GS): Glintstone Stars - Gowry Shop",
            "CL/(GS): Night Shard - Gowry Shop",
            "CL/(GS): Night Maiden's Mist - Gowry Shop",
        ], lambda state: ( self._can_get(state, "CL/(CP): Prosthesis-Wearer Heirloom - give Millicent fixed needle")))
        
        self._add_location_rule(["CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent",
        ], lambda state: ( state.has("Valkyrie's Prosthesis", self.player) and self._can_go_to(state, "Altus Plateau")
                          and self._can_get(state, "CL/(GS): Night Shard - Gowry Shop")))
        
        # self._add_location_rule(["CL/(GS): Desperate Prayer - buy 4th shop item", # gesture
        # ], lambda state: ( self._can_get(state, "CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent")))
        
        self._add_location_rule(["CL/(GS): Flock's Canvas Talisman - kill Gowry or complete questline",
        ], lambda state: ( self._can_get(state, "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area")))
        
        # MARK: Millicent
        
        self._add_location_rule(["CL/(CP): Prosthesis-Wearer Heirloom - give Millicent fixed needle",
        ], "Unalloyed Gold Needle (Fixed)")
        
        self._add_location_rule([
            "EBH/EIW: Rotten Winged Sword Insignia - help Millicent",
            "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area",
            "EBH/EIW: Millicent's Prosthesis - invade Millicent or kill in altus",
        ], lambda state: ( self._can_get(state, "CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent")))
        
        self._add_location_rule([
            "EBH/HR: Miquella's Needle - use needle on flower in boss arena after Millicent quest",
            "EBH/HR: Somber Ancient Dragon Smithing Stone - use needle on flower in boss arena after Millicent quest",
        ], lambda state: ( 
            self._can_get(state, "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area")
            and state.has("Unalloyed Gold Needle (Milicent)", self.player)
        ))
        
        # MARK: Ranni
        
        self._add_location_rule([
            "LG/(CE): Spirit Calling Bell - talk to Ranni",
            "LG/(CE): Lone Wolf Ashes - talk to Ranni",
        ], lambda state: ( self._can_go_to(state, "Liurnia of The Lakes")))
        # you can get in LL if missed i think
        
        self._add_location_rule([
            "NR/(NSG): Fingerslayer Blade - in chest lower area, talk to Ranni in LL",
            "NR/(NSG): Great Ghost Glovewort - in chest lower area, talk to Ranni in LL"
        ], lambda state: ( self._can_go_to(state, "Liurnia of The Lakes")))
        
        self._add_location_rule([
            "LL/(ReR): Snow Witch Hat - in chest, after giving Fingerslayer Blade to Ranni",
            "LL/(ReR): Snow Witch Robe - in chest, after giving Fingerslayer Blade to Ranni",
            "LL/(ReR): Snow Witch Skirt - in chest, after giving Fingerslayer Blade to Ranni",
            "LL/(RaR): Carian Inverted Statue - given by Ranni after giving Fingerslayer Blade",
            "ARM/ARM: Miniature Ranni - to N after giving Ranni Fingerslayer Blade"
        ], "Fingerslayer Blade")
        
        self._add_location_rule(["NS/NWB: Discarded Palace Key - invader drop to SE, need Miniature Ranni"
        ], lambda state: ( state.has("Miniature Ranni", self.player) 
            and self._can_get(state, "ARM/ARM: Miniature Ranni - to N after giving Ranni Fingerslayer Blade")))
        
        self._add_location_rule(["RLA/RLGL: Dark Moon Ring - in chest, requires Discarded Palace Key",
        ], "Discarded Palace Key")
        
        # MARK: Seluvis
        
        self._add_location_rule(["LL/(SR): Seluvis's Introduction - talk to Seluvis after talking to Blaidd in SR", 
        ], lambda state: (self._can_go_to(state, "Siofra River")))
        
        self._add_location_rule([
            "LL/(SR): Nepheli Loux Puppet - on Seluvis's body", 
            "LL/(SR): Dolores the Sleeping Arrow Puppet - Seluvis shop, after you give potion to Nepheli"
        ], lambda state: ( state.has("Seluvis's Potion", self.player)
            and self._can_get(state, "RH: Arsenal Charm - talk to Nepheli before and after defeating SV mainboss")))
        
        self._add_location_rule(["LL/(SR): Dung Eater Puppet - Seluvis shop, after you give potion to Dung Eater", 
        ], lambda state: ( state.has("Seluvis's Potion", self.player)
            and self._can_get(state, "SSG/UR: Sword of Milos - kill Dung Eater or kill him during his invasion in CO")))
        
        self._add_location_rule([
            "LL/(SR): Carian Phalanx - Seluvis shop after potion used",
            "LL/(SR): Glintstone Icecrag - Seluvis shop after potion used",
            "LL/(SR): Freezing Mist - Seluvis shop after potion used",
            "LL/(SR): Carian Retaliation - Seluvis shop after potion used"
        ], "Seluvis's Potion")
        
        # THIS BREAKS
        self._add_location_rule([
            "LL/(SR): Jarwight Puppet - Seluvis shop after finding puppet room",
            "LL/(SR): Finger Maiden Therolina Puppet - Seluvis shop after finding puppet room"
        ], lambda state: (state.has("Starlight Shards", self.player, 3)
            and state.has("Seluvis's Potion", self.player)))
        
        self._add_location_rule([
            "LL/(SR): Magic Scorpion Charm - given by Seluvis after giving Amber Starlight",
            "LL/(SR): Amber Draught - given by Seluvis after giving Amber Starlight"
        ], lambda state: (state.has("Amber Starlight", self.player) 
            and self._can_get(state, "LL/(SR): Jarwight Puppet - Seluvis shop after finding puppet room")))
        
        # Pidia
        
        self._add_location_rule(["LL/(CM): Dolores the Sleeping Arrow Puppet - dropped by Pidia after Seluvis dies"
        ], lambda state: (self._can_get(state, "ARM/ARM: Miniature Ranni - to N after giving Ranni Fingerslayer Blade")
            or state.has("Amber Draught", self.player)))
        
        # MARK: Blaidd / Iji
        
        self._add_location_rule([
            "LL/RaR: Royal Greatsword - kill angry Blaidd",
            "LL/RaR: Blaidd's Armor - kill angry Blaidd",
            "LL/RaR: Blaidd's Gauntlets - kill angry Blaidd",
            "LL/RaR: Blaidd's Greaves - kill angry Blaidd",
            "LL/RM: Iji's Mirrorhelm - kill Iji or after quest"
        ], lambda state: (self._can_get(state, "MA/(CMC): Dark Moon Greatsword - give Ranni Darkmoon Ring under CMC")))
        
        # MARK: Alexander
        
        self._add_location_rule([
            "LL/JB: Exalted Flesh x3 - given by Alexander after getting him unstuck with oil pots, just above JB"
        ], lambda state: ( self._can_get(state, "CL/(WD): Remembrance of the Starscourge - mainboss drop")))
        
        self._add_location_rule([
            "MtG/FL: Jar - talk to Alexander S of FL"
        ], lambda state: ( self._can_get(state, "LL/JB: Exalted Flesh x3 - given by Alexander after getting him unstuck with oil pots, just above JB")))
        
        self._add_location_rule([ # also requires fire giant dead
            "FA/DTL: Shard of Alexander - fight Alexander to SW",
            "FA/DTL: Alexander's Innards - fight Alexander to SW"
        ], lambda state: ( self._can_get(state, "MtG/FL: Jar - talk to Alexander S of FL")))
        
        # MARK: Jar-bairn
        
        self._add_location_rule([
            "LL/JB: Companion Jar - give Alexander's Innards, left after Jar Bairn leaves"
        ], lambda state: ( self._can_get(state, "FA/DTL: Alexander's Innards - fight Alexander to SW")
                          and state.has("Alexander's Innards", self.player)))
        
        # MARK: Diallos
        
        self._add_location_rule([ # need to talk to in LL and VM stuff
            "LL/JB: Hoslow's Petal Whip - on Diallos's body",
            "LL/JB: Diallos's Mask - on Diallos's body",
            "LL/JB: Numen's Rune - on Diallos's body"
        ], lambda state: ( self._can_get(state, "VM/AP: Rykard's Great Rune - mainboss drop")
                          and self._can_get(state, "CL/(WD): Remembrance of the Starscourge - mainboss drop")))
        
        # MARK: VOLCANO QUESTS
        
        # do you need the letters? 1 2 and red, probs not since ng+
        
        self._add_location_rule([ # request 1
            "LG/LC: Scaled Helm - invade Istvan SE of colo",
            "LG/LC: Scaled Armor - invade Istvan SE of colo",
            "LG/LC: Scaled Gauntlets - invade Istvan SE of colo",
            "LG/LC: Scaled Greaves - invade Istvan SE of colo",
        ], lambda state: ( self._can_get(state, "VM/VM: Letter from Volcano Manor (Istvan) - on the table in the drawing room")))
        
        self._add_location_rule([ # reward 1 + patches & bernahl
            "VM/VM: Magma Shot - Tanith reward request 1",
            "VM/VM: Letter from Volcano Manor (Rileigh) - on the table in the drawing room after request 1",
            "VM/VM: Letter to Patches - talk to Patches after request 1",
            "VM/VM: Ash of War: Eruption - Bernahl shop after request 1",
            "VM/VM: Ash of War: Assassin's Gambit - Bernahl shop after request 1"
        ], lambda state: ( self._can_get(state, "LG/LC: Scaled Helm - invade Istvan SE of colo")))
        
        self._add_location_rule([ # request 2
            "AP/OAT: Black-Key Bolt x20 - invade Rileigh",
            "AP/OAT: Crepus's Vial - invade Rileigh"
        ], lambda state: ( self._can_get(state, "VM/VM: Letter from Volcano Manor (Rileigh) - on the table in the drawing room after request 1")))
        
        self._add_location_rule([ # reward 2 + bernahl
            "VM/VM: Serpentbone Blade - Tanith reward request 2",
            "VM/VM: Letter to Bernahl - Bernahl after request 2",
            "VM/VM: Red Letter - on the table in the drawing room after request 2"
        ], lambda state: ( self._can_get(state, "AP/OAT: Crepus's Vial - invade Rileigh")))
    
        self._add_location_rule([ # request 3
            "MotG/SL: Hoslow's Petal Whip - invade Juno Hoslow",
            "MotG/SL: Hoslow's Helm - invade Juno Hoslow",
            "MotG/SL: Hoslow's Armor - invade Juno Hoslow",
            "MotG/SL: Hoslow's Gauntlets - invade Juno Hoslow",
            "MotG/SL: Hoslow's Greaves - invade Juno Hoslow"
        ], lambda state: ( self._can_get(state, "VM/VM: Red Letter - on the table in the drawing room after request 2")))
  
        self._add_location_rule([ # reward 3
            "VM/VM: Taker's Cameo - Tanith reward request 3"
        ], lambda state: ( self._can_get(state, "MotG/SL: Hoslow's Petal Whip - invade Juno Hoslow")))
    
        # MARK: Bernahl
        
        self._add_location_rule([ # bernahl request
            "LRC/FMFF: Raging Wolf Helm - invade Vargram",
            "LRC/FMFF: Raging Wolf Armor - invade Vargram",
            "LRC/FMFF: Raging Wolf Gauntlets - invade Vargram",
            "LRC/FMFF: Raging Wolf Greaves - invade Vargram"
        ], lambda state: ( self._can_get(state, "VM/VM: Letter to Bernahl - Bernahl after request 2")))
        
        self._add_location_rule([ "VM/VM: Gelmir's Fury - Bernahl reward" # bernahl reward
        ], lambda state: ( self._can_get(state, "LRC/FMFF: Raging Wolf Helm - invade Vargram")))
        
        self._add_location_rule([
            "LG/(WS): Beast Champion Helm - kill Bernahl",
            "LG/(WS): Beast Champion Gauntlets - kill Bernahl",
            "LG/(WS): Beast Champion Greaves - kill Bernahl",
            "LG/(WS): Beast Champion Armor (Altered) - kill Bernahl"
        ], lambda state: self._can_get(state, "FA/BGB: Blasphemous Claw - kill invader Bernahl, to NE end of path"))
        
        # MARK: Rya 
               
        self._add_location_rule(["LL/SeI: Volcano Manor Invitation - give Rya her necklace, you will need to buy the item from Boggart or reach altus", 
        ], lambda state: ( self._can_go_to(state, "Altus Plateau") or state.has("Rya's Necklace", self.player)))
   
        self._add_location_rule([
            "VM/VM: Zorayas's Letter - end of Rya's quest, dont kill or give potion", 
            "VM/VM: Daedicar's Woe - end of Rya's quest, any option"
        ], lambda state: ( self._can_get(state, "VM/VM: Tonic of Forgetfulness - given by Tanith after you give Rya Serpent's Amnion")
            and self._can_get(state, "VM/AP: Rykard's Great Rune - mainboss drop")))
        
        # MARK: Patches 
        
        self._add_location_rule([ # patches request
            "RSP/RSPO: Bull-Goat Helm - invade Tragoth",
            "RSP/RSPO: Bull-Goat Armor - invade Tragoth",
            "RSP/RSPO: Bull-Goat Gauntlets - invade Tragoth",
            "RSP/RSPO: Bull-Goat Greaves - invade Tragoth"
        ], lambda state: ( self._can_get(state, "VM/VM: Letter to Patches - talk to Patches after request 1")))
        
        self._add_location_rule(["VM/VM: Magma Whip Candlestick - Patches reward", # patches reward
        ], lambda state: ( self._can_get(state, "RSP/RSPO: Bull-Goat Helm - invade Tragoth")))
        
        self._add_location_rule(["TSC/CI: Dancer's Castanets - given by Patches just outside boss arena",
        ], lambda state: ( self._can_get(state, "VM/AP: Rykard's Great Rune - mainboss drop")
            and self._can_get(state, "VM/VM: Magma Whip Candlestick - Patches reward")))
        
        self._add_location_rule(["LG/(MCV): Glass Shard x3 - Patches chest, after you've given the Dancer's Castanets to Tanith",
        ], lambda state: ( self._can_get(state, "VM/RLB: Aspects of the Crucible: Breath - enemy drop, spawns after Tanith's death")))
        
        self._add_location_rule([
            "LG/(MCV): Spear - kill Patches",
            "LG/(MCV): Leather Armor - kill Patches",
            "LG/(MCV): Leather Gloves - kill Patches",
            "LG/(MCV): Leather Boots - kill Patches"
        ], lambda state: ( self._can_get(state, "LG/(MCV): Glass Shard x3 - Patches chest, after you've given the Dancer's Castanets to Tanith")))

        # MARK: Tanith
        
        self._add_location_rule([ # or after rykard is dead
            "VM/VM: Tonic of Forgetfulness - given by Tanith after you give Rya Serpent's Amnion",
        ], lambda state: ( state.has("Serpent's Amnion", self.player) 
            and self._can_get(state, "LG/LC: Scaled Helm - invade Istvan SE of colo")))
   
        self._add_location_rule([
            "VM/RLB: Consort's Mask - kill Tanith",
            "VM/RLB: Consort's Robe - kill Tanith",
            "VM/RLB: Consort's Trousers - kill Tanith",
            "VM/RLB: Aspects of the Crucible: Breath - enemy drop, spawns after Tanith's death"
        ], lambda state: ( self._can_get(state, "VM/AP: Rykard's Great Rune - mainboss drop") and state.has("Dancer's Castanets", self.player)))
        
        # MARK: DLC NPC
        
        if self.options.enable_dlc: 
            
            # MARK: Grandam
            
            self._add_location_rule([
                "BTS/SPA: Watchful Spirit - given by Hornsent Grandam while wearing the Divine Beast Head",
                "BTS/SPA: Scorpion Stew - given by Hornsent Grandam while wearing the Divine Beast Head a second time after reloading"
            ], lambda state: state.has("Storeroom Key", self.player) and state.has("Divine Beast Head", self.player))
            
            self._add_location_rule([
                "BTS/SPA: Gourmet Scorpion Stew - given by Hornsent Grandam after defeating SK mainboss",
                "BTS/SPA: Gourmet Scorpion Stew - on Hornsent Grandam after defeating SK mainboss, exhausting her dialogue, and reloading"
            ], lambda state: self._can_get(state, "BTS/SPA: Watchful Spirit - given by Hornsent Grandam while wearing the Divine Beast Head") 
                and self._can_get(state, "SK/DCE: Remembrance of the Impaler - mainboss drop"))
            
            # MARK: Florissax
            
            self._add_location_rule([
                "JP/GADC: Ancient Dragon Florissax - admit to putting Florissax to sleep with Thiollier's Concoction",
                "JP/GADC: Dragonbolt of Florissax - given by Florissax if you gave her Thiollier's Concoction before JP mainboss"
                ], "Thiollier's Concoction")
            
            # MARK: Igon
            
            self._add_location_rule([
                "JP/FJP: Igon's Greatbow - to E on Igon's corpse after JP mainboss",
                "JP/FJP: Igon's Helm - to E on Igon's corpse after JP mainboss",
                "JP/FJP: Igon's Armor - to E on Igon's corpse after JP mainboss",
                "JP/FJP: Igon's Gauntlets - to E on Igon's corpse after JP mainboss",
                "JP/FJP: Igon's Loincloth - to E on Igon's corpse after JP mainboss"
            ], "Igon's Furled Finger")
            
            # MARK: Queelign
            
            # his drops will always be one then the second no matter the region order, so require both
            self._add_location_rule([
                "SA/(CC): Prayer Room Key - invader drop",
                "SA/(CC): Ash of War: Flame Skewer - invader drop",
                "BTS/SPA: Crusade Insignia - invader drop in NE courtyard"
            ], lambda state: self._can_go_to(state, "Scadu Altus") and self._can_go_to(state, "Belurat"))
            
            self._add_location_rule(["SK/CDE: Fire Knight Queelign - on Queelign, give Iris of Grace, in room with door"
            ], lambda state: self._can_get(state, "SA/(CC): Prayer Room Key - invader drop")
                and state.has("Prayer Room Key", self.player) and state.has("Iris of Grace", self.player))
            
            self._add_location_rule(["SK/CDE: Queelign's Greatsword - on Queelign, give Iris of Occultation, in room with door"
            ], lambda state: self._can_get(state, "SA/(CC): Prayer Room Key - invader drop")
                and state.has("Prayer Room Key", self.player) and state.has("Iris of Occultation", self.player))
            
            # MARK: Leda
            
            self._add_location_rule([
                "SA/HC: Lacerating Crossed-Tree - given by Leda after invading Hornsent alongside her",
                "SA/HC: Retaliatory Crossed-Tree - given by Leda after invading Ansbach alongside her"
                ], lambda state: self._can_go_to(state, "Shadow Keep"))
            
            # MARK: Freyja
            
            self._add_location_rule("SK/SSF: Golden Lion Shield - given by Freyja after giving her Letter for Freyja", "Letter for Freyja")
            
            # MARK: Ansbach
            
            self._add_location_rule("SK/SFiF: Letter for Freyja - given by Ansbach after giving Secret Rite Scroll", "Secret Rite Scroll")
            
            # MARK: Thiollier
            
            self._add_location_rule("GP/PPC: Thiollier's Concoction - sold by Thiollier after given Black Syrup", "Black Syrup")
            
            self._add_location_rule([
                "EI/GD: Thiollier's Hidden Needle - on Thiollier's body to NW",
                "EI/GD: Thiollier's Mask - on Thiollier's body to NW",
                "EI/GD: Thiollier's Garb - on Thiollier's body to NW",
                "EI/GD: Thiollier's Gloves - on Thiollier's body to NW",
                "EI/GD: Thiollier's Trousers - on Thiollier's body to NW"
                ], lambda state: self._can_get(state, "SCF/GDP: St. Trina's Smile - Thiollier invader drop, after you die to St. Trina four times and tell him your findings"))
            
            self._add_location_rule("SCF/GDP: St. Trina's Blossom - on St. Trina's body after EI mainboss",
                lambda state: self._can_get(state, "EI/DGFS: Remembrance of a God and a Lord - mainboss drop"))
            
            # MARK: Moore
            
            self._add_location_rule([ # tell him to be sad, body in SA by CC
                "GP/MGC: Verdigris Greatshield - on Moore's body",
                "GP/MGC: Verdigris Helm - on Moore's body",
                "GP/MGC: Verdigris Armor - on Moore's body",
                "GP/MGC: Verdigris Gauntlets - on Moore's body",
                "GP/MGC: Verdigris Greaves - on Moore's body"
                ], lambda state: self._can_go_to(state, "Scadu Altus"))
            
            # friendly Kindred of Rot locations
            # "GP/PT: Forager Brood Cookbook [2] - given by friendly Kindred of Rot E of PT"
            # "GP/PT: Black Pyrefly x3 - given by friendly Kindred of Rot E of PT"
            
            # "ER/ERD: Forager Brood Cookbook [3] - given by friendly Kindred of Rot to SE, NE corner of cliffs"
            # "ER/ERD: Yellow Fulgurbloom x3 - given by friendly Kindred of Rot to SE, NE corner of cliffs"

            self._add_location_rule([
                "SA/CC: Forager Brood Cookbook [4] - N of CC, given by friendly Kindred of Rot after you heal it",
                "SA/CC: Shadow Sunflower x3 - N of CC, given by friendly Kindred of Rot after you heal it"
                ], lambda state: state.has("Crafting Kit", self.player) 
                    and (state.has("Nomadic Warrior's Cookbook [19]", self.player) or state.has("Battlefield Priest's Cookbook [4]", self.player)))
            
            # "SA/RFSP: Forager Brood Cookbook [1] - given by friendly Kindred of Rot NW of RFSP"
            # "SA/RFSP: Glintslab Firefly x3 - given by friendly Kindred of Rot NW of RFSP"
            
            # "SA/MR: Forager Brood Cookbook [5] - given by friendly Kindred of Rot, to NE, through cave, on NE ledge"
            # "SA/MR: Pearlescent Scale - given by friendly Kindred of Rot, to NE, through cave, on NE ledge"
            
            # "SA/CDH: Forager Brood Cookbook [6] - given by friendly Kindred of Rot to NW above entrance to SKCD, in W corner"
            # "SA/CDH: Dewgem x3 - given by friendly Kindred of Rot to NW above entrance to SKCD, in W corner"
            
            # MARK: Hornsent
            
            self._add_location_rule("GP/TPC: Furnace Visage x3 - given by Hornsent after giving Scorpion Stew", "Scorpion Stew")
            
            
            # MARK: Dane
            
            self._add_location_rule([
                "SA/MR: Dane's Hat - challenge Dane with May the Best Win",
                "SA/MR: Dryleaf Arts - challenge Dane with May the Best Win"
            ], "May the Best Win")
            
            # MARK: Ymir
            
            self._add_location_rule("FRR: Crimson Seed Talisman +1 - use Hole-Laden Necklace at the hanging bell in the center", "Hole-Laden Necklace")
            
            self._add_location_rule([
                "SA/(CMM): Glintstone Nail - Ymir shop after ringing one of the hanging bells",
                "SA/(CMM): Glintstone Nails - Ymir shop after ringing one of the hanging bells",
                "SA/(CMM): Beloved Stardust - given by Ymir after ringing the hanging bell in FRR",
                "SA/(CMM): Ruins Map (2nd) - given by Ymir after ringing the hanging bell in FRR",
                "FRD: Cerulean Seed Talisman +1 - use Hole-Laden Necklace at the hanging bell in the center"
            ], lambda state: self._can_get(state, "FRR: Crimson Seed Talisman +1 - use Hole-Laden Necklace at the hanging bell in the center"))
            
            self._add_location_rule([
                "SA/(CMM): Fleeting Microcosm - Ymir shop after ringing both hanging bells",
                "SA/(CMM): Ruins Map (3rd) - given by Ymir after ringing both hanging bells"
            ], lambda state: self._can_get(state, "FRD: Cerulean Seed Talisman +1 - use Hole-Laden Necklace at the hanging bell in the center"))
            
            self._add_location_rule([
                "SA/CMM: Cherishing Fingers - in graveyard W of CMM after Ymir dead"
            ], lambda state: self._can_get(state, "SA/(CMM): Maternal Staff - kill invader Ymir"))
            
            # MARK: Jolán
            
            self._add_location_rule([
                "SA/(CMM): Swordhand of Night Jolán - on Jolán after killing Ymir, give Iris of Grace"                
            ], lambda state: state.has("Iris of Grace", self.player) and 
                self._can_get(state, "SA/(CMM): Maternal Staff - kill invader Ymir"))
            
            self._add_location_rule([
                "SA/(CMM): Sword of Night - on Jolán after killing Ymir, give Iris of Occultation"
            ], lambda state: state.has("Iris of Occultation", self.player) and 
                self._can_get(state, "SA/(CMM): Maternal Staff - kill invader Ymir"))
            
    def _add_remembrance_rules(self) -> None:
        """Adds rules for items obtainable for trading remembrances."""

        remembrances = [
            (
                "Remembrance of the Grafted",
                ["Axe of Godrick", "Grafted Dragon"]
            ),
            (
                "Remembrance of the Full Moon Queen",
                ["Carian Regal Scepter", "Rennala's Full Moon"]
            ),
            (
                "Remembrance of the Starscourge",
                ["Starscourge Greatsword", "Lion Greatbow"]
            ),
            (
                "Remembrance of the Regal Ancestor",
                ["Winged Greathorn", "Ancestral Spirit's Horn"]
            ),
            (
                "Remembrance of the Omen King",
                ["Morgott's Cursed Sword", "Regal Omen Bairn"]
            ),
            (
                "Remembrance of the Naturalborn",
                ["Ash of War: Waves of Darkness", "Bastard's Stars"]
            ),
            (
                "Remembrance of the Blasphemous",
                ["Rykard's Rancor", "Blasphemous Blade"]
            ),
            (
                "Remembrance of the Lichdragon",
                ["Fortissax's Lightning Spear", "Death Lightning"]
            ),
            (
                "Remembrance of the Fire Giant",
                ["Giant's Red Braid", "Burn, O Flame!"]
            ),
            (
                "Remembrance of the Blood Lord",
                ["Mohgwyn's Sacred Spear", "Bloodboon"]
            ),
            (
                "Remembrance of the Black Blade",
                ["Maliketh's Black Blade", "Black Blade"]
            ),
            (
                "Remembrance of the Dragonlord",
                ["Dragon King's Cragblade", "Placidusax's Ruin"]
            ),
            (
                "Remembrance of Hoarah Loux",
                ["Axe of Godfrey", "Ash of War: Hoarah Loux's Earthshaker"]
            ),
            (
                "Remembrance of the Rot Goddess",
                ["Hand of Malenia", "Scarlet Aeonia"]
            ),
            (
                "Elden Remembrance",
                ["Marika's Hammer", "Sacred Relic Sword"]
            ),
        ]

        dlc_remembrances = [
            (
                "Remembrance of the Dancing Lion",
                ["Enraged Divine Beast", "Ash of War: Divine Beast Frost Stomp"]
            ),
            (
                "Remembrance of the Twin Moon Knight",
                ["Rellana's Twin Blades", "Rellana's Twin Moons"]
            ),
            (
                "Remembrance of Putrescence",
                ["Putrescence Cleaver", "Vortex of Putrescence"]
            ),
            (
                "Remembrance of the Wild Boar Rider",
                ["Sword Lance", "Blades of Stone"]
            ),
            (
                "Remembrance of the Shadow Sunflower",
                ["Shadow Sunflower Blossom", "Land of Shadow"]
            ),
            (
                "Remembrance of the Impaler",
                ["Spear of the Impaler", "Messmer's Orb"]
            ),
            (
                "Remembrance of the Saint of the Bud",
                ["Poleblade of the Bud", "Rotten Butterflies"]
            ),
            (
                "Remembrance of the Mother of Fingers",
                ["Staff of the Great Beyond", "Gazing Finger"]
            ),
            (
                "Remembrance of the Lord of Frenzied Flame",
                ["Greatsword of Damnation", "Midra's Flame of Frenzy"]
            ),
            (
                "Remembrance of a God and a Lord",
                ["Greatsword of Radahn (Lord)", "Greatsword of Radahn (Light)", "Light of Miquella"]
            ),
        ]
            
        if self.options.enable_dlc:
            remembrances += dlc_remembrances
            self._add_location_rule("JP/GADC: Bayle's Flame Lightning - Dragon Communion, Heart of Bayle",
                lambda state: (state.has("Heart of Bayle", self.player) and self._can_go_to(state, "Jagged Peak Foot")))
            self._add_location_rule("JP/GADC: Bayle's Tyranny - Dragon Communion, Heart of Bayle", 
                lambda state: (state.has("Heart of Bayle", self.player) and self._can_go_to(state, "Jagged Peak Foot")))

        for (remembrance, rem_items) in remembrances:
            self._add_location_rule([
                f"RH: {item} - Enia for {remembrance}" for item in rem_items
            ], lambda state, item=remembrance: (state.has(item, self.player) and self._has_enough_great_runes(state, 1)))
    
    def _add_equipment_of_champions_rules(self) -> None:
        """Adds rules for items obtainable from equipment of champions."""

        equipments = [ # done
            ( # RA mainboss
                "RLA mainboss", #"Rennala, Queen of the Full Moon", # boss
                "RLA: Remembrance of the Full Moon Queen - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Queen's Crescent Crown", 
                    "Queen's Robe",
                    "Queen's Leggings", 
                    "Queen's Bracelets"
                ]
            ),
            ( # MH mainboss
                "EBH/HR mainboss", #"Malenia Blade of Miquella", # boss
                "EBH/HR: Remembrance of the Rot Goddess - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Malenia's Winged Helm", 
                    "Malenia's Armor",
                    "Malenia's Gauntlet", 
                    "Malenia's Greaves"
                ]
            ),
            ( # LAC mainboss
                "LAC/QB mainboss", #"Godfrey, First Elden Lord", # boss
                "LAC/QB: Remembrance of Hoarah Loux - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Elden Lord Crown", 
                    "Elden Lord Armor",
                    "Elden Lord Bracers", 
                    "Elden Lord Greaves"
                ]
            ),
            ( # TSC boss
                "TSC/SCIG boss", #"Elemer of the Briar", # boss
                "TSC/SCIG: Briar Greatshield - boss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Briar Helm", 
                    "Briar Armor",
                    "Briar Gauntlets", 
                    "Briar Greaves"
                ]
            ),
            ( # MH boss
                "MH/HTP boss", #"Loretta, Knight of the Haligtree", # boss
                "MH/HTP: Loretta's Mastery - boss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Royal Knight Helm", 
                    "Royal Knight Armor",
                    "Royal Knight Gauntlets", 
                    "Royal Knight Greaves"
                ]
            ),
            ( # FA mainboss
                "FA/BGB mainboss", #"Maliketh, the Black Blade", # boss
                "FA/BGB: Remembrance of the Black Blade - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Maliketh's Helm", 
                    "Maliketh's Armor",
                    "Maliketh's Gauntlets", 
                    "Maliketh's Greaves"
                ]
            ),
            ( # MotG/(CS) mainboss
                "MotG/(CS) mainboss", #"Commander Niall", # boss
                "MotG/(CS): Veteran's Prosthesis - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Veteran's Helm", 
                    "Veteran's Armor",
                    "Veteran's Gauntlets", 
                    "Veteran's Greaves"
                ]
            ),
            ( # WD mainboss
                "CL/(WD) mainboss", #"Starscourge Radahn", # boss
                "CL/(WD): Remembrance of the Starscourge - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Radahn's Redmane Helm", 
                    "Radahn's Lion Armor",
                    "Radahn's Gauntlets", 
                    "Radahn's Greaves"
                ]
            ),
            ( # LRC mainboss
                "LRC/QB mainboss", #"Morgott, The Omen King", # boss
                "LRC/QB: Remembrance of the Omen King - mainboss drop", # a drop from boss, so we can do 'can get' check
                ["Fell Omen Cloak"]# item
            ),
            ( # MP mainboss
                "MP/(MDM) mainboss", # "Mohg, Lord of Blood", # boss
                "MP/(MDM): Remembrance of the Blood Lord - mainboss drop", # a drop from boss, so we can do 'can get' check
                ["Lord of Blood's Robe"]# item
            ),
        ]

        dlc_equipments = [ # done
            (
                "SK/DCE mainboss", #"Messmer the Impaler", # boss
                "SK/DCE: Remembrance of the Impaler - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Messmer's Helm", 
                    "Messmer's Armor",
                    "Messmer's Gauntlets", 
                    "Messmer's Greaves"
                ]
            ),
            (
                "CE/CLC mainboss", #"Rellana, Twin Moon Knight", # boss
                "CE/CLC: Remembrance of the Twin Moon Knight - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Rellana's Helm", 
                    "Rellana's Armor",
                    "Rellana's Gloves", 
                    "Rellana's Greaves"
                ]
            ),
            (
                "SV/SKBG mainboss", #"Commander Gaius", # boss
                "SV/SKBG: Remembrance of the Wild Boar Rider - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Gaius's Helm", 
                    "Gaius's Armor",
                    "Gaius's Gauntlets"
                ]
            ),
            ( # you cant even get this till the game is beat LMAO, but you can get it in all bosses :)
                "EI/DGFS mainboss", #"Promised Consort Radahn", # boss
                "EI/DGFS: Remembrance of a God and a Lord - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Young Lion's Helm", 
                    "Young Lion's Armor",
                    "Young Lion's Gauntlets", 
                    "Young Lion's Greaves"
                ]
            ),
        ]
            
        if self.options.enable_dlc:
            equipments += dlc_equipments

        for (boss, boss_location, eq_items) in equipments:
            self._add_location_rule([
                f"RH: {item} - Enia shop, defeat {boss}" for item in eq_items
            ], lambda state, bl=boss_location: (self._can_get(state, bl) and self._has_enough_great_runes(state, 1)))
            
    def _add_allow_useful_location_rules(self) -> None:
        """Adds rules for locations that can contain useful but not necessary items.

        If we allow useful items in the excluded locations, we don't want Archipelago's fill
        algorithm to consider them excluded because it never allows useful items there. Instead, we
        manually add item rules to exclude important items.
        """

        all_locations = self._get_our_locations()

        allow_useful_locations = (
            (
                {
                    location.name
                    for location in all_locations
                    if location.name in self.all_excluded_locations
                    and not location.data.missable
                }
                if self.options.excluded_location_behavior < self.options.missable_location_behavior
                else self.all_excluded_locations
            )
            if self.options.excluded_location_behavior == "allow_useful"
            else set()
        ).union(
            {
                location.name
                for location in all_locations
                if location.data.missable
                and not (
                    location.name in self.all_excluded_locations
                    and self.options.missable_location_behavior <
                        self.options.excluded_location_behavior
                )
            }
            if self.options.missable_location_behavior == "allow_useful"
            else set()
        )
        for location in allow_useful_locations:
            self._add_item_rule(
                location,
                lambda item: not item.advancement
            )

        # Prevent the player from prioritizing and "excluding" the same location
        self.options.priority_locations.value -= allow_useful_locations

        if self.options.excluded_location_behavior == "allow_useful":
            self.options.exclude_locations.value.clear()
            
    def _content_in_scope(self, data) -> bool:
        """Whether a location's content belongs in the check pool.

        dlc_only inverts the normal rule: keep ONLY dlc-flagged locations (base game is
        kept for traversal but holds no checks). Otherwise: base always, DLC iff enable_dlc.
        """
        if self.options.dlc_only:
            # Re-include the Twin Maiden Husks (Roundtable Hold) base-game shop
            # slots as randomized checks under dlc_only. The Roundtable vendor is
            # always reachable (base map is free-transit in dlc_only), so these 21
            # shop checks fill cleanly and stay count-neutral (each re-adds its
            # vanilla item to the pool). patch_apworld_twin_maiden_dlc_only_20260622.
            if "Twin maiden shop" in data.name:
                return True
            return bool(data.dlc)
        return (not data.dlc) or bool(self.options.enable_dlc)

    def _add_location_rule(self, location: Union[str, List[str]], rule: Union[CollectionRule, str]) -> None:
        """Sets a rule for the given location if it that location is randomized.

        The rule can just be a single item/event name as well as an explicit rule lambda.
        """
        locations = location if isinstance(location, list) else [location]
        for location in locations:
            data = location_dictionary[location]
            if not self._content_in_scope(data): continue

            if not self._is_location_available(location): continue
            # [key-gates] while collecting key/heart/imbued gates, mark the gated location EXCLUDED
            # (filler-only) instead of gating it on the now-dropped key requirement.
            if getattr(self, "_collecting_key_gates", False):
                self.multiworld.get_location(location, self.player).progress_type = LocationProgressType.EXCLUDED
            if isinstance(rule, str):
                assert (self.item_table[rule].classification == ItemClassification.progression
                        or rule in getattr(self, "_fun_demoted", ())), \
                    f"non-progression item '{rule}' used as a location-gate shorthand"
                rule = lambda state, item=rule: state.has(item, self.player)
            add_rule(self.multiworld.get_location(location, self.player), rule)
    
    def _exclude_region(self, region: str) -> None:
        """[key-gates] Flag every randomized check in `region` EXCLUDED (filler-only). Used when the
        region's entrance was gated by a key/heart/imbued requirement we're dropping."""
        if region not in self.created_regions:
            return
        for loc in self.multiworld.get_region(region, self.player).locations:
            if loc.address is not None:
                loc.progress_type = LocationProgressType.EXCLUDED

    def _add_entrance_rule(self, region: str, rule: Union[CollectionRule, str]) -> None:
        """Sets a rule for the entrance to the given region."""
        assert region in location_tables
        if region not in self.created_regions: return
        # [key-gates] a key/heart/imbued-gated entrance -> the whole region behind it is filler-only.
        if getattr(self, "_collecting_key_gates", False):
            self._exclude_region(region)
        if isinstance(rule, str):
            if " -> " not in rule:
                assert (self.item_table[rule].classification == ItemClassification.progression
                        or rule in getattr(self, "_fun_demoted", ())), \
                    f"non-progression item '{rule}' used as an entrance-gate shorthand"
            rule = lambda state, item=rule: state.has(item, self.player)
        add_rule(self.multiworld.get_entrance("Go To " + region, self.player), rule)

    def _add_item_rule(self, location: str, rule: ItemRule) -> None:
        """Sets a rule for what items are allowed in a given location."""
        if not self._is_location_available(location): return
        add_item_rule(self.multiworld.get_location(location, self.player), rule)

    def _can_go_to(self, state: CollectionState, region) -> bool:
        """Returns whether state can access the given region name."""
        # cango-warp-aware FIX: under region_access=warp a region is reached by its own
        # 'Warp To <region>' lock, so its geographic 'Go To <region>' entrance can be dead when
        # a predecessor region is num_regions-sealed (e.g. Liurnia sealed -> 'Go To Altus Plateau'
        # unreachable -> Wailing Dunes/Radahn falsely unreachable, even though Altus is warp-
        # reachable). Region-reachability matches the docstring + the indirect conditions (which
        # are registered on regions, not the 'Go To' entrance). Sound in-game: the Radahn festival
        # arms on reaching Altus (grace/map flag), which a warp into Altus satisfies.
        if state.can_reach_entrance(f"Go To {region}", self.player):
            return True
        if self.options.region_access == "warp":
            return state.can_reach_region(region, self.player)
        return False
