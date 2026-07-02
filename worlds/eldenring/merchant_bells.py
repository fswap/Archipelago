"""Merchant bell-bearing shop gating (opt-in: merchant_bell_logic).

See docs/er/SPEC-merchant-bells.md. Logic-only ("Option A"): each gated merchant's
shop checks require that merchant's Bell Bearing in logic, which pulls them out of
sphere 1. No baker/client work and no contract change -- the bell is simply promoted
to a real in-pool progression item and the shop locations gain a `state.has(bell)`
access rule.

SOURCE OF TRUTH: the token tables below. Each Bell Bearing item name maps to the
anchored substring token(s) that identify its shop= locations' display names.
resolve_merchant_bells() matches those tokens against the LIVE location table at
gen time (filtered to shop locations), so a future rename breaks loudly via the
double-match / zero-hit guards instead of silently un-gating a shop.

INCLUSION RULE (why only these 11): a merchant is gated only if it owns shop=
checks that the tokens below can identify. NOTE (2026-07-02,
shopslot-reachability): most of these bells have NO live pickup location in
locations.py (the drop rows are commented out),
so the gating bells are INJECTED into the item pool by generate_early
(item_table[bell].inject=True -> _all_injectable_items) instead of arriving
via a world drop; only Gowry's bell still enters through its location. Bells
that gate no shop= location (Bernahl, Sellen, Thops, Iji, Moore, Blackguard)
are never gated or injected.

EXCLUSIONS (never gated): Enia (Great-Rune/Remembrance exchanges, no bell), Twin
Maiden Husks (the fulfillment hub), Kale (gating his shop would kill the sphere-1
early-smithing "lean" checks), and the nomadic/isolated/hermit cart family
(many bells share one ambiguous "Nomadic Merchant" check name).
"""

from typing import Dict, List

# Bell Bearing item name -> anchored tokens found in the owning shop locations' names.
# Tokens are matched as plain substrings against shop= location display names. They are
# anchored (mostly with "- ") so the single-letter "D" cannot match unrelated rows and
# "Corhyn shop" also catches "Brother Corhyn shop".
BASE_MERCHANT_BELLS: Dict[str, List[str]] = {
    "Gostoc's Bell Bearing":     ["- Gostoc shop"],
    "Rogier's Bell Bearing":     ["- Rogier shop"],
    "Patches' Bell Bearing":     ["- Patches shop"],
    "Pidia's Bell Bearing":      ["- Pidia shop"],
    "Seluvis's Bell Bearing":    ["- Seluvis shop"],
    "Miriel's Bell Bearing":     ["- Miriel shop"],
    "Corhyn's Bell Bearing":     ["Corhyn shop"],
    "Gowry's Bell Bearing":      ["- Gowry Shop"],
    "D's Bell Bearing":          ["- D shop"],
    "Blackguard's Bell Bearing": ["Blackguard Boggart"],
}

# DLC merchants -- only applied when enable_dlc is set.
DLC_MERCHANT_BELLS: Dict[str, List[str]] = {
    "Ymir's Bell Bearing":       ["- Ymir shop"],
}


def merchant_bell_names(include_dlc: bool) -> List[str]:
    """Bell item names this feature promotes to progression."""
    names = list(BASE_MERCHANT_BELLS.keys())
    if include_dlc:
        names += list(DLC_MERCHANT_BELLS.keys())
    return names


def resolve_merchant_bells(location_dictionary, include_dlc: bool) -> Dict[str, List[str]]:
    """Map each gating Bell Bearing -> the exact shop location names it gates.

    Resolved against the live location table (shop locations only). Raises on an
    ambiguous double-match so a future data change fails loudly rather than silently
    mis-gating. Bells whose token matches nothing in this seed's scope are omitted.
    """
    tokens: Dict[str, List[str]] = dict(BASE_MERCHANT_BELLS)
    if include_dlc:
        tokens.update(DLC_MERCHANT_BELLS)

    shop_names = [
        name for name, data in location_dictionary.items()
        if getattr(data, "shop", False)
    ]

    result: Dict[str, List[str]] = {}
    owner: Dict[str, str] = {}
    for bell, toks in tokens.items():
        hits = [n for n in shop_names if any(t in n for t in toks)]
        if not hits:
            continue
        for n in hits:
            if n in owner:
                raise ValueError(
                    f"merchant_bells: location {n!r} matched by both "
                    f"{owner[n]!r} and {bell!r} -- tighten the tokens."
                )
            owner[n] = bell
        result[bell] = hits
    return result
