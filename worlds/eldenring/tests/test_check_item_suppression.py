"""Contract pins for the two runtime GRANT/SUPPRESS features that travel in slot_data:
vanilla-pickup SUPPRESSION (checkItemIds / checkItemFlags) and item GRANT (apIdsToItemIds).

Both are "arm loudly or fail loudly" features (CONTRIBUTING.md): if their slot_data table is
silently empty the client's consumer goes INERT (detour.rs logs "vanilla suppressor INERT" /
the grant map is empty) and the seed plays like vanilla with NO error. That exact regression
happened once already -- a refactor deleted __init__.py's [p2-check-items] block, dropping
checkItemFlags entirely and silently disarming the suppressor. These tests FAIL LOUDLY in CI the
moment either table goes missing/empty, on the same region_lock + enable_dlc:false config that
surfaced the bug.

Run (Windows): python worlds/eldenring/tests/run_tests.py check_item_suppression
"""
from test.bases import WorldTestBase


class _SlotDataBase(WorldTestBase):
    game = "EldenRing"
    auto_construct = True

    def _sd(self):
        return self.world.fill_slot_data()


class CheckItemSuppressionArmed(_SlotDataBase):
    """region_lock + enable_dlc:false -- the config LocalItemsOff / the spine-surgery playtest use."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "num_regions": 0}

    def test_suppression_table_armed(self):
        sd = self._sd()
        ids = sd.get("checkItemIds")
        flags = sd.get("checkItemFlags")
        # Both keys must EXIST (missing => regression) and be non-empty: an empty table disarms
        # the client vanilla-suppressor (detour.rs "INERT"), so every check hands out its vanilla
        # item on top of the AP item -- silent, seed-breaking. The FLOOR is a "block was dropped"
        # tripwire, not a coverage spec: checkItemIds counts DISTINCT vanilla item FullIDs across
        # filled locations, so it's modest -- 90 observed on region_lock + enable_dlc:false
        # (2026-07-03); DLC-on seeds run higher. 40 sits well above "dropped to ~0" and below the
        # real baseline.
        self.assertIsInstance(ids, list, "checkItemIds missing/not a list")
        self.assertIsInstance(flags, dict, "checkItemFlags missing/not a dict")
        self.assertGreater(len(ids), 40,
                           f"checkItemIds nearly empty ({len(ids)}, baseline ~90 for this config) "
                           f"-- vanilla-suppress likely disarmed (the [p2-check-items] slot_data "
                           f"block was dropped again)")
        self.assertTrue(flags, "checkItemFlags empty -- vanilla suppressor would go INERT")

    def test_suppression_table_wellformed(self):
        sd = self._sd()
        ids = set(sd.get("checkItemIds") or [])
        flags = sd.get("checkItemFlags") or {}
        for k, v in flags.items():
            self.assertTrue(str(k).lstrip("-").isdigit(), f"checkItemFlags key not an int str: {k!r}")
            self.assertIsInstance(v, list, f"checkItemFlags[{k}] not a list")
            self.assertTrue(v, f"checkItemFlags[{k}] empty flag list")
            self.assertTrue(all(isinstance(f, int) for f in v), f"checkItemFlags[{k}] non-int flag")
            # Every flagged item id must also be in checkItemIds (they are built together).
            self.assertIn(int(k), ids, f"checkItemFlags id {k} absent from checkItemIds")

    def test_item_grant_map_armed(self):
        # Item GRANT path: the client grants received AP items via apIdsToItemIds. Empty => no
        # grants land (the received-item path is the SINGLE grant path in core.rs). Pin it here
        # too so a churn that guts item emission fails loudly on the suppression suite as well.
        sd = self._sd()
        grant = sd.get("apIdsToItemIds")
        self.assertIsInstance(grant, dict, "apIdsToItemIds missing/not a dict")
        self.assertGreater(len(grant), 100,
                           f"apIdsToItemIds nearly empty ({len(grant) if grant else 0}) -- "
                           f"item-grant path disarmed")
