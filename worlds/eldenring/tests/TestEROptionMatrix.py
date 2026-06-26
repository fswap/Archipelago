from test.bases import WorldTestBase


# P4 of SPEC-test-coverage.md. Each class with an `options` dict makes WorldTestBase generate a full
# multiworld for that config in setUp and run the inherited reachability/fill checks -- i.e. it
# asserts the shipping option combinations produce a beatable seed. Run with the rest of the ER
# apworld suite:  python -m pytest worlds/eldenring/tests/   (Windows / Python 3.11+).


class ERBaseGameRegionLock(WorldTestBase):
    """Base-game (DLC off), region_lock, enemy rando -- the base path exposed to the #7 loop."""
    game = "EldenRing"
    options = {
        "enable_dlc": False,
        "world_logic": "region_lock",
        "enemy_rando": True,
        "ending_condition": "elden_beast",
    }


class ERDLCRegionLock(WorldTestBase):
    """DLC on, region_lock, enemy rando -- the validated sync config."""
    game = "EldenRing"
    options = {
        "enable_dlc": True,
        "world_logic": "region_lock",
        "enemy_rando": True,
        "ending_condition": "elden_beast",
    }


class ERBaseGameOpenWorld(WorldTestBase):
    """Base-game, open_world logic -- exercises the non-region-locked graph."""
    game = "EldenRing"
    options = {
        "enable_dlc": False,
        "world_logic": "open_world",
        "enemy_rando": False,
    }


class ERSlotDataContract(WorldTestBase):
    """Asserts the slot_data wire contract the static randomizer (bake) and runtime client
    (connect) both depend on. swap/runes toggles set true here to prove the apworld suppresses
    them under DLC."""
    game = "EldenRing"
    options = {
        "enable_dlc": True,
        "world_logic": "region_lock",
        "swap_multiboss": True,
        "boss_runes_match": True,
    }

    def test_required_keys_and_versions(self):
        sd = self.world.fill_slot_data()
        for key in ("options", "seed", "slot", "apIdsToItemIds", "itemCounts",
                    "locationIdsToKeys", "versions"):
            self.assertIn(key, sd)
        # Lockstep contract range, checked by BOTH the randomizer at bake and the client at connect.
        self.assertEqual(sd["versions"], ">=0.1.0-beta.3 <0.1.0-beta.4")

    def test_id_maps_are_parseable(self):
        sd = self.world.fill_slot_data()
        # apIdsToItemIds: stringified-int keys -> int values (randomizer: long.Parse + (int)(uint)).
        self.assertGreater(len(sd["apIdsToItemIds"]), 0)
        for k, v in sd["apIdsToItemIds"].items():
            int(k)                              # key must parse as an integer
            self.assertIsInstance(v, int)
        # locationIdsToKeys: stringified-int keys -> scope-key strings.
        for k, v in sd["locationIdsToKeys"].items():
            int(k)
            self.assertIsInstance(v, str)

    def test_enemy_swap_toggles_suppressed_under_dlc(self):
        # swap_multiboss / boss_runes_match crash vs DLC enemies, so fill_slot_data must force them
        # false whenever enable_dlc is on -- even though this yaml set them true.
        sd = self.world.fill_slot_data()
        self.assertFalse(sd["options"]["swap_multiboss"])
        self.assertFalse(sd["options"]["boss_runes_match"])
