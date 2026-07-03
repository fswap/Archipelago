"""Regenerate the Rust-side slot_data contract fixture (fixed seed) and assert it emitted.

The consuming half lives in the client repo:
`from-software-archipelago-clients/crates/er-logic/tests/slot_data_fixture.rs` reads the JSON this
test writes and pushes it through every er-logic slot_data consumer (options, scaling config,
progressive tiers, id maps). run_ci.ps1 orders UNIT before CARGO, so apworld-side drift fails on
the CONSUMING side in the same CI pass. The emitting-side key contract is separately asserted by
`ERSlotDataContract` in TestEROptionMatrix.py.

The seed is FIXED so the fixture only changes when the slot_data content genuinely changes (keeps
the submodule diff quiet). Region-spine surgery (SPEC-region-spine-surgery.md SS3b) hardcodes
smoothstep+sphere scaling unconditionally, so the SWEEP H4 cross-check (non-empty
regionSphereTargets whenever scaling is on) is exercised on every seed with no options needed to
arm it; DLC is enabled so the map is big.
"""
import json
import os

from test.bases import WorldTestBase

_FIXTURE_SEED = 1706

# worlds/eldenring/tests -> Archipelago root -> repo root -> client submodule fixture dir.
_HERE = os.path.dirname(os.path.abspath(__file__))
_AP_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_FIXTURE_DIR = os.path.join(
    _AP_ROOT, "..", "from-software-archipelago-clients", "crates", "er-logic", "tests", "fixtures"
)
_FIXTURE = os.path.abspath(os.path.join(_FIXTURE_DIR, "slot_data_fixture.json"))


class TestSlotDataFixture(WorldTestBase):
    game = "EldenRing"
    options = {
        "enable_dlc": True,
        "world_logic": "region_lock",
        # Region-spine surgery (SPEC-region-spine-surgery.md SS3b): completion_scaling /
        # completion_scaling_basis are DELETED options -- __init__.py now hardcodes
        # smoothstep + sphere basis unconditionally, so this world exercises the
        # regionSphereTargets emission path (the Rust-side H4 cross-check consumer) on
        # every seed with no options needed to arm it. Setting the old keys here would be
        # an OptionError post-surgery.
    }

    def world_setup(self, *args, **kwargs):
        # Fixed seed => stable fixture bytes run-to-run (only real contract changes diff).
        super().world_setup(seed=_FIXTURE_SEED)

    def test_regenerate_fixture_for_er_logic(self):
        sd = self.world.fill_slot_data()

        def _wire(o):
            # Mirror the AP wire encoding: raw slot_data may carry Python sets (JSON has no set
            # type; the server serializes them as arrays). Sort for byte-stable fixtures.
            if isinstance(o, (set, frozenset)):
                return sorted(o, key=str)
            raise TypeError("Object of type %s is not JSON serializable" % o.__class__.__name__)

        payload = json.dumps(sd, sort_keys=True, indent=1, default=_wire)
        # Spot-check the shape before shipping it to the Rust side.
        self.assertIn("options", sd)
        self.assertIn("apIdsToItemIds", sd)
        self.assertTrue(sd["apIdsToItemIds"], "apIdsToItemIds empty")
        # Emitting-side half of the Rust H4 cross-check: this class arms completion_scaling with
        # basis=sphere, so the sphere-target table must be non-empty -- an empty one would make
        # every client refuse to arm (scaling silently VANILLA for the whole seed).
        self.assertTrue(sd.get("regionSphereTargets"),
                        "completion_scaling(sphere) armed but regionSphereTargets is empty")
        if not os.path.isdir(_FIXTURE_DIR):
            # Client submodule not checked out (webhost-style AP checkout): nothing to refresh.
            self.skipTest("client submodule fixtures dir absent: %s" % _FIXTURE_DIR)
        old = None
        if os.path.exists(_FIXTURE):
            with open(_FIXTURE, "r", encoding="utf-8") as f:
                old = f.read()
        if old != payload:
            with open(_FIXTURE, "w", encoding="utf-8", newline="\n") as f:
                f.write(payload)
            print("slot_data fixture refreshed: %s (re-run cargo test -p er-logic)" % _FIXTURE)
