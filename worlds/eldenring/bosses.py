from dataclasses import dataclass, field
from typing import Set, Optional


@dataclass
class ERBossInfo:
    """The set of locations a given boss location blocks access to."""

    name: str
    """The boss's name."""

    region: str
    """The region that this is the boss of."""

    id: int
    """The game's ID for this particular boss."""

    flag: Optional[int]
    """The event flag that's set when this boss is defeated.

    This is None for first-phase bosses."""

    dlc: bool = False
    """This boss appears in one of the game's DLCs."""
    
    dungeon: bool = False
    """This boss appears in a underground dungeon."""

    locations: Set[str] = field(default_factory=set)
    """Locations the boss blocks so we can do can_get location."""

base_bosses = [
    # MARK: Limgrave
    #ERBossInfo("Solder of Godrick", "Limgrave", 0, 0), # doesn't have an item behind it since emote spots dont count
    ERBossInfo("Tree Sentinel", "Limgrave", 0, 0,
        locations=[
            "LG/TFS: Golden Halberd - first field boss"
        ]
    ),
    ERBossInfo("Flying Dragon Agheel", "Limgrave", 0, 0,
        locations=[
            "LG/DBR: Dragon Heart - boss drop N of DBR",
            "CL/(CDC): Agheel's Flame - Dragon Communion, kill boss in LG, NW of DBR"
        ]
    ),
    ERBossInfo("Night's Cavalry", "Limgrave", 0, 0,
        locations=[
            "LG/ALN: Ash of War: Repeating Thrust - night boss drop to SE"
        ]
    ),
    ERBossInfo("Bloodhound Knight Darriwil", "Limgrave", 0, 0,
        locations=[
            "LG/(FHE): Bloodhound's Fang - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Tibia Mariner", "Limgrave", 0, 0,
        locations=[
            "LG/(SWV): Deathroot - boss drop",
            "LG/(SWV): Skeletal Militiaman Ashes - boss drop"
        ]
    ),
    # stormhill
    ERBossInfo("Crucible Knight", "Limgrave", 0, 0,
        locations=[
            "LG/(SE): Aspects of the Crucible: Tail - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Deathbird", "Limgrave", 0, 0,
        locations=[
            "LG/WS: Blue-Feathered Branchsword - night boss drop SE of WS"
        ]
    ),
    ERBossInfo("Bell Bearing Hunter", "Limgrave", 0, 0,
        locations=[
            "LG/(WS): Bone Peddler's Bell Bearing - night boss drop"
        ]
    ),
    # limgrave dungeons
    ERBossInfo("Mad Pumpkin Head", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(WR): Glintstone Pebble - Sellen Shop",
            "LG/(WR): Glintstone Stars - Sellen Shop",
            "LG/(WR): Crystal Barrage - Sellen Shop",
            "LG/(WR): Glintstone Arc - Sellen Shop",
            "LG/(WR): Scholar's Armament - Sellen Shop",
            "LG/(WR): Scholar's Shield - Sellen Shop",
        ]
    ),
    ERBossInfo("Ulcerated Tree Spirit", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(FHG): Golden Seed - boss drop",
            "LG/(FHG): Banished Knight Oleg - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(SC): Noble Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Grave Warden Duelist", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(MCC): Banished Knight Engvall - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(DC): Assassin's Crimson Dagger - boss drop"
        ]
    ),
    ERBossInfo("Beastman of Farum Azula", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(GC): Flamedrake Talisman - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Chief", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(CC): Tailoring Tools - boss drop",
            "LG/(CC): Sewing Needle - boss drop"
        ]
    ),
    ERBossInfo("Guardian Golem", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(HC): Blue Dancer Charm - boss drop"
        ]
    ),
    ERBossInfo("Stonedigger Troll", "Limgrave", 0, 0, dungeon=True,
        locations=[
            "LG/(LT): Roar Medallion - boss drop"
        ]
    ),
    
    # MARK: Stormveil
    ERBossInfo("Margit, the Fell Omen", "Stormveil Castle", 0, 0,
        locations=[
            "SV/CT: Talisman Pouch - boss drop" # + the entire castle, but im not doing all that
        ]
    ),
    ERBossInfo("Godrick the Grafted", "Stormveil Castle", 0, 0,
        locations=[
            "SV/SeC: Godrick's Great Rune - mainboss drop",
            "SV/SeC: Remembrance of the Grafted - mainboss drop"
        ]
    ),

    
    
    ERBossInfo("", "", 0, 0,
        locations=[
        ]
    ),
]

dlc_bosses = [
    ERBossInfo("", "", 0, 0,
        locations=[
        ]
    ),
]

for boss in dlc_bosses:
    boss.dlc = True
    
all_bosses = base_bosses + dlc_bosses