from dataclasses import dataclass

from Options import Choice, DeathLink, DefaultOnToggle, ExcludeLocations, OptionList, OptionSet, \
    OptionGroup, PerGameCommonOptions, Range, Toggle

## Game Options

class EndingCondition(Choice):
    """Ending Condition options
    
    **Final Boss:** Will be Elden Beast, or Consort if DLC is enabled.
    **Elden Beast:** Kill Elden Beast, for short runs with DLC on.
    **All Remembrances:** All remembrance bosses, missable ones excluded.
    **All Bosses:** All bosses, missable ones excluded.
    **Capital:** Reach Leyndell and defeat Morgott, the Omen King -- a short run. Pairs with
    `region_count` to seal off everything past the capital.
    **Messmer:** DLC mini-campaign -- reach Shadow Keep and defeat Messmer the Impaler. Keeps
    only the front-half DLC (Gravesite/Belurat/Castle Ensis/Scadu Altus/Shadow Keep) and seals
    the rest. Forces dlc_only on; messmer_kindle is forced off (Enir Ilim is sealed).
    **Godrick:** Shortest base-game run -- keep only Limgrave, Weeping Peninsula and
    Stormveil Castle, then defeat Godrick the Grafted; everything else (and all DLC) is
    sealed. Needs a lock-based world logic (region_lock / region_lock_bosses); forces
    dlc_only off.
    If DLC is on those bosses / remembrances are included (Capital ignores the DLC; it always
    ends at Morgott)."""
    display_name = "Ending Condition"  # this is the option name as it's displayed to the user on the webhost and in the spoiler log
    option_final_boss = 0
    option_elden_beast = 1
    option_all_remembrances = 2
    option_all_bosses = 3
    option_capital = 4
    option_messmer = 5
    option_godrick = 6

class WorldLogic(Choice):
    """World Logic options
    
    **Region Lock:** Each region will require a 'Special item'
    **Region Bosses:** Each region will require % of bosses in that region to be defeated
    **Region Lock Bosses:** Each region will require % of bosses in that region to be defeated and a 'Special item'
    **Open World:** No region locking"""
    display_name = "World Logic"
    option_region_lock = 0
    option_region_bosses = 1
    option_region_lock_bosses = 2
    option_open_world = 3
    default = 0
    
class RegionBossPercent(Range):
    """The % of bosses in a region to unlock the next"""
    display_name = "Region Boss Percent"
    range_start = 1
    range_end = 100
    default = 50
    

    
class RegionSoftLogic(DefaultOnToggle):
    """Region Soft Logic
    
    You might get early caelid access but you won't be expected to go there early.
    """
    display_name = "Region Soft Logic"

class GreatRunesRequired(Range):
    """How many great runes are required to enter Leyndell
    This option is ignored if Region Lock in On"""
    display_name = "Leyndell Great Runes Required"
    range_start = 1
    range_end = 7
    default = 2
    
class GreatRunesFinalBoss(Range):
    """How many great runes are required to access the final boss (the Erdtree:
    Radagon / Elden Beast). 0 means no additional great-rune requirement."""
    display_name = "Final Boss Great Runes Required"
    range_start = 0
    range_end = 7
    default = 0

class GreatRunesMountaintops(Range):
    """How many great runes are required to enter the Mountaintops of the Giants,
    in addition to the Rold Medallion. 0 means no great-rune requirement."""
    display_name = "Mountaintops Great Runes Required"
    range_start = 0
    range_end = 7
    default = 0



class DeathlessRouting(Toggle):
    """Exclude the Volcano Manor abduction (a death-based shortcut from Raya Lucaria) from
    logic. With this on, the Manor complex must be reached legitimately via Mt. Gelmir and
    the Drawing-Room Key rather than by being abducted."""
    display_name = "Deathless Routing"

class GracesPerRegion(Range):
    """Region fusion (TODO #13): how many Sites of Grace to unlock per region when you receive
    that region's lock item (fast travel into the region, no Torrent slog). Graces are chosen by
    spatial spread (a central hub first, then maximum coverage) so the picks are useful, not
    clustered. 0 = unlock ALL of the region's graces (most convenient, least exploration).
    1 = just a warp-in hub. Higher = more coverage. Only takes effect with region gating
    (world_logic region_lock / region_bosses) and a client that consumes regionGraces."""
    display_name = "Graces Unlocked Per Region"
    range_start = 0
    range_end = 12
    default = 3

class GraceRando(DefaultOnToggle):
    """Grace rando (region gating only). Instead of a region lock lighting ALL of that
    region's Sites of Grace, receiving the lock lights ONE RANDOM grace (your warp-in point)
    and every OTHER grace in the region becomes an individual item dropped at a check INSIDE
    that same region -- found by exploring. Count-neutral (swaps for filler), so it never
    grows the pool. ON BY DEFAULT under region gating; set false for the old bundle
    (graces_per_region) behavior. No effect outside a region-gating world_logic."""
    display_name = "Grace Rando"

class RegionAccessLogic(Choice):
    """How region-lock logic models REACHING a region (world_logic region_lock / region_bosses).

    - **Geographic:** you must physically path through connected regions, holding every lock along
      the way (e.g. Altus needs Liurnia Lock AND Altus Lock). The original behavior.
    - **Warp:** a region's OWN lock is sufficient -- receiving it unlocks that region's graces, so
      you fast-travel straight in (Altus needs only Altus Lock). Matches the grace-grant bundle and
      the physical region-lock enforcement, and allows seeds where a geographically-deep region is
      the bootstrap. Only meaningful with region gating + the grace bundle (graces_per_region)."""
    display_name = "Region Access Logic"
    option_geographic = 0
    option_warp = 1
    default = 0

class NumRegions(Range):
    """Short 'reach the capital and kill Morgott' run: keep this many overworld majors and seal
    the rest. num_regions_order chooses HOW the kept set is picked:

      rolled (default) -- N majors rolled at random; reached by warp (forces region_access=warp),
                          since a non-contiguous set has no walking route.
      spine            -- the fixed first-N steps of the spine toward Morgott (1 Limgrave,
                          2 Weeping, 3 Stormveil, 4 Liurnia, 5 Caelid, 6 Dragonbarrow, 7 Altus,
                          8 Volcano), reached geographically. This is the old region_count.

    Limgrave (the free start hub) and Leyndell + Morgott (the goal capstone) are ALWAYS kept and
    both count toward this number. A great-rune floor keeps enough great-rune bosses (Godrick /
    Rennala / Radahn / Rykard) in scope to open Leyndell, so the count is auto-raised if too low.

    Only takes effect with the **Capital** ending condition AND region gating (world_logic
    region_lock / region_lock_bosses). 0 = disabled. ~4 gives a short (roughly 3-4 hour) run."""
    display_name = "Num Regions (Capital run)"
    range_start = 0
    range_end = 9
    default = 0

class NumRegionsOrder(Choice):
    """How num_regions chooses which overworld majors to keep (only matters when num_regions > 0).

    - **rolled** (default): roll N majors at random; reached by warp (forces region_access=warp).
      The original num_regions behavior.
    - **spine**: keep the fixed first-N steps of the spine toward Morgott (Limgrave, Weeping,
      Stormveil, Liurnia, Caelid, Dragonbarrow, Altus, Volcano), reached geographically. This is
      the old region_count option, folded in here.

    Ignored unless num_regions > 0 (and, like num_regions, only under the Capital goal + lock
    logic). num_regions_rune_source: pool is ignored under spine (pool rolls a random set)."""
    display_name = "Num Regions Order"
    option_rolled = 0
    option_spine = 1
    default = 0

