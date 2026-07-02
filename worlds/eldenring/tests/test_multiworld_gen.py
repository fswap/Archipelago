"""Multiworld generation regression tests: the suite never generated TWO EldenRing
slots in one MultiWorld until 2026-07-02, which hid two whole classes of bug.

ER-MULTIWORLD-GEN-TESTS-20260702

Bug class 1 -- shared module-level item tables. generate_early USED to mutate the
module-level item_table / item_table_vanilla in worlds/eldenring/__init__.py
(classification demotes, .skip flips). With two ER slots, slot 1's mutations leaked
into slot 2: slot 2's set_rules used to crash on the gate-shorthand assert
("non-progression item 'Erudition' used as a location-gate shorthand").
patch_per_world_item_table (2026-07-02) fixed the class: each world now copies the
tables onto the INSTANCE in __init__ (world.item_table etc.) and every per-slot
reader/mutator uses the copies, so DIFFERING options are safe. T3
(TestDifferingOptionsDuo) is a hard regression gate now; its expectedFailure
decorator was removed when the overlay landed.

Bug class 2 -- cross-slot pool theft. grace_rando removed filler items from
multiworld.itempool with NO player filter (fixed by patch_silent_noop_warnings A1:
`it.player == self.player`). GLOBAL item/location counts stayed balanced, so
Fill.py's accounting never noticed. Only a PER-PLAYER conservation invariant can
catch this class -- see _assert_per_player_conservation for the derivation.

Idiom sources: multiworld construction via test.general.setup_multiworld and the
distribute + post_fill + finalize_multiworld completion sequence mirror
test/multiworld/test_multiworlds.py (TestTwoPlayerMulti); explicit fixed seeds and
the module docstring / run-command shape mirror
worlds/eldenring/tests/test_local_items_gen.py.

Run (Windows, from the Archipelago root):
    python worlds/eldenring/tests/run_tests.py multiworld_gen
"""
import unittest

from Fill import distribute_items_restrictive
from test.general import setup_multiworld
from worlds.AutoWorld import AutoWorldRegister, call_all
from worlds.eldenring.items import item_table, item_table_vanilla


# Fast 2-slot ER config exercising the mutation-prone generate_early passes:
# region_lock (lock injection + string gate-shorthand rules), tidy_fun_consumables
# (item_table .skip flips), randomize_enia OFF (Remembrance demote in the SHARED
# table -- the patch_fun_demoted_crossslot band-aid path), num_regions 0 (no
# spine), DLC off + minimal accessibility + no progression balancing for speed.
ER_FAST_OPTIONS = {
    "enable_dlc": False,
    "world_logic": "region_lock",
    "tidy_fun_consumables": True,
    "randomize_enia": False,
    "num_regions": 0,
    "accessibility": "minimal",
    "progression_balancing": 0,
}

# Post-overlay (patch_per_world_item_table 2026-07-02) generate_early mutates
# per-world INSTANCE copies, so the module tables should never change during a
# run. The snapshot below is kept as (a) a belt-and-braces restore and (b) the
# pristine baseline that T3 asserts the module tables against after a
# differing-options 2xER generation.
_TRACKED_FIELDS = ("classification", "skip", "filler", "inject")


def _snapshot_item_tables():
    snap = []
    for table in (item_table, item_table_vanilla):
        for data in table.values():
            fields = {f: getattr(data, f) for f in _TRACKED_FIELDS if hasattr(data, f)}
            snap.append((data, fields))
    return snap


_PRISTINE_TABLES = _snapshot_item_tables()


def _restore_item_tables():
    for data, fields in _PRISTINE_TABLES:
        for name, value in fields.items():
            setattr(data, name, value)


