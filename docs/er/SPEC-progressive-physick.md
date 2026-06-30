# SPEC — Progressive Flask of Wondrous Physick (`progressive_physick`)

**Status:** drafted 2026-06-18. apworld + small client step-grant. Default OFF.
Supersedes the bundle-only approach (see SPEC-tear-bundles.md, now a pointer) —
the tear families become the *steps* of one progressive track.

## Goal

One escalating item carries the Physick flask + all the low-value Crystal tears,
in themed chunks. The flask is **earned in logic** (not handed out at spawn), the
junk tears arrive as orderly upgrades instead of a scatter of identical-feeling
pickups, and the ~18 build-defining tears stay **individual world checks**.

Solves three things the bundle + start-flask combo needed separate machinery for:
the dead-flask coupling, the junk-tear spam, and the "free physick at spawn"
inelegance — in one item track. Reuses the [[er-progressive-stone-bells]] /
[[er-bell-overflow-rune]] plumbing wholesale (cap+overflow, persist/dedup from
[[er-progressive-tier-persist]]); far less new client surface than a multi-grant
bundle map.

## Mechanic

A single progressive item — **"Progressive Flask of Wondrous Physick"** — placed
in the pool as K copies. Each received copy advances a step and grants that
step's payload (physical GOODS, granted to inventory via the existing
`[id,count]` multi-grant path — [[er-startitems-grant-loop]]). Overflow past the
last step → a Lord's Rune ([[er-bell-overflow-rune]]). One AP banner per step.

### Steps (bundle-stepped)

| # | Step | Payload (goods id) |
|---|---|---|
| [1] | **Flask** | Flask of Wondrous Physick itself — mechanic online |
| [2] | **Restorative Tears** | Crimsonspill (11000), Greenspill (11001), Crimson (11002), Cerulean (11004), Crimsonburst (11009), Greenburst (11010) |
| [3] | **Shrouding Tears** | Flame (11028), Magic (11029), Lightning (11030), Holy (11031) |
| [4] | **Sapping Tears** (DLC) | Crimson-Sapping (2011020), Cerulean-Sapping (2011030) |
| [5] | **Knot Tears** | Strength-knot (11021), Dexterity-knot (11022), Intelligence-knot (11023), Faith-knot (11024) |

Ordering rationale: flask first (turns the mechanic on), broadly-useful
restoratives early, the most situational family (Knot resistances) last. Step 4
(Sapping) exists **only when `enable_dlc`**; with DLC off it is removed and Knot
shifts up to step [4] — chain is 4 steps DLC-off, 5 steps DLC-on.

### Folded duplicates (→ runes, not in the chain)

Crimson (Alt) 11003, Cerulean (Alt) 11005, Ruptured (Alt) 11017 — pure dup
copies. Drop from pool, backfill as Golden Runes ([[er-filler-replacement]]).

### Kept individual (18 build-definers, unchanged world checks)

Speckled Hardtear (11006), Crimson Bubbletear (11007), Opaline Bubbletear
(11008), Opaline Hardtear (11011), Winged (11012), Thorny Cracked (11013), Spiked
Cracked (11014), Windy (11015), Ruptured (11016), Leaden Hardtear (11018), Twiggy
Cracked (11019), Crimsonwhorl Bubbletear (11020), **Cerulean Hidden (11025)**,
Stonebarb Cracked (11026), Purifying (11027), Bloodsucking (2011050, DLC),
Glovewort (2011060, DLC), Deflecting Hardtear (2011070, DLC).

> Membership is a starting cut — rows move freely between Step tables and Kept.
> Likely re-balance candidates: Windy and Glovewort lean junk; Speckled borderline.

## Pool accounting

- The 16 stepped members + 3 alternates leave the pool as discrete items.
- Pool gains **K progressive copies** (K = 4 DLC-off, 5 DLC-on) + the 18 kept
  individuals stay.
- Net change ≈ −15 (DLC-on) discrete items; backfill to count-neutral with the
  cheapest-first Golden Rune demand-drop ([[er-rune-skip-injectable-room]]), or
  let it shrink (a Trimmed/lean win). Match whatever the active mode already does
  — no new knob.