class NumRegionsRuneSource(Choice):
    """Where the great runes that open Leyndell come from, under a num_regions Capital run.

    Leyndell's gate is a pure item count (it needs `great_runes_required` great runes, with NO
    region/tower dependency), so the runes can come from EITHER kept boss regions or the item pool.

    **regions** (default): the runes live on their boss in KEPT regions. num_regions is raised so
        enough rune bosses (and Altus, the only route) stay in scope -- the floor couples the region
        count to great_runes_required, so very small runs are impossible. Limgrave is the forced hub.

    **pool**: the runes are INJECTED into the item pool as items (count-neutral -- one filler slot is
        freed per injected rune) instead of being kept as boss regions. The region floor drops to
        just the always-kept set (Roundtable hub + Leyndell), so a 1-middle-region run is legal, and
        Limgrave is no longer force-kept (it becomes a normal rollable/sealable middle). The random
        non-contiguous set is reached by WARP via the Roundtable hub (each region by its own lock;
        Limgrave by 'Warp To Limgrave'). Only meaningful when num_regions > 0."""
    display_name = "Num Regions Rune Source"
    option_regions = 0
    option_pool = 1
    default = 0

class NumRegionsChain(Toggle):
    """Chain the random num_regions Capital run into a linear lock breadcrumb so the difficulty
    (and AP fill spheres) ramp 1..N instead of every region opening from sphere 1.

    With this ON, the kept regions form a single line off the Limgrave hub: the first region's
    lock is free, and every later region's lock is found on the PREVIOUS region's main boss --
    so you clear region 1 to open region 2, clear region 2 to open region 3, and so on, up to
    Altus -> Leyndell -> Morgott. Altus is always the last link before the capital. Sphere-ordered
    completion scaling can then tier each region by its depth in the chain.

    Only meaningful with `num_regions > 0`, the **Capital** ending condition, and region gating
    (world_logic region_lock / region_lock_bosses); ignored otherwise. Off = the flat num_regions
    roll (all kept regions reachable from sphere 1)."""
    display_name = "Num Regions Chain (linear sphere ramp)"


class DLCOnlyChain(Toggle):
    """Chain the DLC-only (Land of Shadow) run into a linear lock breadcrumb so the AP fill
    spheres (and completion scaling) ramp 1..N instead of every kept DLC region opening from
    sphere 1.

    PHASE 1: only acts under the **Messmer** ending condition (which forces dlc_only on). The kept
    DLC slice -- Gravesite (free hub) -> Belurat / Ensis -> Scadu Altus -> Shadow Keep (Messmer) --
    is breadcrumbed: the first gated region's lock is found on a Gravesite boss, and each later
    region's lock is found on the PREVIOUS region's main boss, with Shadow Keep / Messmer pinned
    last. Off = the flat dlc_only roll (all kept regions reachable from sphere 1).

    A plain dlc_only seed (no Messmer goal) with this ON warns and no-ops: the full 14-lock DLC
    tree chain is Phase 2 (it needs the per-region warp-grace audit). See SPEC-dlc-only-chain.md."""
    display_name = "DLC-Only Chain (linear sphere ramp)"



class RoyalAccess(Toggle):
    """Keep Royal Capital graces accessable after it becomes ashen."""
    display_name = "Royal Capital Accessable"

class ExtraRegionLocks(OptionSet):
    """Opt-in granular region locks (region_lock / region_lock_bosses only). Each name splits a
    finer lock into its own sphere instead of folding under its parent region's lock. Empty
    (default) = coarse, the original behavior.
      stormhill    -- gate Stormhill (Limgrave -> Stormveil mid-spine key)
      godrick      -- gate the Godrick goal behind its own lock, separate from Stormveil Castle
      castle_morne -- gate the Castle Morne interior separately from Weeping (needs the carve)
      limgrave_caves -- ALIAS of limgrave_underground (auto-normalized in code); the same 10 underground regions (Fringefolk Hero's Grave, Coastal
                        Cave + Church of Dragon Communion, Groveside Cave, Stormfoot Catacombs,
                        Limgrave Tunnels, Murkwater Cave, Murkwater Catacombs, Highroad Cave,
                        Deathtouched Catacombs) behind one shared lock
      liurnia_caves -- gate Liurnia's 8 minor dungeons (Stillwater/Lakeside/Academy caves, Road's
                       End/Black Knife/Cliffbottom catacombs, Raya Lucaria Crystal Tunnel,
                       Ruin-Strewn Precipice) behind one shared lock
      limgrave_underground -- gate Limgrave's 10 underground regions (Fringefolk Hero's Grave,
                              Coastal Cave + Church of Dragon Communion, Groveside Cave, Stormfoot
                              Catacombs, Limgrave Tunnels, Murkwater Cave, Murkwater Catacombs,
                              Highroad Cave, Deathtouched Catacombs) behind one shared lock
      mountaintops_caves -- gate the 6 Mountaintops/Snowfield minor dungeons (Giant-Conquering
                            Hero's Grave, Giants' Mountaintop Catacombs, Spiritcaller Cave,
                            Consecrated Snowfield Catacombs, Cave of the Forlorn, Yelough Anix
                            Tunnel) behind one shared lock
      altus_caves -- gate Altus Plateau's 6 minor dungeons (Sainted Hero's Grave, Unsightly
                     Catacombs, Perfumer's Grotto, Sage's Cave, Old Altus Tunnel, Altus Tunnel)
                     behind one shared lock, split out from Altus Plateau
      dlc_catacombs -- (DLC) gate Fog Rift Catacombs + Belurat Gaol behind one shared lock,
                       split out from Gravesite Plain (Messmer mini-campaign granularity)
      chokepoint_locks -- gate legacy-dungeon BACK halves on their mid-boss chokepoint, and
                          split that dungeon's sweep into before/after (Godskin Duo -> Farum
                          Azula Main, Loretta -> Elphael). Pure logic; see SPEC-chokepoint-locks.md
      snowfield -- split Consecrated Snowfield (101 overworld checks / 130 with its minor
                   dungeons) out of the Mountaintops/Rold cluster behind its own dedicated
                   'Snowfield Lock', so it seals and opens independently (still reached via
                   the Haligtree Secret Medallion route)
    """
    display_name = "Extra Region Locks"
    valid_keys = {"stormhill", "godrick", "castle_morne", "dlc_catacombs"}

    valid_keys = valid_keys | {"altus_caves"}
    valid_keys = valid_keys | {"mountaintops_caves"}
    valid_keys = valid_keys | {"limgrave_underground"}
    valid_keys = valid_keys | {"liurnia_caves"}
    valid_keys = valid_keys | {"limgrave_caves"}
    valid_keys = valid_keys | {"chokepoint_locks"}
    valid_keys = valid_keys | {"snowfield"}
class EarlyLeveling(Toggle):
    """Grant the ability to Level Up at Sites of Grace from the start, skipping Melina's accord
    and her meeting cutscene entirely. Sets event flag 4680 (Level Up enable) + 951 (Melina
    first-meeting done) at load. Useful for region-lock / dlc_only runs where her grace trigger
    may never fire. Because suppressing the meeting also skips her Torrent hand-off, this co-grants
    Torrent (Spectral Steed Whistle) so you are never left without the mount."""
    display_name = "Early Leveling (skip Melina)"

