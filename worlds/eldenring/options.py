from dataclasses import dataclass
import json
from typing import Any, Dict

from Options import Choice, DeathLink, DefaultOnToggle, PriorityLocations, ExcludeLocations, OptionList, OptionDict, \
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
    default = 3
    # visibility = Visibility.none
    
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
    """You will always get Altus access before needing to go to Caelid."""
    display_name = "Region Soft Logic"

class GreatRunesRequiredLeyndell(Range):
    """How many great runes are required to enter Leyndell."""
    display_name = "Leyndell Great Runes Required"
    range_start = 0
    range_end = 7
    default = 2
    
class GreatRunesRequiredMountain(Range):
    """What is required to enter Mountaintops.

    - **Vanilla:** Rold Medallion is required.
    - **0-7:** Rold Medallion is not required; require this many Great Runes instead."""
    display_name = "Mountaintops Great Runes Required"
    range_start = -1
    range_end = 7
    default = -1
    
class GreatRunesRequiredErdtree(Range):
    """How many great runes are required to access the Erdtree."""
    display_name = "Erdtree Great Runes Required"
    range_start = 0
    range_end = 7
    default = 0
    
class RoyalAccess(Toggle):
    """Keep Royal Capital graces accessable after it becomes ashen."""
    display_name = "Royal Capital Accessable"

class StoneswordMasterKey(Choice):
    """Stonesword Key options
    
    **Regional Key:** Adds an individual Master Key for each region.
    **Single Key:** Adds a Single Master Key.
    """
    display_name = "Stonesword Master Key"
    option_vanilla = 0
    option_regional_keys = 1
    option_single_key = 2

# MARK: DLC

class EnableDLC(Toggle):
    """Enable DLC"""
    display_name = "Enable DLC"
    
class MessmerKindle(Toggle):
    """Messmer Kindle Shards"""
    display_name = "Messmer Kindle Shards"
    
class MessmerKindleRequired(Range):
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
    
class DLCMessmerKindle(Choice):
    """Randomize Messmer's Kindling / Shards.
    
    **DLC Only:** Randomize Kindling to your DLC.
    **Not Base:** Don't randomize Kindling to your base game.
    """
    display_name = "DLC Messmer's Kindling"
    option_normal = 0
    option_dlc_only = 1
    option_not_base = 2
    
class DLCScadutreeFragments(Choice):
    """Randomize Scadutree Fragments.
    
    **DLC Only:** Randomize Scadutree Fragments to your DLC.
    **Not Base:** Don't randomize Scadutree Fragments to your base game.
    """
    display_name = "DLC Scadutree Fragments"
    option_normal = 0
    option_dlc_only = 1
    option_not_base = 2

class DLCTimingOption(Choice):
    """Guarantee that you don't need to enter the DLC until later in the run.

    - **Early:** 'Pureblood Knight Medal' will spawn in an early sphere, unless MissableLocationBehaviorOption is set to do_not_randomize, it'll be at its normal spot.
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
    
class DLCSpiritspringStones(Toggle):
    """Randomize the Spiritsping Stones.""" 
    display_name = "Randomize Spiritsping Stones"
    visibility = Visibility.none   

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

class RestrictiveBossPlacement(DefaultOnToggle):
    """Restrict what arena's bosses can be placed into."""
    display_name = "Restrictive Boss Placement"
    
class RykardEncounter(DefaultOnToggle):
    """Give Serpent-Hunter on encounter with Rykard/Serpent in boss arenas.
    If off Serpent-Hunter will be randomized and be required for whatever Rykard/Serpent block."""
    display_name = "Rykard Encounter"
    
class BossScalingPercent(Range):
    """Scales HP and damage for enemies placed into boss slots.

    100 keeps the current static randomizer scaling. 90 means 90% of the boss
    location's HP and damage scaling, while 120 means 120%.
    """
    display_name = "Boss HP/Damage Scaling Percent"
    range_start = 25
    range_end = 200
    default = 100

