"""grace_rando OFF must NOT leak grace items into the item pool.

Grace items are constructed inject=True (items.py: ERItemData(..., inject=True, grace=True)) so
grace_rando can place them at checks. But the grace_rando option gate only guards PLACEMENT
(create_items), never the injection -- so with grace_rando OFF the grace items still flow into the
filler pool via _all_injectable_items. Found in playtest 2026-07-03 (grace_rando is off for v0.1).
This pins that no `Grace: ...` item reaches the pool when grace_rando is off.
"""
from test.bases import WorldTestBase


class GraceRandoOffNoLeak(WorldTestBase):
    game = "EldenRing"
    # grace_rando is DefaultOnToggle -> must set it False explicitly (v0.1 config).
    options = {"enable_dlc": False, "world_logic": "region_lock", "grace_rando": False}

    def test_no_grace_items_in_pool(self):
        # Grace items are named 'Grace: <place> (<region>)' / 'Grace: <region> #<flag>' -- the
        # 'Grace: ' prefix (with colon) is unique to them; excludes 'Grace Mimic' / 'Iris of Grace'.
        leaked = sorted({i.name for i in self.multiworld.itempool
                         if i.player == self.player and i.name.startswith("Grace: ")})
        self.assertEqual(leaked, [],
                         f"{len(leaked)} grace item(s) leaked into the pool with grace_rando OFF "
                         f"(e.g. {leaked[:5]}) -- grace items are inject=True unconditionally; "
                         f"their inject must be gated on grace_rando (generate_early)")