class QuickStart(Toggle):
    """Quick Start (dlc_only): grant enough Lord's Runes at load-in to reach ~Runelevel 120
    right away. A DLC-only run skips the base game's rune-earning curve, so this hands you the
    runes you would have farmed there. Reaching RL120 from level 1 costs 3,506,749 runes total;
    this grants 71 Lord's Runes (50,000 each = 3,550,000), held as consumable items you spend
    and level with at any Site of Grace. Only takes effect when dlc_only is on (it is inert
    otherwise, since a normal start earns these runes through play)."""
    display_name = "Quick Start (RL120 runes, dlc_only)"

class DLCOnlyRuneCatchup(Toggle):
    """Rune Catch-up (dlc_only): turn every rune-currency drop in the pool into a
    Lord's Rune (50,000 runes each) so a DLC-only start can rocket up to the DLC's
    enemy scaling. A DLC-only run skips the base game's whole rune-earning curve;
    this makes the rune drops you DO find pay out at the maximum rate. Every Golden
    Rune / Hero's Rune / Numen's Rune / smaller rune (base and DLC) becomes a Lord's
    Rune in place -- same number of items, just each worth 50,000. Great Runes and
    Rune Arcs are NOT runes-currency and are left untouched. Only takes effect when
    dlc_only is on (inert otherwise)."""
    display_name = "Rune Catch-up (Lord's Runes, dlc_only)"

class EnableDLC(Toggle):
    """Enable DLC"""
    display_name = "Enable DLC"

class DLCOnly(Toggle):
    """Restrict the check pool to the Shadow of the Erdtree DLC only (base game kept for
    traversal, but holds no checks). Forces Enable DLC on. Inverse of enable_dlc."""
    display_name = "DLC Only"
    
class ScadutreeFrontload(Range):
    """Bias this many TOTAL Scadutree Fragments into the earliest reachable locations
    (sphere 1) so Scadutree Blessing can ramp early and the DLC's area-scaled enemies
    (enemy attack ~x3.75 from the first zone) stop one-shotting a fresh dlc_only start.
    The fragments are still real checks -- just placed early; you still revere them at a
    Land of Shadow grace. 0 = no front-loading (fragments distribute normally -- the
    'true sicko' setting). Only meaningful with the DLC on; capped at how many fragments
    exist in the pool. See SPEC-scadu-in-base.md (dlc_only addendum)."""
    display_name = "Scadutree Fragment Front-load"
    range_start = 0
    range_end = 50
    default = 8

class MessmerKindle(Toggle):
    """Messmer Kindle Shards"""
    display_name = "Messmer Kindle Shards"
    
class MessmerKindleRequired(Range):
    """Messmer Kindle Shards required to access Enir Ilim."""
    display_name = "Messmer Kindle Shards Required"
    range_start = 2
    range_end = 15
    default = 5
    
class MessmerKindleMax(Range):
    """How many Messmer Kindle Shards there are."""
    display_name = "Messmer Kindle Shards Max"
    range_start = 2
    range_end = 15
    default = 10

class DLCTimingOption(Choice):
    """Guarantee that you don't need to enter the DLC until later in the run.

    - **Early:** 'Pureblood Knight Medal' will spawn in an early sphere.
    - **Off:** You may have to enter the DLC with 'Pureblood Knight Medal' item.
    - **Late:** You won't have to enter the DLC until after getting to Snowfield.
    """
    display_name = "DLC Timing"
    option_early = 0
    option_off = 1
    option_late = 2
    default = 1
    
class EnemyRando(Toggle):
    """Randomizes the enemies."""
    display_name = "Enemy randomizer"

class MaterialRando(DefaultOnToggle):
    """Randomizes the indefinitely spawning materials."""
    display_name = "Material Randomizer"

## Item & Location

class RandomizeStartingLoadout(DefaultOnToggle):
    """Randomizes the equipment characters begin with."""
    display_name = "Randomize Starting Loadout"

class AutoEquipOption(Toggle):
    """Automatically equips any received armor or left/right weapons."""
    display_name = "Auto-Equip"
    
class AutoUpgradeOption(Toggle):
    """Automatically upgrades any received weapons to highest upgraded level."""
    display_name = "Auto-Upgrade"
    
class ProgressiveItems(OptionSet):
    """Consolidated front-end for the progressive upgrade-item families. Each key replaces
    that family's discrete pickups with PROGRESSIVE items (see the individual options for the
    full detail). This is the preferred way to set them; the legacy per-family toggles still
    work and are OR-unioned in (mapped onto the booleans at generate_early).

      stone_bells     -- Miner's Bell Bearings -> 2 progressive (Smithing x4 / Somber x5)
      glovewort_bells -- Glovewort Picker's Bell Bearings -> 2 progressive (Grave x3 / Ghost x3)
      flasks          -- Golden Seeds + Sacred Tears -> 2 progressive (charges / potency)
      physick         -- Flask of Wondrous Physick + low-value tears -> 1 progressive ladder
    """
    display_name = "Progressive Items"
    valid_keys = {"stone_bells", "glovewort_bells", "flasks", "physick"}


class ProgressiveStoneBells(Toggle):
    """Replace the 9 discrete Miner's Bell Bearings with 2 PROGRESSIVE items
    (Smithing x4, Somber x5). The Nth copy received unlocks the next rung of the
    Twin Maidens stone shop, in order. Works with auto_upgrade too: the shop is a
    stone source, and using stones is what raises the live auto-upgrade target. See
    SPEC-progressive-stone-bells.md."""
    display_name = "Progressive Stone Bell Bearings"

class ProgressiveBellCount(Range):
    """How many copies of EACH progressive stone bell (Smithing, Somber) to put in the pool
    when progressive_stone_bells is on. There are only 4 Smithing / 5 Somber real upgrade
    tiers; copies beyond that are overflow that grant a Lord's Rune each (client-side). More
    copies = the upgrade ladder comes online earlier and more rune payout, but in dlc_only they
    inject as mandatory progression and eat the tight injection budget, so keep it modest.
    Applies to both bells equally. Only matters when progressive_stone_bells is on."""
    display_name = "Progressive Bell Pool Count"
    range_start = 5
    range_end = 40
    default = 15

class ProgressiveBellEarlyCount(Range):
    """How many copies of EACH progressive stone bell to FORCE into sphere-1 (no-item-reachable)
    locations in dlc_only, via early_items, so the upgrade ladder opens near the start. Soft and
    capped by pool availability + sphere-1 size, so it never fails gen. 0 = no early forcing
    (normal distribution). Only matters when progressive_stone_bells is on and dlc_only."""
    display_name = "Progressive Bell Early Count"
    range_start = 0
    range_end = 10
    default = 4

class CraftingKitOption(Choice):
    """Choose how the Crafting Kit is handled.

    - **Randomize:** Can be anywhere.
    - **Early:** Make it anywhere before Altus and not in Caelid.
    - **Do Not Randomize:** Leave it at its normal spot.
    - **Start With:** Granted at the start of the run (a copy also stays in the pool).
    """
    display_name = "Crafting Kit Behavior"
    option_randomize = 0
    option_early = 1
    option_do_not_randomize = 2
    option_start_with = 3
    default = 1
    
class MapOption(Choice):
    """Choose how maps are handled.

    - **Randomize:** Can be anywhere.
    - **Give:** Add to starting inventory.
    - **Do Not Randomize:** Leave it at its normal spot.
    """
    display_name = "Map Behavior"
    option_randomize = 0
    option_give = 1
    option_do_not_randomize = 2
    default = 1
    