class _MultiworldGenTestBase(unittest.TestCase):
    """Multiworlds are built INSIDE the test methods (not setUp) so generation
    crashes are attributed to the test itself -- required for expectedFailure to
    capture the differing-options crash class in TestDifferingOptionsDuo."""

    def setUp(self):
        self.addCleanup(_restore_item_tables)

    @staticmethod
    def _world_type(game):
        return AutoWorldRegister.world_types[game]

    def _assert_per_player_conservation(self, multiworld):
        """Per-player item/location conservation at the pre-fill boundary.

        Derivation: Fill.distribute_items_restrictive pairs the FLAT
        multiworld.itempool against the FLAT multiworld.get_unfilled_locations()
        (top of distribute_items_restrictive) and raises only on the GLOBAL
        remainder; the per-player Counter diff near the bottom of the function is
        logging, and only fires on a global mismatch. So a world that removes
        another slot's pool items and/or locks items onto another slot's
        locations keeps global balance while corrupting that slot -- exactly the
        grace_rando theft (patch_silent_noop_warnings A1). The invariant:

          (a) no unfilled EVENT location remains (address None must be pre-filled
              by its own world before fill; an unfilled one would be paired with
              a real item by the flat fill and mask a count skew),
          (b) for every player p:  #(itempool items with item.player == p)
              == #(unfilled locations of p). Fails when p's pool was robbed
              (item side shrinks) or p's locations were filled from outside
              (location side shrinks),
          (c) every ALREADY-FILLED real-address location holds its OWN player's
              item. Pre-fill placements in this suite are all self-placements
              (ER grace tokens / vanilla locks; no plando), so a cross-player
              placement here pins case (b)'s location side to the offender.

        ER satisfies (b) by construction: create_items builds exactly one item
        per own unfilled location (the get_unfilled_locations(self.player) loop
        plus the num_required_extra_items filler top-up), and grace_rando is
        count-neutral per player (one OWN filler removed per locked token).
        """
        for loc in multiworld.get_unfilled_locations():
            self.assertIsNotNone(
                loc.address,
                "unfilled event location %s (player %d) at fill time" % (loc.name, loc.player))
        for player in multiworld.player_ids:
            pool = sum(1 for item in multiworld.itempool if item.player == player)
            unfilled = len(multiworld.get_unfilled_locations(player))
            self.assertEqual(
                pool, unfilled,
                "player %d (%s): %d pool items vs %d unfilled locations -- some world "
                "stole this slot's items or filled this slot's locations (global counts "
                "can still balance, so only this per-player check catches it)"
                % (player, multiworld.game[player], pool, unfilled))
        for loc in multiworld.get_filled_locations():
            if loc.address is not None:
                self.assertEqual(
                    loc.item.player, loc.player,
                    "pre-placed item %s (player %d) sits at %s belonging to player %d"
                    % (loc.item.name, loc.item.player, loc.name, loc.player))

    def _fill(self, multiworld):
        # Same completion sequence the fork's own multiworld suite drives
        # (test/multiworld/test_multiworlds.py, TestTwoPlayerMulti).
        distribute_items_restrictive(multiworld)
        call_all(multiworld, "post_fill")
        call_all(multiworld, "finalize_multiworld")


class TestTwoIdenticalERSlots(_MultiworldGenTestBase):
    """T1: identical-options 2xER duo -- Erudition-crash regression + conservation."""

    def test_identical_duo_generates_and_conserves(self):
        er = self._world_type("EldenRing")
        # Completing setup_multiworld at all IS the regression assert: before
        # patch_fun_demoted_crossslot, slot 2's set_rules crashed right here with
        # "non-progression item ... used as a location-gate shorthand".
        multiworld = setup_multiworld([er, er], options=ER_FAST_OPTIONS, seed=1)
        self._assert_per_player_conservation(multiworld)
        self._fill(multiworld)