class DisableGargoylePoisonCloudDamage(Toggle):
    """Disable the damage tick in Valiant Gargoyles' poison cloud while leaving poison buildup intact."""
    display_name = "Disable Damage Tick in Valiant Gargoyles' Poison Cloud"

class NightBosses(Choice):
    """
    Normal: Bosses spawn at night.
    Always On: Bosses will always spawn.
    Require Item: Bosses only spawn after finding an item.   just an idea from Spencenox, not implimented
    """
    display_name = "Night Bosses"
    option_normal = 0
    option_always_on = 1
    # option_require_item = 2
    default = 0

class RandomEnemyPresetOption(OptionDict):
    """The YAML preset for the static enemy randomizer.

    See the online enemy randomization documentation for available options.
    Include this as nested YAML. For example:

      random_enemy_preset:
        RemoveSource: Basilisk; Fingercreeper
        DontRandomize: Tree Sentinel

    Elden Ring uses class-based enemy pools. To let major bosses, minor bosses,
    world minibosses, night minibosses, dragon minibosses, and evergaol bosses
    draw from one combined boss pool:

      random_enemy_preset:
        DontRandomize: DLCAllEnemies
        Classes:
          Boss:
            Pools:
            - Weight: 100
              Pool: AllBosses

    To keep only DLC hostile NPCs and invasions at their vanilla placements while
    still shuffling base game hostile NPCs:

      random_enemy_preset:
        DontRandomize: DLCHostileNPC
    """
    display_name = "Random Enemy Preset"
    supports_weighting = False
    default = {}

    valid_keys = ["Description", "RecommendFullRandomization", "RecommendNoEnemyProgression", "Options",
                  "OopsAll", "Boss", "Miniboss", "Basic", "BuffBasicEnemiesAsBosses",
                  "DontRandomize", "RemoveSource", "EnemyMultiplier", "AdjustSource", "Classes", "Enemies"]

    @classmethod
    def get_option_name(cls, value: Dict[str, Any]) -> str:
        return json.dumps(value)

class MaterialRando(DefaultOnToggle):
    """Randomizes the indefinitely spawning materials."""
    display_name = "Material Randomizer"

# MARK: Traps

class TrapFillPercentage(Range):
    """
    Replace a percentage of filler items in the item pool with random traps.
    """
    display_name = "Trap Fill Percentage"
    range_start = 0
    range_end = 100
    default = 0
    
class BaseTrapWeight(Choice):
    """
    Base Class for Trap Weights
    """
    option_none = 0
    option_low = 1
    option_medium = 2
    option_high = 4
    default = 2
    # visibility = Visibility.none
    
class ExampleTrapWeight(BaseTrapWeight):
    """
    Example Trap: Description
    """
    display_name = "Example Trap Weight"
    
# Traps that need dlc stuff to work
    
class ExampleDLCTrapWeight(BaseTrapWeight):
    """
    Example DLC Trap: Description
    """
    display_name = "Example DLC Trap Weight"
    
class BlindnessTrapWeight(BaseTrapWeight):
    """
    Blindness Trap: Blinds the player for a short time.
    """
    display_name = "Blindness Trap Weight"
    

# MARK: Item & Location

class RandomizeStartingLoadout(DefaultOnToggle):
    """Randomizes the equipment characters begin with."""
    display_name = "Randomize Starting Loadout"

class RandomizeStartingKeepsakes(Toggle):
    """Randomizes selectable keepsakes at character creation."""
    display_name = "Randomize Starting Keepsakes"

class RequireOneHandedStartingWeapons(DefaultOnToggle):
    """Require starting equipment to be usable one-handed."""
    display_name = "Require One-Handed Starting Weapons"

class RemoveWeaponAndSpellRequirements(Toggle):
    """Remove all stat requirements from weapons and spells."""
    display_name = "Remove All Weapon and Spell Requirements"

class NoEquipLoadOption(Toggle):
    """Disable the equip load constraint from the game."""
    display_name = "No Equip Load"

class ReduceNonSomberUpgradeCost(Toggle):
    """Reduce regular Smithing Stone costs for non-somber weapons to one stone per weapon level."""
    display_name = "Reduce Upgrade Cost for Non-Somber Weapons"