class SmithingBellBearingOption(Choice):
    """Choose how smithing stone bell bearings are handled.

    - **Randomize:** Can be anywhere.
    - **Progression Randomize:** Make them a progression item, and be required for the area after they would normally be in.
    - **Do Not Randomize:** Leave them at their normal spots.
    """
    display_name = "Smithing Bell Bearing Behavior"
    option_randomize = 0
    option_progression_randomize = 1
    option_do_not_randomize = 2
    default = 1
    
class MerchantBellLogic(Choice):
    """Gate merchant shop checks behind that merchant's Bell Bearing.

    - **Off:** Merchant shops are in logic as normal.
    - **Logic Only:** A merchant's shop checks require receiving that merchant's Bell
      Bearing (promoted to an in-pool progression item), pulling those checks out of
      sphere 1. Only merchants whose bell has a real world drop are gated. Logic-only:
      no physical relocation of stock. See docs/er/SPEC-merchant-bells.md.
    """
    display_name = "Merchant Bell Bearing Logic"
    option_off = 0
    option_logic_only = 1
    default = 0

class SpellShopSpellsOnly(Toggle):
    """Spell Shops only have spells."""
    display_name = "Spell Shop Spells Only"
    
class EarlyLegacyDungeonsEarly(Toggle):
    """Early Legacy Dungeons are early"""
    display_name = "Early Legacy Dungeons Early"
    
class LocalItemOnly(DefaultOnToggle):
    """Only progression or useful items will show up in other players games.
    Used with ExcludeLocalItemOnly option."""
    display_name = "Local Item Option"
    
class ExcludeLocalItemOnly(OptionList):
    """If LocalItemOnly is true then these item categories will show up in other players games.
    - [Items] **Item Group**
    - [~600] **Weapon**: All Weapons and Ammo.
    - [621] **Armor**: All Armors.
    - [154] **Accessory**: All Talismans.
    - [105] **AshofWar**: All Ashes of War.
    - [~3700] **Goods**: All Goods.
    
    Goods should always be local only.
    """
    display_name = "Exclude Local Item Only"
    default = ["Weapon", "Armor", "Accessory", "AshofWar"]
    valid_keys_casefold = ["Weapon", "Armor", "Accessory", "AshofWar", "Goods"]
    
class ERImportantLocations(OptionList):
    """Prevent these location types from having an unimportant items.
    - [Checks] **Locations**
    - [25] *Remembrance*: Main boss Remembrances.
    - [33] *Seedtree*: Golden Seed trees.
    - [13] *Basin*: Basins that contain tears.
    - [12] *Church*: Sacred Tears.
    - [24] *Map*: Map pillars.
    - [52] *Fragment*: Scadu Fragments.
    - [13] *Cross*: All cross items.
    - [26] *Revered*: Revered Spirit Ashes.
    - [21] *KeyItem*: Key items.
    - [~52] *Boss*: Major boss drops (broader than Remembrance; can over-constrain).
    - [21] *Shop*: Twin Maiden Husks shop (Roundtable Hold), non-missable. Opt-in; not in default.
    
    The *total* amount of priority checks should be below:
    - **Vanilla**: [90] 
    - **DLC**: [120]
    """
    display_name = "Important Locations"
    default = ["Remembrance", "Seedtree", "Church", "Boss", "Fragment", "Revered"]
    valid_keys_casefold = ["Remembrance", "Seedtree", "Basin", "Church", "Map", "Fragment", "Cross", "Revered", "KeyItem", "Boss", "Shop"]

class ERExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important items.
    - **dlc**: If you want DLC items but dont wanna do DLC.
    - **hidden**: Hard to find items.
    - **blizzard**: The hard to see area of snowfield."""
    default = frozenset()  # keys (dlc/hidden/blizzard) wired to location groups in locations.py
    # dlc / hidden / blizzard resolve via location_name_groups (see patch_apworld_exclude_locations_groups.py).
    valid_keys_casefold = ["dlc", "hidden", "blizzard"]

class ExcludedLocationBehaviorOption(Choice):
    """How to choose items for excluded locations in ER.

    - **Allow Useful:** Excluded locations can't have progression items, but they can have useful items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in excluded locations.
    - **Do Not Randomize:** Excluded locations always contain the same item as in vanilla Elden Ring.

    A "progression item" is anything that's required to unlock another location in some game.
    A "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Excluded Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    default = 2

