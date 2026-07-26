from typing import Any, Dict

from Options import Accessibility, ProgressionBalancing
from .options import GoalOption, ExcludeDungeonBosses, WorldLogic, RegionSoftLogic,\
        GreatRunesRequiredLeyndell, GreatRunesRequiredMountain, GreatRunesRequiredErdtree,\
        RoyalAccess,\
        StoneswordMasterKey,\
        EnemyRando, RandomEnemyPresetOption,\
        RestrictiveBossPlacement, RykardEncounter, BossScalingPercent, DisableGargoylePoisonCloudDamage, NightBosses,\
        DungeonSweep,\
        MaterialRando,\
        RandomizeStartingLoadout, RandomizeStartingKeepsakes,\
        RequireOneHandedStartingWeapons, RemoveWeaponAndSpellRequirements, NoEquipLoadOption, ReduceNonSomberUpgradeCost,\
        SnowFast,\
        AutoEquipOption, AutoUpgradeOption,\
        DeathLink,\
        EnableDLC,\
        MessmerKindle, MessmerKindleRequired, MessmerKindleMax,\
        DLCMessmerKindle, DLCScadutreeFragments,\
        DLCTimingOption,\
        DLCMaxLevelWeapons,\
        DLCAbyssalTorrent,\
        DLCSpiritspringStones,\
        DLCStart, DLCStartingItems, DLCStartingShop, DLCCarePackage, DLCInitialRuneLevel,\
        NGPlusTrapCount, StatusTrapCount,\
        BlindnessTrapCount,\
        CraftingKitOption, MapOption, SmithingBellBearingOption,\
        SmoothUpgradeItems, SmoothRuneItems,\
        SpellShopSpellsOnly,\
        EarlyLegacyDungeonsEarly,\
        LocalItemOnly,\
        ERExcludeLocations, ExcludedLocationBehaviorOption, MissableLocationBehaviorOption,\
        ERPriorityLocationGroups, ERImportantAtPriorityOnly, ERImportantAtPriorityEarly,\
        ERUsefulAtPriority, FlaskUpgradesAtPriority, ScaduAtPriority, TalismanPouchesAtPriority, CrackedTearsAtPriority, MemoryStonesAtPriority, RemembrancesAtPriority