class SnowFast(Toggle):
    """Adds Mountaintops of the Giants shortcuts for faster traversal."""
    display_name = "Add Shortcuts in Mountaintops for Faster Traversal"

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
    # visibility = Visibility.none
    
class SmoothRuneItems(Toggle):
    """Smooth Rune Items."""
    display_name = "Smooth Rune Items"
    # visibility = Visibility.none
    
class SpellShopSpellsOnly(Toggle):
    """Spell Shops only have spells."""
    display_name = "Spell Shop Spells Only"
    
class EarlyLegacyDungeonsEarly(Toggle):
    """Access to Stormveil and Raya Lucaria will be early."""
    display_name = "Stormveil and Raya Lucaria Early"

# MARK: Priority Stuff
    
class ERPriorityLocationGroups(PriorityLocations):
    """Prevent these location types from having an unimportant items.
    
    - *Achievement Boss*: Base game Achievement bosses.
    - *DLC Remembrance Boss*: DLC Remembrance bosses.
    - *Boss Reward*: Base game bosses.
    - *DLC Boss Reward*: DLC bosses.
    - *Overworld Boss*: Base game Overworld bosses.
    - *DLC Overworld Boss*: DLC Overworld bosses.
    - *Chest*: Chests.
    - *Scarab*: Scarabs.
    - *Seedtree*: Golden Seed trees.
    - *Basin*: Basins that contain tears.
    - *Church*: Sacred Tears.
    - *Map*: Map pillars.
    - *Fragment*: Scadu Fragments.
    - *Cross*: All cross items.
    - *Revered*: Revered Spirit Ashes.
    - *Key Items*: Key items.
    """
    display_name = "Priority Location Groups"
    default = ["Achievement Boss", "Seedtree", "Map", "Church", "Cross", "Overworld Boss"]
    valid_keys = ["chest", "scarab", "seedtree", "basin", "church", "map", "key items",
        "fragment", "cross", "revered", "overworld boss", "dlc overworld boss", 
        "achievement boss", "dlc remembrance boss", "boss reward", "dlc boss reward"]
    valid_keys_casefold = True
    
class ERImportantAtPriorityOnly(Toggle):
    """Should important items be only at priority locations.
    Generator likes to fail if there is to little priority locations, add more if it fails."""
    display_name = "Important at Priority Only"
    # visibility = Visibility.none # likes to fill error depending on how many priority locations there are
    
class ERImportantAtPriorityEarly(Range):
    """
    Needs Important at Priority Only On.
    
    Make extra generated locations appear more early game (Limgrave, Weeping, Liurnia, Stormveil and Raya Lucaria).
    
    1: Normal.
    2+: Multiplied odds of early game locations.
    
    Example: Setting this to 3 will make early locations 3 times more likely to have extra locations.
    """
    display_name = "Important At Priority Early"
    range_start = 1
    range_end = 5
    default = 1

class ERUsefulAtPriority(Toggle):
    """Should useful items be included in Priority locations.
    This is used with Important at Priority Only option since it uses custom priority handling."""
    display_name = "Useful at Priority"
    # visibility = Visibility.none

class FlaskUpgradesAtPriority(Toggle):
    "Should flask upgrades be randomized to important locations."
    display_name = "Flask Upgrades at Priority"
    
class ScaduAtPriority(Toggle):
    "Should scadu fragments be randomized to important locations."
    display_name = "Scadutree Fragments at Priority"

class TalismanPouchesAtPriority(Toggle):
    "Should talisman pouches be randomized to important locations."
    display_name = "Talisman Pouches at Priority"

class CrackedTearsAtPriority(Toggle):
    "Should Wondrous Physick tears be randomized to important locations."
    display_name = "Cracked Tears at Priority"

class MemoryStonesAtPriority(Toggle):
    "Should memory stones be randomized to important locations."
    display_name = "Memory Stones at Priority"

class RemembrancesAtPriority(Toggle):
    "Should remembrances be randomized to important priority locations."
    display_name = "Remembrances at Priority"