class MissableLocationBehaviorOption(Choice):
    """Which items can be placed in locations that can be permanently missed.

    - **Allow Useful:** Missable locations can't have progression items, but they can have useful items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in missable locations.
    - **Do Not Randomize:** Missable locations always contain the same item as in vanilla Elden Ring.

    A "progression item" is anything that's required to unlock another location in some game.
    A "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Missable Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    default = 2

class NoWeaponRequirements(Toggle):
    """Remove all stat requirements from weapons, ammo, and spells.

    Anything the multiworld hands you is immediately usable regardless of build —
    useful when your weapon progression is at the mercy of the item pool.
    """
    display_name = "No Weapon Requirements"

class DungeonSweep(Choice):
    """Beating a dungeon's boss automatically sends every remaining check in that dungeon.

    - **None:** Normal behavior; every check must be picked up individually.
    - **Minidungeons:** Catacombs, caves, tunnels, heroes' graves, and gaols sweep when
      their boss dies.
    - **All:** Minidungeons plus legacy dungeons (Stormveil, Raya Lucaria, Volcano Manor,
      Leyndell, Farum Azula, the Haligtree, Mohgwyn Palace, and the DLC legacy dungeons),
      which sweep when their main (remembrance) boss dies, plus self-contained castle
      regions (Caria Manor, Fog Rift Fort), which sweep on their boss drop.
    - **Bosses:** Total boss attribution (SPEC-boss-attribution.md). Everything in **All**,
      plus every open-world check is attributed to the nearest field boss in its region
      (Agheel, Lansseax, Tibia Mariner, evergaols, night bosses...), falling back to the
      region's great-rune/remembrance boss. Killing any boss sweeps the checks attributed
      to it; see Grace Sweep for a complementary trigger. The bake emits this map to
      apconfig.json (sweep_flags).

    Swept shop checks are sent without purchase, and swept quest checks skip their
    questlines (this also rescues missable NPC checks inside dungeons). Note this can
    send 30+ checks at once, which affects pacing for everyone else in the multiworld.
    """
    display_name = "Dungeon Sweep"
    option_none = 0
    option_minidungeons = 1
    option_all = 2
    option_bosses = 3
    default = 0

class GraceSweep(Choice):
    """Complementary trigger for Dungeon Sweep = **Bosses**: lighting a Site of Grace sweeps
    nearby checks, filling the gaps where field bosses are sparse. A check sends on whichever
    of its triggers fires first (boss killed OR grace lit). Has no effect unless Dungeon Sweep
    is set to Bosses.

    - **Off:** Boss triggers only.
    - **Complement:** Only checks the boss layer covers poorly (far from any field boss, or
      stuck on a region capstone) also get a grace trigger. Targeted; recommended.
    - **Full:** Every open-world check also gets its nearest-grace trigger, so lighting graces
      sweeps the world as you explore. Strong; can trivialize exploration.
    """
    display_name = "Grace Sweep"
    option_off = 0
    option_complement = 1
    option_full = 2
    default = 0

class SwapMultiBoss(Toggle):
    """Enemy randomizer: swap bosses between multi-boss fights (mini-dungeon bosses only).
    Only has an effect when the Enemy Randomizer is enabled."""
    display_name = "Swap Multi-Boss Fights"

class BossRunesMatchOriginal(Toggle):
    """Enemy randomizer: a relocated boss drops the runes the original occupant of that
    spot would have dropped, instead of its own. Only applies with Enemy Randomizer on."""
    display_name = "Boss Runes Match Original"

class ImpoliteEnemies(Toggle):
    """Enemy randomizer: make enemies less passive in groups (they aggro more readily).
    Only has an effect when the Enemy Randomizer is enabled."""
    display_name = "Impolite Enemies"

class DisableSerpentHunterUpgrade(Toggle):
    """Disable upgrading the Serpent-Hunter greatspear (a niche base-randomizer balance
    tweak). Applies whether or not the Enemy Randomizer is on."""
    display_name = "Disable Serpent-Hunter Upgrade"

class BellPhysickOption(Choice):
    """How to handle the Spirit Calling Bell and Flask of Wondrous Physick. Both are inert
    on their own -- the bell needs Spirit Ashes, the flask needs Crystal Tears -- so a random
    early pickup of either sits useless until its companions turn up.

    - **Start With:** granted at the start of the run (a copy is also left in the pool).
    - **Do Not Randomize:** locked at their vanilla locations (Ranni / Third Church of Marika).
    - **Randomize:** shuffled into the pool like any other item.
    """
    display_name = "Bell & Physick Handling"
    option_start_with = 0
    option_do_not_randomize = 1
    option_randomize = 2
    default = 0


class VanillaUpgrades(OptionSet):
    """Lock upgrade-item families at their VANILLA locations -- removes them from the randomized
    pool and overrides important_locations for those classes. Replaces the old
    flask_upgrade_option / blessing_option "do not randomize" modes.

      flasks    -- Golden Seeds (flask charges) + Sacred Tears (flask potency) stay vanilla.
      blessings -- Scadutree Fragments + Revered Spirit Ashes stay vanilla (DLC only; ignored off).

    Empty (default) = everything is randomized. To instead FORCE these to hold progression, list
    Seedtree / Church / Fragment / Revered in important_locations (the default already does all 4)."""
    display_name = "Vanilla Upgrades (lock at vanilla)"
    valid_keys = {"flasks", "blessings"}




class DerandomizeQuestlines(Choice):
    """De-randomize long NPC questlines whose chains gate only optional content.

    Their link items are dead-weight 'progression' that crowds the priority/progression
    fill and can drop junk-chain keys onto important locations. Locking the chains at
    vanilla frees the fill and keeps important locations holding real progression.
    Region- and goal-gating quest items are never touched (Drawing-Room Key, Haligtree
    Secret Medallion, Hole-Laden Necklace).

    - **Off:** questlines stay randomized.
    - **Links Only:** lock the chain LINK items at vanilla; reward checks stay randomized
      (good rewards like the Dark Moon Greatsword still appear shuffled). Pure fill relief.
    - **Full:** also pull the good terminal rewards to vanilla and re-inject a shuffled
      copy at the expense of one filler, so they're obtainable without doing the quest.
    See SPEC-questline-derando.md."""
    display_name = "De-randomize NPC Questlines"
    option_off = 0
    option_links_only = 1
    option_full = 2
    default = 0

class ShopChecks(Toggle):  # [shop-checks]
    """Randomize shop slots as AP checks. DEFAULT OFF (shops EXCLUDED) in the pure-runtime
    model: the game world is vanilla, so a randomized shop slot is a blind buy -- you spend
    runes without seeing the AP reward, which is worse UX than no check. With this OFF, shop
    locations drop from the active check set (via _in_location_pool, the same curation lever
    trimmed/lean use) and the shops just sell their vanilla wares.

    Turn this ON to put shop slots back in the randomized pool (legacy behavior). Once shop
    PREVIEWS ship (Option A of SPEC-shop-checks.md -- LocationScouts + ER shop-text hook), this
    should become a DefaultOnToggle (default shops back ON), since a previewed shop is a real
    decision again. See SPEC-shop-checks.md."""
    display_name = "Shop Checks (randomize shop slots -- off = vanilla shops)"

class SoftConsumableShop(Toggle):
    """Sell Stonesword Keys and Dragon Hearts in unlimited supply at the Twin Maiden Husks
    (Roundtable Hold) instead of scattering them through the world.

    They gate imp-statue seals and the Dragon Communion shops but are otherwise 'progression'
    only by classification, which drags them into the priority/progression fill. With this on
    they leave the randomized pool, the key/heart logic gates are satisfied by the always-
    reachable shop, and the latent nokey access gap on those checks is closed. REQUIRES the
    baked Twin Maiden shop rows (patch_baker_soft_consumable_shop) -- don't enable without it."""
    display_name = "Soft-Consumable Shop (Twin Maiden keys/hearts)"

class DerandomizeGurranq(Toggle):
    """De-randomize Gurranq's deathroot ladder -- 10 missable rewards behind a blind cumulative
    deathroot gate. Locks the ladder at vanilla and re-injects the three keepers (Clawmark Seal,
    Beastclaw Greathammer, Ancient Dragon Smithing Stone) into the shuffled pool so the good
    rewards stay obtainable (and stop being missable) while Deathroot leaves the pool. The seven
    mediocre beast incantations/AoW go vanilla. See SPEC-soft-consumables.md."""
    display_name = "De-randomize Gurranq Deathroot Ladder"

class TidyFunConsumables(Toggle):
    """Pull junk 'fun consumables' out of the randomized pool -- progression only by
    classification, gating ~nothing, crowding the priority/progression fill. Festering Bloody
    Fingers (PvP, gate nothing) are skipped; Starlight Shards (Seluvis puppets, needs 3) and
    Seedbed Curses (Dung Eater, needs 5) are start-granted at their required counts so the gated
    checks stay reachable. Reward checks stay shuffled. See SPEC-soft-consumables.md."""
    display_name = "Tidy Junk Consumables (Festering/Starlight/Seedbed)"

class SoftProgression(Toggle):
    """Wiggle room for `accessibility: full`. Demote progression that gates NOTHING in logic --
    upgrade Bell Bearings (smithing/somber/glovewort) and the Progressive Flask of Wondrous Physick
    -- to `useful` when accessibility is strict (full/items). Frees fill slack so the meaningful
    progression lands on important_locations under full, without diluting it (no Bell Bearings on
    your boss drops). No effect under minimal (everything spills there anyway). See SPEC."""
    display_name = "Soft Progression (demote boring progression to useful under full)"

class PoolBuilder(Toggle):
    """Compose the item pool from an all-game priority ladder instead of inheriting whatever
    the included locations natively held. Native LOW-TIER pickups (C/D/F base weapons & armor,
    armor-set non-representative pieces, hand-curated trim junk) are scrubbed from the pool and
    swapped 1:1 for ranked whole-game juice -- S-tier weapons/armor/spells/Ashes of War, top
    spirit ashes, S talismans, glovewort bells, remembrances, crystal tears, capped Memory
    Stones / Talisman Pouches -- then elastic runes + seeds/tears for the remainder. The
    LOCATION always stays a check; only the item on it changes, so the pool size is unchanged.
    Includes armor-set collapse. Made for reduced-scope modes (godrick, legacy-dungeons,
    trimmed) where the native contents are too thin or junk-heavy to be fun. junk_retention
    still seasons in a few deliberate bad checks. Injects BASE-game juice (DLC juice is
    dlc_gear_curation / relevance_uplift's job). See SPEC-pool-builder.md."""
    display_name = "Pool Builder (compose from all-game ladder)"