- The stepped tears' **vanilla locations stay checks**; only the items leave.

## Trim interaction

Tears are filler GOODS (same trap as [[er-spell-trim-keep]]). The progressive
item is **progression-classified**, so it survives Trimmed automatically. Keep a
`HIGH_TIER_TEARS` keep-set (= the 18 Kept ids) wired into the curation keep-rule
so the individuals also survive. Watch the `filler==0` falsy gotcha — force
`.classification` *after* `create_item` ([[er-filler-replacement]]).

## Option interactions

- **`progressive_physick` ON force-disables the start-flask grant**
  (`bell_physick_option`). The flask is now step [1], not a spawn item.
- ⚠ The Torrent start-grant currently gates on `bell_physick_option == 0`
  ([[er-torrent-start-grant]]) — confirm disabling the physick start path here
  doesn't accidentally drop or duplicate the Torrent grant. Decouple if needed.
- Mutually exclusive with any future flat `tear_bundles` / discrete-progressive
  tear option — gate one off the other.

## Implementation surface

- `items.py` — allocate **1 synthetic progressive item id** (⚠ open Q: free id
  block; don't collide with 11000-range or 2011xxx). Mark progressive.
- `options.py` — `progressive_physick` Toggle, default OFF, apworld-only.
- `__init__.py` `create_items` — when ON: drop the 16 stepped + 3 alternate tear
  items; add K Progressive Flask copies; force classification; backfill filler.
  Gate the Sapping step on `enable_dlc` (K = 4 vs 5; Knot collapses into the
  vacated slot when DLC-off so there's no index gap).
- `__init__.py` `item_name_groups` — register the 4 family names as groups
  (hintable; cheap to keep even with the toggle OFF).
- `curation.py` — `HIGH_TIER_TEARS` keep-set + wire into `_in_location_pool`.
- `fill_slot_data` — extend the existing `progressiveGrants` map: each Progressive
  Flask copy is `{"goodsList": [packed FullIDs...], "flags": []}` (a whole family),
  vs. the bells'/consumables' single `{"goods": id, "flags": []}`. Built from
  `physick_ladder(enable_dlc)`.
- **Client (separate repo, Windows build) — REAL change required.** The
  `progressiveGrants` consumer today grants ONE `goods` per copy; teach it to also
  honour an optional `goodsList` (grant every id in the list for that copy). Reuse
  the existing progressive counter + persisted-index dedup
  ([[er-progressive-tier-persist]]) and the past-the-ladder Lord's Rune overflow
  ([[er-bell-overflow-rune]], goods 2919). One banner per copy. NOTE: the
  consumables' "no client change" claim does NOT extend here — multi-goods steps
  are new.

Implemented by `patch_apworld_progressive_physick.py` (repo root; run on Windows,
verify via Read). It installs `physick_tears.py` and applies all apworld edits
above + the Torrent decoupling below.

## Open questions

1. Free synthetic item id for the progressive item.
2. Count-neutral backfill vs. let-it-shrink — default to active mode.
3. Final membership of Windy / Glovewort / Speckled.
4. ~~Torrent-grant decoupling from `bell_physick_option`~~ — DONE via the new
   `torrent_start` Choice (auto/on/off); auto preserves prior behaviour and adds
   progressive_physick to the grant condition. Torrent no longer keys off the flask
   start path.
5. Should step [1] (bare flask) also seed one starter tear so the first copy
   isn't a flask you can't yet fill usefully? (Lean: no — restoratives are step
   [2], close behind.)

## Testing

- Linux py3.11 gen-test: toggle ON, confirm spoiler shows K Progressive Flask
  copies + 18 individuals + 0 alternates; verify K=4 DLC-off / 5 DLC-on; pool
  count matches.
- Windows -Client build: receive copies in order, confirm step [1] grants the
  flask and each later step dumps its whole family into inventory and mixes into
  the flask; overflow copy yields a Lord's Rune; one banner per step; tier
  counter persists across a save/reconnect ([[er-progressive-tier-persist]]).
