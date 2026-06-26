"""Progressive Flask of Wondrous Physick ladder (SPEC-progressive-physick.md).

ONE progressive item collapses the flask + the low-value Crystal tears into themed
steps. Unlike the stone-bell / consumable ladders (one goods per copy), each physick
step grants a LIST of goods (a whole tear family), emitted into progressiveGrants as
{"goodsList": [...packed FullIDs...], "flags": []}. Step 0 = the empty flask itself.
Copies past the last step overflow to a Lord's Rune (client-side, same as the bells).

The ~18 build-defining tears stay individual randomized checks (HIGH_TIER_TEARS, used
by the Trimmed keep-rule). Pure-dup 'Alternate' tears are dropped to filler/runes.
"""

PROG_PHYSICK = "Progressive Flask of Wondrous Physick"

FLASK_GOODS = 250  # EquipParamGoods id: Flask of Wondrous Physick (granted at step 0)

# Per-step goods (raw EquipParamGoods ids; packed |0x40000000 at emit time in __init__).
_STEP_FLASK    = [FLASK_GOODS]
_STEP_RESTORE  = [11000, 11001, 11002, 11004, 11009, 11010]  # Crimsonspill/Greenspill/Crimson/Cerulean/Crimsonburst/Greenburst
_STEP_SHROUD   = [11028, 11029, 11030, 11031]                # Flame/Magic/Lightning/Holy-Shrouding
_STEP_SAPPING  = [2011020, 2011030]                          # Crimson-/Cerulean-Sapping  (DLC only)
_STEP_KNOT     = [11021, 11022, 11023, 11024]                # Strength/Dexterity/Intelligence/Faith-knot


def physick_ladder(enable_dlc):
    """Ordered list of steps (each a list of goods ids). Sapping is included only with
    the DLC; with it off the chain is 4 steps and Knot fills the vacated slot (no gap)."""
    steps = [_STEP_FLASK, _STEP_RESTORE, _STEP_SHROUD]
    if enable_dlc:
        steps.append(_STEP_SAPPING)
    steps.append(_STEP_KNOT)
    return steps


# Discrete item NAMES dropped from the pool when progressive_physick is on (the flask +
# every bundled/low-value tear + pure-dup alternates). The ladder grants these client-side.
PHYSICK_DROP_NAMES = frozenset({
    "Flask of Wondrous Physick",
    # restoratives
    "Crimsonspill Crystal Tear", "Greenspill Crystal Tear", "Crimson Crystal Tear",
    "Cerulean Crystal Tear", "Crimsonburst Crystal Tear", "Greenburst Crystal Tear",
    # elemental shrouding
    "Flame-Shrouding Cracked Tear", "Magic-Shrouding Cracked Tear",
    "Lightning-Shrouding Cracked Tear", "Holy-Shrouding Cracked Tear",
    # sapping (DLC)
    "Crimson-Sapping Cracked Tear", "Cerulean-Sapping Cracked Tear",
    # resistance knots
    "Strength-knot Crystal Tear", "Dexterity-knot Crystal Tear",
    "Intelligence-knot Crystal Tear", "Faith-knot Crystal Tear",
    # pure-dup alternates (vanilla double pickups) -> filler/runes
    "Crimson Crystal Tear (Alternate)", "Cerulean Crystal Tear (Alternate)",
    "Ruptured Crystal Tear (Alternate)",
})

# 18 build-definers KEPT as individual randomized checks. Used by the Trimmed keep-rule
# so these filler-classified GOODS are not scrubbed (mirrors HIGH_TIER_SPELLS).
HIGH_TIER_TEARS = frozenset({
    "Speckled Hardtear", "Crimson Bubbletear", "Opaline Bubbletear", "Opaline Hardtear",
    "Winged Crystal Tear", "Thorny Cracked Tear", "Spiked Cracked Tear", "Windy Crystal Tear",
    "Ruptured Crystal Tear", "Leaden Hardtear", "Twiggy Cracked Tear", "Crimsonwhorl Bubbletear",
    "Cerulean Hidden Tear", "Stonebarb Cracked Tear", "Purifying Crystal Tear",
    "Bloodsucking Cracked Tear", "Glovewort Crystal Tear", "Deflecting Hardtear",
})