class TestCrossGameDuo(_MultiworldGenTestBase):
    """T2: ChecksFinder + EldenRing, ER deliberately the SECOND player.

    Order matters for theft bugs: the unfiltered grace_rando comprehension took
    the FIRST matching filler in the flat itempool, i.e. an EARLIER player's
    items -- with ER second, the victim is ChecksFinder (25 items total, so the
    old bug would have gutted its entire pool). ChecksFinder is the pick because
    it is a tiny, dependency-free, always-shipped world (worlds/checksfinder)
    that generates on pure default options.
    """

    def test_er_as_second_player(self):
        cf = self._world_type("ChecksFinder")
        er = self._world_type("EldenRing")
        multiworld = setup_multiworld([cf, er], options=[{}, dict(ER_FAST_OPTIONS)], seed=2)
        self._assert_per_player_conservation(multiworld)
        self._fill(multiworld)


class TestDifferingOptionsDuo(_MultiworldGenTestBase):
    """T3: DIFFERING-options 2xER -- per-world item_table overlay regression gate."""

    def test_differing_enia_slots_keep_their_own_classifications(self):
        """Slot 1 (randomize_enia OFF) demotes every Remembrance entry to useful
        in generate_early; slot 2 (randomize_enia ON) logic-gates its Enia
        turn-in checks on its Remembrance items, so for slot 2 they MUST stay
        progression.

        Historically the demote hit the shared MODULE-LEVEL item_table and
        leaked into slot 2 (this test was @unittest.expectedFailure). Since
        patch_per_world_item_table (2026-07-02) each world mutates its own
        instance copy (world.item_table), so this is a hard regression gate:
        if it fails, some code path is mutating the module tables again.
        """
        er = self._world_type("EldenRing")
        slot1 = dict(ER_FAST_OPTIONS)                       # randomize_enia False
        slot2 = dict(ER_FAST_OPTIONS, randomize_enia=True)  # differs from slot 1
        multiworld = setup_multiworld([er, er], options=[slot1, slot2], seed=3)
        remembrances = [item for item in multiworld.itempool
                        if item.player == 2 and item.name.startswith("Remembrance")]
        self.assertTrue(remembrances,
                        "slot 2 (randomize_enia ON) should pool Remembrance items")
        demoted = sorted({item.name for item in remembrances if not item.advancement})
        self.assertFalse(
            demoted,
            "slot 1's randomize_enia=false demote leaked into slot 2's items via the "
            "shared module-level item_table: %s" % demoted)
        # Overlay invariant: after a DIFFERING-options 2xER generation the MODULE
        # tables must still match their import-time snapshot (all mutation is
        # per-instance now). Catches any new module-table mutation path.
        dirty = [(data.name, field, getattr(data, field))
                 for data, fields in _PRISTINE_TABLES
                 for field, pristine in fields.items()
                 if getattr(data, field) != pristine]
        self.assertFalse(
            dirty,
            "module-level item tables mutated during generation (per-world overlay "
            "regression); first offenders: %s" % dirty[:10])


class TestGraceTokenLocality(_MultiworldGenTestBase):
    """T4: grace_rando tokens must stay inside their owning slot (A1 regression)."""

    def test_grace_tokens_stay_local(self):
        er = self._world_type("EldenRing")
        options = dict(ER_FAST_OPTIONS, grace_rando=True)
        multiworld = setup_multiworld([er, er], options=options, seed=4)
        grace_placements = [loc for loc in multiworld.get_filled_locations()
                            if loc.item.name.startswith("Grace: ")]
        self.assertTrue(
            grace_placements,
            "grace_rando ON under region_lock should lock grace tokens at in-region "
            "checks; none found -- the placement pass did not run")
        for loc in grace_placements:
            self.assertEqual(
                loc.item.player, loc.player,
                "grace token %s (player %d) placed at %s of player %d"
                % (loc.item.name, loc.item.player, loc.name, loc.player))
        # The theft side of A1: each token's matching filler removal must have come
        # from the SAME slot's pool -- per-player conservation pins it.
        self._assert_per_player_conservation(multiworld)


if __name__ == "__main__":
    unittest.main()
