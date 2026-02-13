from dataclasses import dataclass

from Options import Choice, DeathLink, DefaultOnToggle, ExcludeLocations, OptionList, \
    OptionGroup, PerGameCommonOptions, Range, Toggle

# MARK: Game Options

class EndingCondition(Choice):
    """Ending Condition options
    
    **Final Boss:** Will be Elden Beast, or Consort if DLC is enabled.
    **Elden Beast:** Kill Elden Beast, for short runs with DLC on.
    **All Remembrances:** All remembrance bosses, missable ones excluded.
    **All Bosses:** All bosses, missable ones excluded.
    If DLC is on those bosses / remembrances are included."""
    display_name = "Ending Condition"  # this is the option name as it's displayed to the user on the webhost and in the spoiler log
    option_final_boss = 0
    option_elden_beast = 1
    option_all_remembrances = 2
    option_all_bosses = 3

class WorldLogic(Choice):
    """World Logic options
    
    **Region Lock:** Each region will require a 'Special item'.
    **Region Bosses:** Each region will require % of bosses in that region to be defeated.
    **Region Lock Bosses:** Each region will require % of bosses in that region to be defeated and a 'Special item'.
    **Open World:** No region locking."""
    display_name = "World Logic"
    option_region_lock = 0
    option_region_bosses = 1
    option_region_lock_bosses = 2
    option_open_world = 3
    default = 0
    
class RegionBossPercent(Range):
    """The % of bosses in a region to unlock the next."""
    display_name = "Region Boss Percent"
    range_start = 1
    range_end = 100
    default = 50
    
class RegionBossType(Toggle):
    """Remove cave and catacombs type bosses from region bosses."""
    display_name = "Region Boss Type"
    
class RegionSoftLogic(DefaultOnToggle):
    """Region Soft Logic
    
    You might get early caelid access but you won't be expected to go there early.
    """
    display_name = "Region Soft Logic"

class GreatRunesRequiredLeyndell(Range):
    """How many great runes are required to enter Leyndell."""
    display_name = "Leyndell Great Runes Required"
    range_start = 0
    range_end = 7
    default = 2
    
class GreatRunesRequiredMountain(Range):
    """How many great runes are required to enter Mountaintops.
    If greater than 0 Rold Medallion is not required."""
    display_name = "Mountaintops Great Runes Required"
    range_start = 0
    range_end = 7
    default = 0
    
class RoyalAccess(Toggle):
    """Keep Royal Capital graces accessable after it becomes ashen."""
    display_name = "Royal Capital Accessable"

# MARK: DLC

class EnableDLC(Toggle):
    """Enable DLC"""
    display_name = "Enable DLC"
    
class DLCStart(Choice):
    """Where the run starts.
    
    - **Normal:** Start in Limgrave.
    - **DLC Start:** Start in Gravesite Plain, with no access to base game.
    - **DLC Start With Base:** Start in Gravesite Plain with access to base game.
    """
    display_name = "DLC Start"
    option_normal = 0
    option_dlc_start = 1
    option_dlc_start_with_base = 2
    default = 0
    
class DLCRandomization(Choice):
    """How to randomize dlc items.
    
    - **Together:** Randomize base and dlc together.
    - **Separately:** Randomize dlc items to dlc locations.
    """
    display_name = "DLC Randomization"
    option_together = 0
    option_separately = 1
    default = 0
    
class MessmerKindle(Toggle): # another toggle to make them only spawn in dlc?
    """Messmer Kindle Shards"""
    display_name = "Messmer Kindle Shards"
    
class MessmerKindleRequired(Range): # i just picked these numbers idk how many would be good
    """Messmer Kindle Shards required to access Enir Ilim."""
    display_name = "Messmer Kindle Shards Required"
    range_start = 2
    range_end = 20
    default = 5
    
class MessmerKindleMax(Range):
    """How many Messmer Kindle Shards there are."""
    display_name = "Messmer Kindle Shards Max"
    range_start = 2
    range_end = 20
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
    
# MARK: Other Rando
    
class EnemyRando(Toggle):
    """Randomizes the enemies."""
    display_name = "Enemy Randomizer"

class MaterialRando(DefaultOnToggle):
    """Randomizes the indefinitely spawning materials."""
    display_name = "Material Randomizer"

# MARK: Item & Location

