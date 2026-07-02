"""ER test-package guard (2026-07-02, trimmed by patch_per_world_item_table).

The ITEM-TABLE half of the original guard is RETIRED: generate_early now mutates
per-world instance copies (world.item_table / world.item_table_vanilla /
world.filler_item_names), so the module tables in worlds.eldenring.items stay
pristine for the life of the process and need no snapshot/restore
(tests/test_multiworld_gen.py T3 asserts exactly that).

What remains is the LOCATION half: rules_mixin.py still mutates the module-level
location_tables per slot (Leyndell .missable flips when royal_access is OFF), so
restore .missable before every WorldTestBase test to keep test order from
poisoning later modules. Retire this file's guard when locations get the same
per-world overlay treatment.
"""
from test.bases import WorldTestBase

from ..locations import location_tables

_MISSING = object()


def _snapshot_locations():
    locs = []
    for region_locs in location_tables.values():
        for loc in region_locs:
            locs.append((loc, getattr(loc, "missable", _MISSING)))
    return locs


_PRISTINE_LOCS = _snapshot_locations()


def restore_shared_tables():
    """Reset the remaining known shared-table mutation site (location .missable)."""
    for loc, v in _PRISTINE_LOCS:
        if v is not _MISSING:
            setattr(loc, "missable", v)


if not getattr(WorldTestBase, "_er_table_guard_installed", False):
    _orig_setup = WorldTestBase.setUp

    def _guarded_setup(self):
        restore_shared_tables()  # every test starts from pristine shared tables
        _orig_setup(self)

    WorldTestBase.setUp = _guarded_setup
    WorldTestBase._er_table_guard_installed = True