# MARK: Excludes and Behavior
    
class LocalItemOnly(OptionList):
    """Which categories should be local only, useful and progression excluded.
    - [Items] **Item Group**
    - [~600] **Weapon**: All Weapons and Ammo.
    - [621] **Armor**: All Armors.
    - [154] **Accessory**: All Talismans.
    - [105] **AshofWar**: All Ashes of War.
    - [~3700] **Goods**: The two below
    - **Filler**: All Crafting Mats.
    - **Non-Filler**: Smithing stones, Spells and Spirit ashes.
    
    Filler should always be local only, it floods the itempool with useless items.
    """
    display_name = "Local Item Only"
    default = ["Filler"]
    valid_keys = ["weapon", "armor", "accessory", "ashofwar", "goods", "filler", "non-filler"]
    valid_keys_casefold = True # spells are part of goods, do we add them to ashes of war or weapons category?

class ERExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important items.
    - **DLC**: If you want DLC items but dont wanna do DLC.
    - **Hidden**: Hard to find items.
    - **Blizzard**: The hard to see area of snowfield.
    - **Scarab**: Scarabs that drop items.
    - **Furnace Golem**: DLC Furnace Golems.
    - **Out of the Way**: Items that take a bit to get.
    - **Drop**: One time drop items from enemies."""
    default = frozenset({"Hidden"})
    valid_keys = {"dlc", "hidden", "blizzard", "scarab", "furnace golem", "out of the way", "drop"} # testing "All Locations"
    valid_keys_casefold = True
    
    unconverted_groups = set() # this is so dumb but it works, i need the unconverted group names
    def verify_keys(self) -> None:
        super().verify_keys()
        self.unconverted_groups = self.value
        
    def excluded_groups(self):
        return self.unconverted_groups

class ExcludedLocationBehaviorOption(Choice):
    """How to choose items for excluded locations in ER.

    - **Allow Useful:** Excluded locations can't have progression items, but they can have useful items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in excluded locations.
    - **Do Not Randomize:** Excluded locations always contain the same item as in vanilla.
    - **Omit:** This location won't count as a check (if the item is filler) and contains the same item as in vanilla.

    A "progression item" is anything that's required to unlock another location in some game.
    A "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Excluded Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    option_omit = 4
    default = 2