class RandomizeStartingLoadout(DefaultOnToggle):
    """Randomizes the equipment characters begin with."""
    display_name = "Randomize Starting Loadout"

class AutoEquipOption(Toggle):
    """Automatically equips any received armor or left/right weapons."""
    display_name = "Auto-Equip"
    
class AutoUpgradeOption(Toggle):
    """Automatically upgrades any received weapons to highest upgraded level."""
    display_name = "Auto-Upgrade"
    
class CraftingKitOption(Choice):
    """Choose how the Crafting Kit is handled.

    - **Randomize:** Can be anywhere.
    - **Early:** Make it anywhere before Altus and not in Caelid.
    - **Do Not Randomize:** Leave it at its normal spot.
    """
    display_name = "Crafting Kit Behavior"
    option_randomize = 0
    option_early = 1
    option_do_not_randomize = 2
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
    
class SmoothUpgradeItems(Toggle): # these fail, Exception: ER bug: there are 518 locations that can contain smoothed items, but only 491 items to smooth.
    """Smooth Upgrade Items."""
    display_name = "Smooth Upgrade Items"
    
class SmoothRuneItems(Toggle):
    """Smooth Rune Items."""
    display_name = "Smooth Rune Items"
    
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
    
    The *total* amount of priority checks should be below:
    - **Vanilla**: [90] 
    - **DLC**: [120]
    """
    display_name = "Important Locations"
    default = ["Remembrance", "Seedtree", "Map"]
    valid_keys_casefold = ["Remembrance", "Seedtree", "Basin", "Church", "Map", "Fragment", "Cross", "Revered", "KeyItem"]

class ERExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important items.
    - **dlc**: If you want DLC items but dont wanna do DLC.
    - **hidden**: Hard to find items.
    - **blizzard**: The hard to see area of snowfield."""
    default = frozenset({}) # still errors
    # Exception: Location 'hidden' from option 'ERExcludeLocations(hidden)' is not a valid location name from 'EldenRing'. Did you mean 'RH: Mace - Twin maiden shop' (18% sure)
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

@dataclass
class EROptions(PerGameCommonOptions):
    ending_condition: EndingCondition
    world_logic: WorldLogic
    region_boss_percent: RegionBossPercent
    region_boss_type: RegionBossType
    soft_logic: RegionSoftLogic
    great_runes_required_leyndell: GreatRunesRequiredLeyndell
    great_runes_required_mountain: GreatRunesRequiredMountain
    royal_access: RoyalAccess
    
    enable_dlc: EnableDLC
    dlc_start: DLCStart
    dlc_randomization: DLCRandomization
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
    
    crafting_kit_option: CraftingKitOption
    map_option: MapOption
    smithing_bell_bearing_option: SmithingBellBearingOption
    smooth_upgrade_items: SmoothUpgradeItems
    smooth_rune_items: SmoothRuneItems
    spell_shop_spells_only: SpellShopSpellsOnly
    early_legacy_dungeons:EarlyLegacyDungeonsEarly
    local_item_option: LocalItemOnly
    exclude_local_item_only: ExcludeLocalItemOnly
    important_locations: ERImportantLocations
    exclude_locations: ERExcludeLocations
    excluded_location_behavior: ExcludedLocationBehaviorOption
    missable_location_behavior: MissableLocationBehaviorOption

option_groups = [
    OptionGroup("Logic", [
        EndingCondition,
        WorldLogic,
        RegionBossPercent,
        RegionBossType,
        RegionSoftLogic,
        GreatRunesRequiredLeyndell,
        GreatRunesRequiredMountain,
        RoyalAccess,
    ]),
    OptionGroup("Equipment", [
        RandomizeStartingLoadout,
        AutoEquipOption,
    ]),
    OptionGroup("DLC", [
        EnableDLC,
        DLCStart,
        DLCRandomization,
        MessmerKindle,
        MessmerKindleRequired,
        MessmerKindleMax,
        DLCTimingOption
    ]),
    OptionGroup("Item & Location Options", [
        CraftingKitOption,
        MapOption,
        SmithingBellBearingOption,
        SmoothUpgradeItems,
        SmoothRuneItems,
        SpellShopSpellsOnly,
        EarlyLegacyDungeonsEarly,
        LocalItemOnly,
        ExcludeLocalItemOnly,
        ERImportantLocations,
        ERExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ])
]