class ProgressiveFlasks(Toggle):
    """Replace the discrete Golden Seeds and Sacred Tears with two PROGRESSIVE items
    (Progressive Golden Seed = flask charges, Progressive Sacred Tear = flask potency).
    Each received copy grants one seed / tear that you spend at a grace / church; copies
    past the vanilla cap (30 seeds / 12 tears) grant a Lord's Rune instead. Clean single
    names for trackers and trimmed / pool-builder pools. See SPEC-progressive-consumables.md.
    Expects flask_upgrade_option left at 'randomize' so the seeds/tears are in the pool."""
    display_name = "Progressive Flask Upgrades"

class ProgressiveFlaskCount(Range):
    """How many copies of EACH progressive flask item (Progressive Golden Seed = charges,
    Progressive Sacred Tear = potency) to GUARANTEE into a dlc_only pool -- via the same
    count-neutral, filler-funded swap the stone bells use (cheapest junk dropped to fund them).

    dlc_only has few vanilla Golden Seed / Sacred Tear checks, so the normal 1:1 progressive_flasks
    swap barely fires there; this seats a tunable number regardless, and copies past the vanilla cap
    (30 seeds / 12 tears) pay out as Lord's Runes -- the flask analogue of progressive_bell_count.
    0 = off (1:1 swap only). Only matters with progressive_flasks on + dlc_only."""
    display_name = "Progressive Flask Pool Count (dlc_only guarantee)"
    range_start = 0
    range_end = 40
    default = 0

class ProgressiveFlaskEarlyCount(Range):
    """How many copies of EACH progressive flask item (Golden Seed, Sacred Tear) to
    FORCE into sphere-1 (no-item-reachable) locations in dlc_only, via early_items, so
    flask charges and potency ramp up near the start (mirror of progressive_bell_early_count).
    Soft and capped by pool availability + sphere-1 size, so it never fails gen. 0 = no
    early forcing (normal distribution). Only matters when progressive_flasks is on and dlc_only."""
    display_name = "Progressive Flask Early Count"
    range_start = 0
    range_end = 10
    default = 4

class ProgressiveGlovewortBells(Toggle):
    """Replace the 6 discrete Glovewort Picker's Bell Bearings with two PROGRESSIVE items
    (Grave x3, Ghost x3). The Nth copy grants the next bell tier in order (you hand it to
    Roderika to stock that glovewort tier, vanilla). Copies past 3 grant a Lord's Rune.
    Sibling of progressive_stone_bells. See SPEC-progressive-consumables.md."""
    display_name = "Progressive Glovewort Bell Bearings"

class ProgressivePhysick(Toggle):
    """Collapse the Flask of Wondrous Physick + the low-value Crystal tears into ONE
    progressive item. The 1st copy grants the empty flask itself (the physick mechanic,
    earned in logic rather than handed out at spawn); each later copy grants a whole themed
    tear family -- [2] restoratives, [3] elemental Shrouding, [4] Sapping (DLC), [5] resistance
    Knots. The ~18 build-defining tears (Opaline / Thorny / Cerulean Hidden / ...) stay
    individual randomized checks; pure-dup 'Alternate' tears are dropped. Copies past the last
    step grant a Lord's Rune. Supersedes the start-flask grant of bell_physick (the Spirit
    Calling Bell still follows that option). See SPEC-progressive-physick.md."""
    display_name = "Progressive Flask of Wondrous Physick"

class ProgressivePhysickCount(Range):
    """How many copies of the Progressive Flask of Wondrous Physick to GUARANTEE into a dlc_only
    pool, via the same count-neutral, filler-funded swap the stone bells / flasks use.

    Physick is a SINGLE ladder (~5 steps: flask -> restoratives -> Shrouding -> Sapping(DLC) ->
    Knots), so keep this LOW -- copies past the ladder length just pay out as Lord's Runes. Additive
    to the normal injectable seating. 0 = off. Only matters with progressive_physick on + dlc_only."""
    display_name = "Progressive Physick Pool Count (dlc_only guarantee)"
    range_start = 0
    range_end = 40
    default = 0

class TorrentStart(Choice):
    """Whether the Spectral Steed Whistle (Torrent) is granted at the start -- decoupled from
    the flask/bell start grant into its own knob.

    - **Auto (default):** grant Torrent at start when the normal Melina hand-off is bypassed,
      i.e. when bell_physick is start_with OR progressive_physick is on. Preserves the prior
      behaviour.
    - **On:** always grant Torrent at start.
    - **Off:** never grant it at start (meet Melina the vanilla way). Early Leveling still
      force-grants Torrent regardless, since it suppresses her hand-off (flag 951)."""
    display_name = "Torrent at Start"
    option_auto = 0
    option_on = 1
    option_off = 2
    default = 0

class NoSpiritAshes(Toggle):
    """Remove spirit summons from the run entirely. Every Spirit Ash / summon (generic and
    named legends alike) and the Spirit Calling Bell are dropped from the item pool -- their
    locations stay randomized checks, backfilled with filler. Under bell_physick: start_with
    the bell is also not granted at start. The pool builder skips its top-spirit injection too.
    Use when you don't want to engage the summon system at all. The two vanilla checks that
    require a summon mechanic to reach become unreachable (fine under accessibility: minimal)."""
    display_name = "No Spirit Ashes"

class LocationPool(Choice):
    """How many locations are randomized checks -- controls your footprint in a multiworld.

    - **All:** every pickup (~3900). Big slice of the pool; lots of far-flung filler checks.
    - **Trimmed:** drops low-value filler pickups (golden runes, consumables, materials,
      cookbooks); keeps gear, upgrades, and all key/boss/important checks (~2150).
    - **Lean:** only meaningful checks -- boss drops, key items, remembrances, flask upgrades
      (seeds/tears), DLC blessings, plus anything holding a progression item (~500).
      Recommended for multiworld syncs.
    """
    display_name = "Location Pool Size"
    option_all = 0
    option_trimmed = 1
    option_lean = 2
    default = 0


class DLCGearCuration(Toggle):
    """Curate the gear pool: drop bad base-game weapons/armor, and (with the DLC) bring in the best DLC gear.

    When on, every base-game weapon/armor piece rated C-tier or below (mediocre /
    weak / joke gear) is removed from the item pool -- its location stays a randomized
    check, but the junk no longer spreads. If Enable DLC is also on, the freed slots
    are backfilled with one extra copy each of the best (S/A-tier) DLC weapons and
    armor, so you receive top-tier Shadow-of-the-Erdtree gear instead of vendor trash.
    With the DLC off (or once the DLC gear is exhausted), the freed slots fall back to
    normal filler. Tiers come from the bundled PvE tier list.
    """
    display_name = "DLC Gear Curation"