template = {
    "goal":                                 GoalOption,
    "exclude_dungeon":                      ExcludeDungeonBosses,
    "world_logic":                          WorldLogic,
    "soft_logic":                           RegionSoftLogic,
    "great_runes_required_leyndell":        GreatRunesRequiredLeyndell,
    "great_runes_required_mountain":        GreatRunesRequiredMountain,
    "great_runes_required_erdtree":         GreatRunesRequiredErdtree,
    "royal_access":                         RoyalAccess,
    "use_master_key":                       StoneswordMasterKey,
    
    "enable_dlc":                           EnableDLC,
    "dlc_start":                            DLCStart,
    "dlc_starting_items":                   DLCStartingItems,
    "dlc_starting_shop":                    DLCStartingShop,
    "dlc_care_package":                     DLCCarePackage,
    "dlc_initial_rune_level":               DLCInitialRuneLevel,
    "messmer_kindle":                       MessmerKindle,
    "messmer_kindle_required":              MessmerKindleRequired,
    "messmer_kindle_max":                   MessmerKindleMax,
    "dlc_messmer_kindle":                   DLCMessmerKindle,
    "dlc_scadutree_fragments":              DLCScadutreeFragments,
    "dlc_timing":                           DLCTimingOption,
    "dlc_max_level_weapons":                DLCMaxLevelWeapons,
    "dlc_abyssal_torrent":                  DLCAbyssalTorrent,
    "spiritspring_stones":                  DLCSpiritspringStones,
    
    "enemy_rando":                          EnemyRando,
    "restrictive_bosses":                   RestrictiveBossPlacement,
    "rykard_encounter":                     RykardEncounter,
    "boss_scaling_percent":                 BossScalingPercent,
    "disable_gargoyle_poison_cloud_damage": DisableGargoylePoisonCloudDamage,
    "night_bosses":                         NightBosses,
    "dungeon_sweep":                        DungeonSweep,
    "random_enemy_preset":                  RandomEnemyPresetOption,
    "material_rando":                       MaterialRando,
    "death_link":                           DeathLink,
    
    "ngplus_trap_count":                    NGPlusTrapCount,
    "status_trap_count":                    StatusTrapCount,
    
    "blindness_trap_count":                 BlindnessTrapCount,

    "random_start":                         RandomizeStartingLoadout,
    "randomize_starting_keepsakes":         RandomizeStartingKeepsakes,
    "require_one_handed_starting_weapons":  RequireOneHandedStartingWeapons,
    "remove_weapon_and_spell_requirements": RemoveWeaponAndSpellRequirements,
    "no_equip_load":                        NoEquipLoadOption,
    "reduce_non_somber_upgrade_cost":       ReduceNonSomberUpgradeCost,
    "snowfast":                             SnowFast,
    "auto_equip":                           AutoEquipOption,
    "auto_upgrade":                         AutoUpgradeOption,
    
    "crafting_kit_option":                  CraftingKitOption,
    "map_option":                           MapOption,
    "smithing_bell_bearing_option":         SmithingBellBearingOption,
    "smooth_upgrade_items":                 SmoothUpgradeItems,
    "smooth_rune_items":                    SmoothRuneItems,
    "spell_shop_spells_only":               SpellShopSpellsOnly,
    "early_legacy_dungeons":                EarlyLegacyDungeonsEarly,
    "priority_location_groups":             ERPriorityLocationGroups,
    "important_at_priority_only":           ERImportantAtPriorityOnly,
    "important_at_priority_early":          ERImportantAtPriorityEarly,
    "useful_at_priority":                   ERUsefulAtPriority,
    "flask_at_priority":                    FlaskUpgradesAtPriority,
    "scadu_at_priority":                    ScaduAtPriority,
    "talisman_pouches_at_priority":         TalismanPouchesAtPriority,
    "cracked_tears_at_priority":            CrackedTearsAtPriority,
    "memory_stones_at_priority":            MemoryStonesAtPriority,
    "remembrances_at_priority":             RemembrancesAtPriority,
    "local_item_only":                      LocalItemOnly.default,
    "exclude_locations":                    ERExcludeLocations.default,
    "excluded_location_behavior":           ExcludedLocationBehaviorOption,
    "missable_location_behavior":           MissableLocationBehaviorOption,
}


