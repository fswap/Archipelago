import json
from dataclasses import dataclass
from typing import Any

from Options import (
    Choice,
    DefaultOnToggle,
    ExcludeLocations,
    OptionDict,
    OptionGroup,
    PerGameCommonOptions,
    Toggle,
    Visibility,
)

## Game Options


class QuickHirata(Choice):
    """Force the Young Lord's Bell Charm to be early in your local world or the multiworld"""
    display_name = "Quick Hirata"
    option_off = 0
    option_early_global = 1
    option_early_local = 2
    default = option_off


class VeryEarlyHirata(Choice):
    """Make it possible to need to progress into Hirata Estate before Ashina Outskirts (no softlock)"""
    display_name = "Allow Very Early Hirata"
    option_off = 0
    option_early_global = 1
    option_early_local = 2
    default = option_off

class DeathLink(Choice):
    """When you die, everyone who enabled death link dies. Of course, the reverse is true too.

    - **Off:** Death link is disabled. (The default.)
    - **Full Death:** Death link triggers only for full deaths. (No resurrection available or falling death).
    - **Any Death:** Death link triggers anytime you hit 0 HP. (Usage can lead to angry cooperators.)
    """
    display_name = "Death Link"
    option_off = 0
    alias_false = 0
    option_full_death = 1
    alias_true = 1
    option_any_death = 2
    default = 0

class RemoveHeadlessSlowWalk(Toggle):
    """Remove the Headless-induced slow walk."""
    display_name = "Remove Headless slow walk"

## Skills

class ShuffleSkills(Toggle):
    """Shuffle the Skills in the Skill Trees unlocked via Esoteric Texts"""
    display_name = "Shuffle Skills in Esoteric Texts"


class RandomizeSkillsItemOption(Toggle):
    """Randomize the Skills as Item pickups """
    display_name = "Randomize Skills as Item Pickups"
    visibility = Visibility.none

### Enemies

class RandomizeEnemiesOption(DefaultOnToggle):
    """Randomize enemy and boss placements."""
    display_name = "Randomize Enemies"


class RandomizeHeadlessOption(Toggle):
    """Include headless in the randomizer pool for minibosses (non-underwater)

    This is ignored unless enemies are randomized.
    """
    display_name = "Randomize Headless"


class SimilarBossPhases(DefaultOnToggle):
    """Prevent fights to be something like Sword Saint Isshin + Demon of Hatred.

     This setting will try to keep a similar number of phases compared to the replaced vanilla bosses.

     This is ignored unless enemies are randomized.
     """
    display_name = "Similar Number of Boss Phases"


class BalancedEndgameBossPhases(DefaultOnToggle):
    """Prevent early bosses to be seriously unfun by considering late game boss phases as longer than earlier ones.

    This is ignored unless enemies are randomized.
    """
    display_name = "Smoothed Boss Phases"


class SimpleEarlyMinibosses(DefaultOnToggle):
    """Prevent early minibosses from being unfun without scaling.

    This is ignored unless enemies are randomized.
    """
    display_name = "Simple Early Minibosses"


class ScaleEnemiesOption(DefaultOnToggle):
    """Scale randomized enemy stats to match the areas in which they appear.

    Disabling this will tend to make the early game much more difficult and the late game much
    easier.

    This is ignored unless enemies are randomized.
    """
    display_name = "Scale Enemies"


class RandomEnemyPresetOption(OptionDict):
    """The YAML preset for the static enemy randomizer.

    See the static randomizer documentation in `randomizer\\presets\\README.txt` for details.
    Include this as nested YAML. For example:

    .. code-block:: YAML

      random_enemy_preset:
        RemoveSource: Demon of Hatred; Corrupted monk
        DontRandomize: Shichimen Warrior
    """
    display_name = "Random Enemy Preset"
    supports_weighting = False
    default = {}

    valid_keys = ["Description", "RecommendFullRandomization", "RecommendNoEnemyProgression",
                  "OopsAll", "Boss", "Miniboss", "Basic", "Add", "FoldingMonkey", "BuffBasicEnemiesAsBosses",
                  "DontRandomize", "RemoveSource", "Enemies"]

    @classmethod
    def get_option_name(cls, value: dict[str, Any]) -> str:
        return json.dumps(value)


## Item & Location

class Carpsanity(Toggle):
    """Add Treasure Carp drops into the item pool"""
    display_name = "Carpsanity"


class SekiroExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important item."""
    default = frozenset({"Hidden", "Upgrade", "Miscellaneous"})


class ExcludedLocationBehaviorOption(Choice):
    """How to choose items for excluded locations in DS3.

    - **Allow Useful:** Excluded locations can't have progression items, but they can have useful
      items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in excluded
      locations.
    - **Do Not Randomize:** Excluded locations always contain the same item as in vanilla Dark Souls
      III.

    A "progression item" is anything that's required to unlock another location in some game. A
    "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Excluded Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    default = 2


class MissableLocationBehaviorOption(Choice):
    """Which items can be placed in locations that can be permanently missed.

    - **Allow Useful:** Missable locations can't have progression items, but they can have useful
      items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in missable
      locations.
    - **Do Not Randomize:** Missable locations always contain the same item as in vanilla Dark Souls
      III.

    A "progression item" is anything that's required to unlock another location in some game. A
    "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Missable Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    default = 2


@dataclass
class SekiroOptions(PerGameCommonOptions):
    # Game Options
    quick_hirata: QuickHirata
    very_early_hirata: VeryEarlyHirata
    death_link: DeathLink
    remove_headless_slow_walk: RemoveHeadlessSlowWalk

    # Skills
    shuffle_skills: ShuffleSkills
    randomize_skills_as_items: RandomizeSkillsItemOption

    # Enemies
    randomize_enemies: RandomizeEnemiesOption
    randomize_headless: RandomizeHeadlessOption
    similar_boss_phases: SimilarBossPhases
    balanced_endgame_boss_phases: BalancedEndgameBossPhases
    simple_early_minibosses: SimpleEarlyMinibosses
    scale_enemies: ScaleEnemiesOption
    random_enemy_preset: RandomEnemyPresetOption

    # Item & Location
    carpsanity: Carpsanity
    exclude_locations: SekiroExcludeLocations
    excluded_location_behavior: ExcludedLocationBehaviorOption
    missable_location_behavior: MissableLocationBehaviorOption


option_groups = [
    OptionGroup("Skills", [
        ShuffleSkills,
        RandomizeSkillsItemOption,
    ]),
    OptionGroup("Enemies", [
        RandomizeEnemiesOption,
        RandomizeHeadlessOption,
        SimilarBossPhases,
        BalancedEndgameBossPhases,
        SimpleEarlyMinibosses,
        ScaleEnemiesOption,
        RandomEnemyPresetOption,
    ]),
    OptionGroup("Item & Location Options", [
        Carpsanity,
        SekiroExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ])
]