class FillerReplacement(Choice):
    """Replace leftover junk / low-value filler in the item pool with worthwhile economy items.

    The DLC-only and curated pools leave a few hundred 'filler' slots that would otherwise
    hold vendor-trash crafting mats, cookbooks and tiny rune drops. This swaps EVERY
    filler-classified item in the pool (both the throwaway pads and the low-value game
    items) for something useful, keeping the same pool size and filler classification so
    fill / progression-balancing are unaffected -- only the content of the junk slots changes.

    - **Off:** Vanilla behaviour -- filler stays as the usual junk goods.
    - **Runes:** Every filler slot becomes a Golden Rune (mid-to-high value). Pure money /
      leveling boost; no interaction with auto_upgrade.
    - **Stones And Runes:** Filler becomes a mix of Smithing / Somber Smithing Stones (spread
      across tiers) and Golden Runes. Best for an upgrade-hungry DLC run; intended for
      auto_upgrade OFF (with auto_upgrade on, received gear is already maxed, so the stones
      are wasted -- use Runes instead).
    """
    display_name = "Filler Replacement"
    option_off = 0
    option_runes = 1
    option_stones_and_runes = 2
    default = 0


class JunkRetention(Range):
    """Keep a fraction of deliberately-bad "comedy junk" as real checks instead of scrubbing
    every junk slot into something good.

    Bad checks are part of the spirit of Archipelago -- opening a chest and getting throwable
    excrement is a real (funny) outcome. This is the percent of the junk items present in the
    pool to SPARE from the curation scrub, drawn (comedy-first) from a curated funny/gross
    list (the Excrement trio, Soiled Loincloth, Toxic Mushroom, Ash of War: No Skill / Kick,
    ...). See Junk Retention Style for what counts as sparable junk.

    Count-neutral: a spared item just occupies a slot a rune / uplift item would otherwise
    fill. Only does anything when a scrub path is active (Filler Replacement, or the dlc_only
    relevance uplift); with no scrub, this junk already stays in the pool naturally.

    0 = scrub everything (vanilla). 12 (default) = a light seasoning of junk.
    """
    display_name = "Junk Retention"
    range_start = 0
    range_end = 100
    default = 12


class JunkRetentionStyle(Choice):
    """What counts as sparable junk for Junk Retention.

    - **Comedy:** spare only the curated COMEDY_JUNK list (funny/gross items). Default.
    - **Comedy And Generic:** comedy first, plus a small sprinkle of generic D/F-tier filler
      (~30% of the comedy budget) so the junk isn't always the *same* joke items.
    - **Uniform:** no comedy preference -- spare from all D/F-tier filler equally.
    """
    display_name = "Junk Retention Style"
    option_comedy = 0
    option_comedy_and_generic = 1
    option_uniform = 2
    default = 0


class RandomizeEnia(DefaultOnToggle):
    """Randomize the Roundtable / Enia (Finger Reader) slots -- Remembrance turn-ins and the
    remembrance-boss gear shop. ON (default): those are AP checks. OFF: leave Enia vanilla
    (turn in a Remembrance -> that boss's weapon, 1:1; gear sold normally), removing ~30+
    'checks with extra steps'. The slots become locked-vanilla and the item pool shrinks to match."""
    display_name = "Randomize Enia (Remembrance shop)"

class RandomStartRegion(Choice):
    """Roll a random overworld region to start in instead of Limgrave / The First Step. The chosen
    region becomes the free sphere-1 hub: its lock is pre-collected (so it joins sphere 1 under the
    Limgrave-rooted warp graph), and its grace bundle + map reveal + open flag fire at load. Requires
    a lock-based world_logic (region_lock / region_lock_bosses); forces region_access=warp. Inert
    under dlc_only (Gravesite is already the fixed hub) and under any region-seal goal
    (capital/region_count/messmer/godrick) for now.

    - off:        vanilla -- start at The First Step (Limgrave).
    - overworld:  roll among the overworld majors (Weeping, Liurnia, Caelid, Altus) -- each has a
                  clean warp grace + map piece. Safest.
    - any_major:  any region with a grace bundle + lock. Spicier; some lack a map pillar."""
    display_name = "Random Starting Region"
    option_off = 0
    option_overworld = 1
    option_any_major = 2
    default = 0

class StartRegionFreebie(Choice):
    """How much comes free with the rolled start region. The start region is always reachable with
    zero items (its lock is pre-collected); this controls whether Limgrave (Roundtable / early
    services / Torrent hand-off area) is also lit at load.

    - hub_only:    just the start region's graces + open flag.
    - to_limgrave: also light Limgrave's start graces so services are never stranded behind a lock
                   you happened not to start near (recommended)."""
    display_name = "Start Region Freebie"
    option_hub_only = 0
    option_to_limgrave = 1
    default = 1

class CompletionScaling(Choice):
    """Reshape Elden Ring's difficulty curve by seed-completion order rather than leave it vanilla.
    The baker re-scales every enemy from its native (geographic = completion-order) tier along the
    chosen curve. Inspired by FogMod's fog-gate-depth scaling. Runs with OR without enemy_rando -- a scale-only bake pass applies it when enemy rando is off.

    - off:    vanilla scaling.
    - flat:   identity (same as vanilla; confirms the pipeline ran).
    - gentle: convex -- easier for longer, difficulty concentrated late.
    - steep:  concave -- difficulty climbs fast, mid-game already punishing.
    - smoothstep: S-curve -- gentle early on-ramp, steep mid-game, plateau into the cap."""
    display_name = "Completion Scaling"
    option_off = 0
    option_flat = 1
    option_gentle = 2
    option_steep = 3
    option_smoothstep = 4
    default = 0

class CompletionScalingFloor(Range):
    """Minimum scaling tier as a PERCENT of the baker's MaxTier (0 = earliest tier can stay 1;
    25 = nothing below ~a quarter of the curve). Only with completion_scaling on."""
    display_name = "Completion Scaling Floor (% of MaxTier)"
    range_start = 0
    range_end = 50
    default = 0

class CompletionScalingBasis(Choice):
    """How completion_scaling orders the tiers.
    - geographic: by each enemy's native (vanilla) area tier. Start-UNAWARE -- a random start still
      fights softened-but-mid-game enemies. Cheap; the v1 default.
    - sphere: by each REGION's Archipelago fill SPHERE, so your rolled start region is sphere 1
      (tier 1) and difficulty climbs with YOUR progression, not geography. Needs the baker bridge
      (SPEC-sphere-ordered-scaling.md) to actually apply; the apworld emits the table + ER_SPHERE_TIERS.txt
      either way for inspection."""
    display_name = "Completion Scaling Basis"
    option_geographic = 0
    option_sphere = 1
    default = 0

class GlobalScadutreeBlessing(Choice):
    """EXPERIMENTAL (default off). Turn Scadutree Fragments into a GAME-WIDE power curve.
    The runtime client counts how many Scadutree Fragments you hold, converts that to a
    Scadutree Blessing level via the vanilla cost curve, and writes the game's stored blessing
    level so the DLC blessing buff applies ANYWHERE -- not just the Land of Shadow. See
    SPEC-global-scadutree-blessing.md.

    - off:         vanilla. Fragments do nothing outside the DLC.
    - player_only: apply the player blessing globally (enemies untouched). Power fantasy /
                   accessibility knob.
    - scaled:      same player apply; intended to pair with completion_scaling lifted into the
                   DLC enemy-tier band (enemy side is a separate, later baker change). On the
                   client this currently behaves like player_only; the value is shipped so
                   seeds can opt in ahead of the enemy-side work."""
    display_name = "Global Scadutree Blessing"
    option_off = 0
    option_player_only = 1
    option_scaled = 2
    default = 0