all_random_options = {
    "progression_balancing":                "random",
    "accessibility":                        "random",
    "goal":                                 "random",
    "exclude_dungeon":                      "random",
    "world_logic":                          "random",
    "soft_logic":                           "random",
    "great_runes_required_leyndell":        "random",
    "great_runes_required_mountain":        "random",
    "great_runes_required_erdtree":         "random",
    "royal_access":                         "random",
    "use_master_key":                       "random",
    
    "enable_dlc":                           "random",
    "dlc_start":                            "random",
    "dlc_starting_items":                   "random",
    "dlc_starting_shop":                    "random",
    "dlc_care_package":                     "random",
    "dlc_initial_rune_level":               "random",
    "messmer_kindle":                       "random",
    "messmer_kindle_required":              "random",
    "messmer_kindle_max":                   "random",
    "dlc_messmer_kindle":                   "random",
    "dlc_scadutree_fragments":              "random",
    "dlc_timing":                           "random",
    "dlc_max_level_weapons":                "random",
    "dlc_abyssal_torrent":                  "random",
    "spiritspring_stones":                  "random",
    
    "enemy_rando":                          EnemyRando.option_true,
    "restrictive_bosses":                   "random",
    "rykard_encounter":                     "random",
    "boss_scaling_percent":                 "random-range-75-125",
    "disable_gargoyle_poison_cloud_damage": "random",
    "night_bosses":                         "random",
    "dungeon_sweep":                        "random",
    "random_enemy_preset":                  RandomEnemyPresetOption.default,
    "material_rando":                       "random",
    "death_link":                           DeathLink.option_false,
    
    "ngplus_trap_count":                    "random",
    "status_trap_count":                    "random",
    
    "blindness_trap_count":                 "random",

    "random_start":                         RandomizeStartingLoadout.option_true,
    "randomize_starting_keepsakes":         RandomizeStartingKeepsakes.option_true,
    "require_one_handed_starting_weapons":  "random",
    "remove_weapon_and_spell_requirements": "random",
    "no_equip_load":                        "random",
    "reduce_non_somber_upgrade_cost":       "random",
    "snowfast":                             "random",
    "auto_equip":                           "random",
    "auto_upgrade":                         "random",
    
    "crafting_kit_option":                  CraftingKitOption.option_randomize,
    "map_option":                           MapOption.option_randomize,
    "smithing_bell_bearing_option":         SmithingBellBearingOption.option_progression_randomize,
    "smooth_upgrade_items":                 "random",
    "smooth_rune_items":                    "random",
    "spell_shop_spells_only":               "random",
    "early_legacy_dungeons":                "random",
    "priority_location_groups":             "random",
    "important_at_priority_only":           "random",
    "important_at_priority_early":          "random",
    "useful_at_priority":                   "random",
    "flask_at_priority":                    "random",
    "scadu_at_priority":                    "random",
    "talisman_pouches_at_priority":         "random",
    "cracked_tears_at_priority":            "random",
    "memory_stones_at_priority":            "random",
    "remembrances_at_priority":             "random",
    "local_item_only":                      LocalItemOnly.default,
    "exclude_locations":                    ERExcludeLocations.default,
    "excluded_location_behavior":           "random",
    "missable_location_behavior":           "random",
}



# hardcore_mode_options = {
#     "progression_balancing":         ProgressionBalancing.default,
#     "accessibility":                 Accessibility.option_minimal,
#     "ignore_cleansing":              IgnoreCleansing.option_true,
#     "auto_run":                      AutoRun.option_false,
#     "dss_patch":                     DSSPatch.option_true,
#     "always_allow_speed_dash":       AlwaysAllowSpeedDash.option_false,
#     "iron_maiden_behavior":          IronMaidenBehavior.option_vanilla,
#     "required_last_keys":            9,
#     "available_last_keys":           9,
#     "buff_ranged_familiars":         BuffRangedFamiliars.option_false,
#     "buff_sub_weapons":              BuffSubWeapons.option_false,
#     "buff_shooter_strength":         BuffShooterStrength.option_false,
#     "item_drop_randomization":       ItemDropRandomization.option_tiered,
#     "halve_dss_cards_placed":        HalveDSSCardsPlaced.option_true,
#     "countdown":                     Countdown.option_none,
#     "sub_weapon_shuffle":            SubWeaponShuffle.option_true,
#     "disable_battle_arena_mp_drain": DisableBattleArenaMPDrain.option_false,
#     "required_skirmishes":           RequiredSkirmishes.option_none,
#     "pluto_griffin_air_speed":       PlutoGriffinAirSpeed.option_false,
#     "skip_dialogues":                SkipDialogues.option_false,
#     "skip_tutorials":                SkipTutorials.option_false,
#     "nerf_roc_wing":                 NerfRocWing.option_false,
#     "early_escape_item":             EarlyEscapeItem.option_double,
#     "battle_arena_music":            BattleArenaMusic.option_nothing,
#     "death_link":                    CVCotMDeathLink.option_off,
#     "completion_goal":               CompletionGoal.option_battle_arena_and_dracula,
# }

er_options_presets: Dict[str, Dict[str, Any]] = {
    "All Random": all_random_options,
}