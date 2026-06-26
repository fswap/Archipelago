"""Progressive consumable-upgrade grant tables (SPEC-progressive-consumables.md sections 1/2/5).

Four upgrade items collapsed into single progressive items, modelled on the stone bells.
Realisation = Option A: grant the vanilla goods id per received copy, and past the meaningful
cap grant a Lord's Rune (goods 2919) -- the SAME client path the stone bells already ship.
fill_slot_data emits these into "progressiveGrants" with EMPTY flag lists + an ordered goods
ladder, so the client grants goods[k] on the Kth copy and a Lord's Rune past the ladder length.
NO client change needed: the goods ladder + built-in overflow reuse the bell pipeline.

  - Flasks (fungible): Progressive Golden Seed (flask charges, goods 10010, cap 30) and
    Progressive Sacred Tear (flask potency, goods 10020, cap 12). Every copy grants the same
    goods; the player spends it at a grace/church. Copies past the vanilla cap -> Lord's Rune.
  - Glovewort bells (ordered ladder): Progressive Grave-Glovewort Bell -> bell bearings
    8960/8961/8962, Progressive Ghost-Glovewort Bell -> 8963/8964/8965. The Kth copy grants
    the Kth bell (in order); the player hands it to Roderika to stock that tier (vanilla).
    Copies past 3 -> Lord's Rune.

Future enhancement (NOT shipped here): the stone-bell-style Option B (auto-set Roderika's
eventFlag_forStock so the shop stocks without a hand-in) is BLOCKED on extracting the Roderika
spirit-tuning eventFlag_forStock groups from vanilla_er/ShopLineupParam.csv -- do NOT guess
those ids (see er-event-flag-validity). The Option-A hand-in path here is fully functional.
"""

OVERFLOW_GOODS = 2919  # Lord's Rune, granted per copy past the meaningful cap

PROG_GOLDEN_SEED = "Progressive Golden Seed"
PROG_SACRED_TEAR = "Progressive Sacred Tear"
PROG_GRAVE_GLOVE = "Progressive Grave-Glovewort Bell"
PROG_GHOST_GLOVE = "Progressive Ghost-Glovewort Bell"

# Discrete vanilla item -> the progressive item that REPLACES it 1:1 in the pool. Split by
# family so each toggle gates its own discretes independently.
FLASK_DISCRETE_TO_PROGRESSIVE = {
    "Golden Seed": PROG_GOLDEN_SEED,
    "Sacred Tear": PROG_SACRED_TEAR,
}
GLOVEWORT_DISCRETE_TO_PROGRESSIVE = {
    "Glovewort Picker's Bell Bearing [1]": PROG_GRAVE_GLOVE,
    "Glovewort Picker's Bell Bearing [2]": PROG_GRAVE_GLOVE,
    "Glovewort Picker's Bell Bearing [3]": PROG_GRAVE_GLOVE,
    "Ghost-Glovewort Picker's Bell Bearing [1]": PROG_GHOST_GLOVE,
    "Ghost-Glovewort Picker's Bell Bearing [2]": PROG_GHOST_GLOVE,
    "Ghost-Glovewort Picker's Bell Bearing [3]": PROG_GHOST_GLOVE,
}

# Per progressive item: the ORDERED goods ladder granted copy-by-copy. Length = the meaningful
# cap (copies past it overflow to a Lord's Rune, client-side). Fungible flasks repeat the same
# goods id up to the vanilla max; glovewort bells list the three distinct tiers in order.
CONSUMABLE_GOODS_LADDERS = {
    PROG_GOLDEN_SEED: [10010] * 30,   # 30 Golden Seeds = max flask charges
    PROG_SACRED_TEAR: [10020] * 12,   # 12 Sacred Tears = max flask potency
    PROG_GRAVE_GLOVE: [8960, 8961, 8962],
    PROG_GHOST_GLOVE: [8963, 8964, 8965],
}

FLASK_PROGRESSIVE_NAMES = (PROG_GOLDEN_SEED, PROG_SACRED_TEAR)
GLOVEWORT_PROGRESSIVE_NAMES = (PROG_GRAVE_GLOVE, PROG_GHOST_GLOVE)