class MissableLocationBehaviorOption(Choice):
    """Which items can be placed in locations that can be permanently missed.

    - **Allow Useful:** Missable locations can't have progression items, but they can have useful items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in missable locations.
    - **Do Not Randomize:** Missable locations always contain the same item as in vanilla.
    - **Omit:** This location won't count as a check (if the item is filler) and contains the same item as in vanilla.

    A "progression item" is anything that's required to unlock another location in some game.
    A "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Missable Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    option_omit = 4
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
    great_runes_required_erdtree: GreatRunesRequiredErdtree
    royal_access: RoyalAccess
    use_master_key: StoneswordMasterKey
    
    enable_dlc: EnableDLC
    dlc_start: DLCStart
    dlc_starting_items: DLCStartingItems
    dlc_starting_shop: DLCStartingShop
    dlc_care_package: DLCCarePackage
    dlc_initial_rune_level: DLCInitialRuneLevel
    messmer_kindle: MessmerKindle
    messmer_kindle_required: MessmerKindleRequired
    messmer_kindle_max: MessmerKindleMax
    dlc_messmer_kindle: DLCMessmerKindle
    dlc_scadutree_fragments: DLCScadutreeFragments
    dlc_timing: DLCTimingOption
    dlc_max_level_weapons: DLCMaxLevelWeapons
    dlc_abyssal_torrent: DLCAbyssalTorrent
    spiritspring_stones: DLCSpiritspringStones
    
    enemy_rando: EnemyRando
    restrictive_bosses: RestrictiveBossPlacement
    rykard_encounter: RykardEncounter
    boss_scaling_percent: BossScalingPercent
    disable_gargoyle_poison_cloud_damage: DisableGargoylePoisonCloudDamage
    night_bosses: NightBosses
    random_enemy_preset: RandomEnemyPresetOption
    material_rando: MaterialRando
    death_link: DeathLink
    
    trap_fill_percentage: TrapFillPercentage
    example_trap_weight: ExampleTrapWeight
    
    example_dlc_trap_weight: ExampleDLCTrapWeight
    blindness_trap_weight: BlindnessTrapWeight

    random_start: RandomizeStartingLoadout
    randomize_starting_keepsakes: RandomizeStartingKeepsakes
    require_one_handed_starting_weapons: RequireOneHandedStartingWeapons
    remove_weapon_and_spell_requirements: RemoveWeaponAndSpellRequirements
    no_equip_load: NoEquipLoadOption
    reduce_non_somber_upgrade_cost: ReduceNonSomberUpgradeCost
    snowfast: SnowFast
    auto_equip: AutoEquipOption
    auto_upgrade: AutoUpgradeOption
    
    crafting_kit_option: CraftingKitOption
    map_option: MapOption
    smithing_bell_bearing_option: SmithingBellBearingOption
    smooth_upgrade_items: SmoothUpgradeItems
    smooth_rune_items: SmoothRuneItems
    spell_shop_spells_only: SpellShopSpellsOnly
    early_legacy_dungeons: EarlyLegacyDungeonsEarly
    local_item_only: LocalItemOnly
    priority_location_groups: ERPriorityLocationGroups
    important_at_priority_only: ERImportantAtPriorityOnly
    important_at_priority_early: ERImportantAtPriorityEarly
    useful_at_priority: ERUsefulAtPriority
    flask_at_priority: FlaskUpgradesAtPriority
    scadu_at_priority: ScaduAtPriority
    talisman_pouches_at_priority: TalismanPouchesAtPriority
    cracked_tears_at_priority: CrackedTearsAtPriority
    memory_stones_at_priority: MemoryStonesAtPriority
    remembrances_at_priority: RemembrancesAtPriority
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
        GreatRunesRequiredErdtree,
        RoyalAccess,
        StoneswordMasterKey,
    ]),
    OptionGroup("Other Randomizers", [
        EnemyRando,
        RestrictiveBossPlacement,
        RykardEncounter,
        BossScalingPercent,
        DisableGargoylePoisonCloudDamage,
        NightBosses,
        RandomEnemyPresetOption,
        MaterialRando,
    ]),
    OptionGroup("Equipment", [
        RandomizeStartingLoadout,
        RandomizeStartingKeepsakes,
        RequireOneHandedStartingWeapons,
        RemoveWeaponAndSpellRequirements,
        NoEquipLoadOption,
        ReduceNonSomberUpgradeCost,
        SnowFast,
        AutoEquipOption,
        AutoUpgradeOption,
    ]),
    OptionGroup("Death Link", [
        DeathLink
    ]),
    OptionGroup("DLC", [
        EnableDLC,
        MessmerKindle,
        MessmerKindleRequired,
        MessmerKindleMax,
        DLCMessmerKindle,
        DLCScadutreeFragments,
        DLCTimingOption,
        DLCMaxLevelWeapons,
        DLCAbyssalTorrent,
        DLCSpiritspringStones,
    ]),
    OptionGroup("DLC Start", [
        DLCStart,
        DLCStartingItems,
        DLCStartingShop,
        DLCCarePackage,
        DLCInitialRuneLevel,
    ]),
    OptionGroup("Traps", [
        TrapFillPercentage,
        ExampleTrapWeight,
    ]),
    OptionGroup("DLC Traps", [
        ExampleDLCTrapWeight,
        BlindnessTrapWeight
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
        ERExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ]),
    OptionGroup("Priority Location Rules", [
        ERPriorityLocationGroups,
        ERImportantAtPriorityOnly,
        ERImportantAtPriorityEarly,
        ERUsefulAtPriority,
        FlaskUpgradesAtPriority,
        ScaduAtPriority,
        TalismanPouchesAtPriority,
        CrackedTearsAtPriority,
        MemoryStonesAtPriority,
        RemembrancesAtPriority,
    ])
]