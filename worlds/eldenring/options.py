from dataclasses import dataclass
import json
from typing import Any, Dict

from Options import Choice, DeathLink, DefaultOnToggle, ExcludeLocations, OptionList, OptionDict, \
    OptionGroup, OptionSet, PerGameCommonOptions, Range, Toggle, OptionError, Visibility
    
from .bosses import all_bosses

# MARK: Game Options

class GoalOption(OptionSet):
    """Which bosses must be defeated in order to win the game, of the form "<Region> Boss".

    If multiple bosses are selected, all of them must be defeated in order to
    achieve your goal. By default, only "Final Boss" and "DLC Final Boss" is
    selected.
    """
    display_name = "Goal"
    valid_keys = {type + " Boss" for boss in all_bosses if boss.flag for type in boss.type}
    default = frozenset({"Final Boss", "DLC Final Boss"})
    
    visibility = Visibility.none # for now so fuzzer doesn't complain about game being unbeatable

    def verify_keys(self) -> None:
        super().verify_keys()
        if not set(self.value): raise OptionError("You must set at least one Goal.")
        
class ExcludeDungeonBosses(DefaultOnToggle):
    "Exclude dungeon bosses from Goal. ex: Catacomb and Cave bosses, not Siofra River bosses"
    display_name = "Exclude Dungeon Bosses"

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

class StoneswordMasterKey(Toggle):
    "Replace Stonesword Keys with a Master Key for each region"
    display_name = "Stonesword Master Key"

# MARK: DLC

class EnableDLC(Toggle):
    """Enable DLC"""
    display_name = "Enable DLC"

class DLCRandomization(Choice):
    """How to randomize DLC items.
    
    - **Together:** Randomize base and DLC together.
    - **Separately:** Randomize DLC items to DLC locations or other worlds.
    """
    display_name = "DLC Randomization"
    option_together = 0
    option_separately = 1
    default = 0
    
    visibility = Visibility.none # for now so fuzzer doesn't complain
    
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
    
class DLCMessmerKindle(Toggle):
    """Randomize Messmer's Kindling and Shards to DLC or other worlds."""
    display_name = "DLC Messmer's Kindling"
    
class DLCScadutreeFragments(Toggle):
    """Randomize Scadutree Fragments to DLC or other worlds."""
    display_name = "DLC Scadutree Fragments"

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
    
class DLCMaxLevelWeapons(Toggle):
    """Upgrade all weapons to max level in the DLC."""
    display_name = "DLC Max Level Weapons"
    
class DLCAbyssalTorrent(Toggle):
    """Prevent Torrent from getting frightened."""
    display_name = "DLC Abyssal Torrent"
    
# randomizing spiritspring seals would mean making a location for the seals
    
# MARK: DLC Start

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
    
class DLCStartingItems(OptionList):
    """Choose what base game items to start with in DLC Start.
    If there is no access to base game, items not started with will be randomized into the DLC.
    
    - **Sacred Tears**
    - **Golden Seeds**
    - **Talisman Pouches**
    - **Memory Stones**
    - **Whetblades**
    - **Upgrade Bell Bearings**"""
    display_name = "DLC Starting Items"
    supports_weighting = False
    default = ["Talisman Pouches", "Whetblades"]

    valid_keys = ["sacred tears", "golden seeds", "talisman pouches", 
                  "memory stones", "whetblades", "upgrade bell bearings"]
    valid_keys_casefold = True

class DLCStartingShop(Toggle): # just the static rando option
    """Add a shop at grace with all base game equipment for free."""
    display_name = "DLC Starting Shop"
    
class DLCCarePackage(Toggle): # just the static rando option
    """Start with 80 extra base game items."""
    display_name = "DLC Care Package"
    