@dataclass
class EROptions(PerGameCommonOptions):
    ending_condition: EndingCondition
    world_logic: WorldLogic
    region_boss_percent: RegionBossPercent
    soft_logic: RegionSoftLogic
    great_runes_required: GreatRunesRequired
    great_runes_final_boss: GreatRunesFinalBoss
    great_runes_mountaintops: GreatRunesMountaintops
    deathless_routing: DeathlessRouting
    graces_per_region: GracesPerRegion
    grace_rando: GraceRando
    region_access: RegionAccessLogic
    num_regions: NumRegions
    num_regions_order: NumRegionsOrder
    num_regions_rune_source: NumRegionsRuneSource
    num_regions_chain: NumRegionsChain
    dlc_only_chain: DLCOnlyChain
    completion_scaling: CompletionScaling
    completion_scaling_floor: CompletionScalingFloor
    completion_scaling_basis: CompletionScalingBasis
    global_scadutree_blessing: GlobalScadutreeBlessing
    random_start_region: RandomStartRegion
    start_region_freebie: StartRegionFreebie
    royal_access: RoyalAccess
    early_leveling: EarlyLeveling
    extra_region_locks: ExtraRegionLocks
    enable_dlc: EnableDLC
    dlc_only: DLCOnly
    quick_start: QuickStart
    dlc_only_rune_catchup: DLCOnlyRuneCatchup
    scadu_frontload: ScadutreeFrontload
    messmer_kindle: MessmerKindle
    messmer_kindle_required: MessmerKindleRequired
    messmer_kindle_max: MessmerKindleMax
    dlc_timing: DLCTimingOption
    enemy_rando: EnemyRando
    material_rando: MaterialRando
    death_link: DeathLink

    random_start: RandomizeStartingLoadout
    auto_equip: AutoEquipOption
    auto_upgrade: AutoUpgradeOption
    progressive_items: ProgressiveItems
    progressive_stone_bells: ProgressiveStoneBells
    progressive_bell_count: ProgressiveBellCount
    progressive_bell_early_count: ProgressiveBellEarlyCount
    progressive_physick: ProgressivePhysick
    progressive_physick_count: ProgressivePhysickCount

    crafting_kit_option: CraftingKitOption
    randomize_enia: RandomizeEnia
    map_option: MapOption
    smithing_bell_bearing_option: SmithingBellBearingOption
    merchant_bell_logic: MerchantBellLogic
    spell_shop_spells_only: SpellShopSpellsOnly
    early_legacy_dungeons:EarlyLegacyDungeonsEarly
    local_item_option: LocalItemOnly
    exclude_local_item_only: ExcludeLocalItemOnly
    important_locations: ERImportantLocations
    exclude_locations: ERExcludeLocations
    excluded_location_behavior: ExcludedLocationBehaviorOption
    missable_location_behavior: MissableLocationBehaviorOption
    dungeon_sweep: DungeonSweep
    grace_sweep: GraceSweep
    no_weapon_requirements: NoWeaponRequirements
    swap_multiboss: SwapMultiBoss
    boss_runes_match: BossRunesMatchOriginal
    impolite_enemies: ImpoliteEnemies
    disable_serpent_hunter_upgrade: DisableSerpentHunterUpgrade
    bell_physick_option: BellPhysickOption
    torrent_start: TorrentStart
    vanilla_upgrades: VanillaUpgrades
    soft_progression: SoftProgression
    tidy_fun_consumables: TidyFunConsumables
    soft_consumable_shop: SoftConsumableShop
    shop_checks: ShopChecks  # [shop-checks]
    derandomize_gurranq: DerandomizeGurranq
    derandomize_questlines: DerandomizeQuestlines
    location_pool: LocationPool
    dlc_gear_curation: DLCGearCuration
    junk_retention: JunkRetention
    junk_retention_style: JunkRetentionStyle
    filler_replacement: FillerReplacement
    no_spirit_ashes: NoSpiritAshes
    progressive_flasks: ProgressiveFlasks
    progressive_flask_early_count: ProgressiveFlaskEarlyCount
    progressive_flask_count: ProgressiveFlaskCount
    progressive_glovewort_bells: ProgressiveGlovewortBells
    pool_builder: PoolBuilder

# option_groups: progressive_items merge by patch_apworld_progressive_items_options -- see docs/er/SPEC-options-consolidation.md
option_groups = [
    OptionGroup("Goal & World Logic", [
        EndingCondition,
        WorldLogic,
        RegionBossPercent,
        RegionSoftLogic,
        RegionAccessLogic,
        ExtraRegionLocks,
    ]),
    OptionGroup("Great Runes", [
        GreatRunesRequired,
        GreatRunesFinalBoss,
        GreatRunesMountaintops,
    ]),
    OptionGroup("Short Runs (Capital)", [
        GracesPerRegion,
        NumRegions,
        NumRegionsOrder,
        NumRegionsRuneSource,
        NumRegionsChain,
    ]),
    OptionGroup("Start", [
        RandomStartRegion,
        StartRegionFreebie,
        EarlyLeveling,
        RandomizeStartingLoadout,
        TorrentStart,
    ]),
    OptionGroup("DLC", [
        EnableDLC,
        DLCOnly,
        DLCTimingOption,
        ScadutreeFrontload,
        MessmerKindle,
        MessmerKindleRequired,
        MessmerKindleMax,
    ]),
    OptionGroup("DLC-Only Catch-up", [
        QuickStart,
        DLCOnlyRuneCatchup,
    ]),
    OptionGroup("Pool & Curation", [
        LocationPool,
        PoolBuilder,
        DLCGearCuration,
        FillerReplacement,
        JunkRetention,
        JunkRetentionStyle,
        TidyFunConsumables,
        SoftConsumableShop,
        ShopChecks,  # [shop-checks]
        DerandomizeGurranq,
        DerandomizeQuestlines,
        SoftProgression,
        NoSpiritAshes,
        RandomizeEnia,
    ]),
    OptionGroup("Progressive Items", [
        ProgressiveItems,
        ProgressiveBellCount,
        ProgressiveBellEarlyCount,
        ProgressivePhysickCount,
        ProgressiveFlaskEarlyCount,
        ProgressiveFlaskCount,
    ]),
    OptionGroup("Fill Priority", [
        ERImportantLocations,
        ERExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
        VanillaUpgrades,
        MerchantBellLogic,
        LocalItemOnly,
        ExcludeLocalItemOnly,
    ]),
    OptionGroup("Sweep", [
        DungeonSweep,
        GraceSweep,
    ]),
    OptionGroup("Enemy Randomizer", [
        EnemyRando,
        SwapMultiBoss,
        BossRunesMatchOriginal,
        ImpoliteEnemies,
        CompletionScaling,
        CompletionScalingFloor,
    ]),
    OptionGroup("Equipment & QoL", [
        AutoEquipOption,
        AutoUpgradeOption,
        NoWeaponRequirements,
        CraftingKitOption,
        MapOption,
        SmithingBellBearingOption,
        SpellShopSpellsOnly,
        EarlyLegacyDungeonsEarly,
        MaterialRando,
        BellPhysickOption,
        DeathLink,
    ]),
    OptionGroup("Superseded (use progressive_items)", [
        ProgressiveStoneBells,
        ProgressiveGlovewortBells,
        ProgressiveFlasks,
        ProgressivePhysick,
    ], start_collapsed=True),
    OptionGroup("Advanced & Experimental", [
        GlobalScadutreeBlessing,
        CompletionScalingBasis,
        DeathlessRouting,
        RoyalAccess,
        DisableSerpentHunterUpgrade,
    ], start_collapsed=True),
]