class DLCInitialRuneLevel(Choice): # just the static rando option
    """Runes are given to level up at start."""
    display_name = "DLC Initial Rune Level"
    option_0 = 0
    option_30 = 30
    option_60 = 60
    option_90 = 90
    option_120 = 120
    option_150 = 150
    option_200 = 200
    default = 0
    
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
    - **Early:** Make it anywhere before Altus and not in Caelid, if DLC Only it'll be in Gravesite Plain.
    - **Do Not Randomize:** Leave it at its normal spot, if DLC Only is on it'll be in Roundtable Twin Maiden Shop.
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
    - **Do Not Randomize:** Leave them at their normal spots.
    """
    display_name = "Map Behavior"
    option_randomize = 0
    option_give = 1
    option_do_not_randomize = 2
    default = 1
    
class SmithingBellBearingOption(Choice):
    """Choose how smithing stone bell bearings are handled.
    This doesn't work with dlc only, add them to starting inventory or they get randomized.

    - **Randomize:** Can be anywhere.
    - **Progression Randomize:** Make them a progression item, and be required for the area after they would normally be in and for DLC.
    - **Do Not Randomize:** Leave them at their normal spots.
    """
    display_name = "Smithing Bell Bearing Behavior"
    option_randomize = 0
    option_progression_randomize = 1
    option_do_not_randomize = 2
    default = 1
    
class SmoothUpgradeItems(Toggle):
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
    valid_keys = ["weapon", "armor", "accessory", "ashofwar", "goods"]
    valid_keys_casefold = True
    
class ERPriorityLocationGroups(OptionList):
    """Prevent these location types from having an unimportant items.
    
    - *Remembrance*: Main boss Remembrances.
    - *Seedtree*: Golden Seed trees.
    - *Basin*: Basins that contain tears.
    - *Church*: Sacred Tears.
    - *Map*: Map pillars.
    - *Fragment*: Scadu Fragments.
    - *Cross*: All cross items.
    - *Revered*: Revered Spirit Ashes.
    - *KeyItem*: Key items.
    - *Bosses*: All goal bosses.
    - *Overworld Bosses*: All overworld goal bosses.
    """
    display_name = "Priority Location Groups"
    default = ["Remembrance", "Seedtree", "Map", "Church", "Cross", "Overworld Bosses"]
    valid_keys = ["remembrance", "seedtree", "basin", "church", "map", 
                           "fragment", "cross", "revered", "keyitem", "bosses", "overworld bosses"]
    valid_keys_casefold = True
    
class ERImportantAtPriorityOnly(Toggle):
    """Should important items be only at priority locations.
    If the total amount of priority checks are low there will be like 20 items on each location."""
    display_name = "Important at Priority Only"
    
class FlaskUpgradesAtPriority(Toggle):
    "Should flask upgrades be randomized to important locations."
    display_name = "Flask Upgrades at Priority"
    
class ScaduAtPriority(Toggle):
    "Should scadu fragments be randomized to important locations."
    display_name = "Scadutree Fragments at Priority"

class ERExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important items.
    - **dlc**: If you want DLC items but dont wanna do DLC.
    - **hidden**: Hard to find items.
    - **blizzard**: The hard to see area of snowfield."""
    default = frozenset({}) # idk how ds3 does this, it just errors
    # valid_keys = ["dlc", "hidden", "blizzard"]
    # valid_keys_casefold = True

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
    goal: GoalOption
    exclude_dungeon: ExcludeDungeonBosses
    world_logic: WorldLogic
    region_boss_percent: RegionBossPercent
    region_boss_type: RegionBossType
    soft_logic: RegionSoftLogic
    great_runes_required_leyndell: GreatRunesRequiredLeyndell
    great_runes_required_mountain: GreatRunesRequiredMountain
    royal_access: RoyalAccess
    use_master_key: StoneswordMasterKey
    
    enable_dlc: EnableDLC
    dlc_start: DLCStart
    dlc_starting_items: DLCStartingItems
    dlc_starting_shop: DLCStartingShop
    dlc_care_package: DLCCarePackage
    dlc_initial_rune_level: DLCInitialRuneLevel
    dlc_randomization: DLCRandomization
    messmer_kindle: MessmerKindle
    messmer_kindle_required: MessmerKindleRequired
    messmer_kindle_max: MessmerKindleMax
    dlc_messmer_kindle: DLCMessmerKindle
    dlc_scadutree_fragments: DLCScadutreeFragments
    dlc_timing: DLCTimingOption
    dlc_max_level_weapons: DLCMaxLevelWeapons
    dlc_abyssal_torrent: DLCAbyssalTorrent
    
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
    priority_location_groups: ERPriorityLocationGroups
    important_at_priority_only: ERImportantAtPriorityOnly
    flask_at_priority: FlaskUpgradesAtPriority
    scadu_at_priority: ScaduAtPriority
    exclude_locations: ERExcludeLocations
    excluded_location_behavior: ExcludedLocationBehaviorOption
    missable_location_behavior: MissableLocationBehaviorOption

option_groups = [
    OptionGroup("Logic", [
        GoalOption,
        ExcludeDungeonBosses,
        WorldLogic,
        RegionBossPercent,
        RegionBossType,
        RegionSoftLogic,
        GreatRunesRequiredLeyndell,
        GreatRunesRequiredMountain,
        RoyalAccess,
        StoneswordMasterKey,
    ]),
    OptionGroup("Equipment", [
        RandomizeStartingLoadout,
        AutoEquipOption,
    ]),
    OptionGroup("DLC", [
        EnableDLC,
        DLCRandomization,
        MessmerKindle,
        MessmerKindleRequired,
        MessmerKindleMax,
        DLCMessmerKindle,
        DLCScadutreeFragments,
        DLCTimingOption,
        DLCMaxLevelWeapons,
        DLCAbyssalTorrent,
    ]),
    OptionGroup("DLC Start", [
        DLCStart,
        DLCStartingItems,
        DLCStartingShop,
        DLCCarePackage,
        DLCInitialRuneLevel,
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
        ERExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ]),
    OptionGroup("Priority Location Rules", [
        ERPriorityLocationGroups,
        ERImportantAtPriorityOnly,
        FlaskUpgradesAtPriority,
        ScaduAtPriority,
    ])
]
