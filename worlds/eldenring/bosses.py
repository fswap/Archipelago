from dataclasses import dataclass, field
from typing import Set, Optional


@dataclass
class ERBossInfo:
    """The set of locations a given boss location blocks access to."""

    name: str
    """The boss's name."""

    type: list[str]
    """The region/type that this is the boss of."""

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
    #ERBossInfo("Solder of Godrick", ["Limgrave"], 0, 0), # doesn't have an item behind it since emote spots dont count
    ERBossInfo("Tree Sentinel (LG)", ["Limgrave", "Overworld"], 0, 0,
        locations=[
            "LG/TFS: Golden Halberd - first field boss"
        ]
    ),
    ERBossInfo("Flying Dragon Agheel (LG)", ["Limgrave", "Overworld"], 0, 0,
        locations=[
            "LG/DBR: Dragon Heart - boss drop N of DBR",
            "CL/(CDC): Agheel's Flame - Dragon Communion, kill boss in LG, NW of DBR"
        ]
    ),
    ERBossInfo("Night's Cavalry (LG)", ["Limgrave", "Overworld"], 0, 0,
        locations=[
            "LG/ALN: Ash of War: Repeating Thrust - night boss drop to SE"
        ]
    ),
    ERBossInfo("Bloodhound Knight Darriwil (LG)", ["Limgrave", "Overworld", "Evergaol"], 0, 0,
        locations=[
            "LG/(FHE): Bloodhound's Fang - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Tibia Mariner (LG)", ["Limgrave", "Overworld"], 0, 0,
        locations=[
            "LG/(SWV): Deathroot - boss drop",
            "LG/(SWV): Skeletal Militiaman Ashes - boss drop"
        ]
    ),
    ERBossInfo("Mad Pumpkin Head (LG/WR)", ["Limgrave", "Overworld", "Ruin"], 0, 0,
        locations=[
            "LG/(WR): Glintstone Pebble - Sellen Shop",
            "LG/(WR): Glintstone Stars - Sellen Shop",
            "LG/(WR): Crystal Barrage - Sellen Shop",
            "LG/(WR): Glintstone Arc - Sellen Shop",
            "LG/(WR): Scholar's Armament - Sellen Shop",
            "LG/(WR): Scholar's Shield - Sellen Shop",
        ]
    ),
    ERBossInfo("Crucible Knight (LG)", ["Limgrave", "Overworld", "Evergaol"], 0, 0,
        locations=[
            "LG/(SE): Aspects of the Crucible: Tail - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Deathbird (LG)", ["Limgrave", "Overworld"], 0, 0,
        locations=[
            "LG/WS: Blue-Feathered Branchsword - night boss drop SE of WS"
        ]
    ),
    ERBossInfo("Bell Bearing Hunter (LG)", ["Limgrave", "Overworld"], 0, 0,
        locations=[
            "LG/(WS): Bone Peddler's Bell Bearing - night boss drop"
        ]
    ),
    # limgrave dungeons
    ERBossInfo("Ulcerated Tree Spirit (LG/FHG)", ["Limgrave", "Dungeon", "Grave"], 0, 0, dungeon=True,
        locations=[
            "LG/(FHG): Golden Seed - boss drop",
            "LG/(FHG): Banished Knight Oleg - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog (LG/SC)", ["Limgrave", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LG/(SC): Noble Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Grave Warden Duelist (LG/MCC)", ["Limgrave", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LG/(MCC): Banished Knight Engvall - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin (LG/DC)", ["Limgrave", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LG/(DC): Assassin's Crimson Dagger - boss drop"
        ]
    ),
    ERBossInfo("Beastman of Farum Azula (LG/GC)", ["Limgrave", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "LG/(GC): Flamedrake Talisman - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Chief (LG/CC)", ["Limgrave", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "LG/(CC): Tailoring Tools - boss drop",
            "LG/(CC): Sewing Needle - boss drop"
        ]
    ),
    ERBossInfo("Guardian Golem (LG/HC)", ["Limgrave", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "LG/(HC): Blue Dancer Charm - boss drop"
        ]
    ),
    ERBossInfo("Stonedigger Troll (LG/LT)", ["Limgrave", "Dungeon", "Tunnel"], 0, 0, dungeon=True,
        locations=[
            "LG/(LT): Roar Medallion - boss drop"
        ]
    ),
    
    # MARK: Stormveil
    ERBossInfo("Margit, the Fell Omen", ["Stormveil Castle"], 0, 0,
        locations=[
            "SV/CT: Talisman Pouch - boss drop" # + the entire castle, but im not doing all that
        ]
    ),
    ERBossInfo("Godrick the Grafted", ["Stormveil Castle", "Remembrance", "Great Rune"], 0, 0,
        locations=[
            "SV/SeC: Godrick's Great Rune - mainboss drop",
            "SV/SeC: Remembrance of the Grafted - mainboss drop"
        ]
    ),

    # MARK: Weeping Peninsula
    ERBossInfo("Ancient Hero of Zamor (WP)", ["Weeping Peninsula", "Overworld", "Evergaol"], 0, 0,
        locations=[
            "WP/(WE): Radagon's Scarseal - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Leonine Misbegotten (WP/CM)", ["Weeping Peninsula", "Castle Morne", "Overworld"], 0, 0,
        locations=[
            "WP/(CM): Grafted Blade Greatsword - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Avatar (WP)", ["Weeping Peninsula", "Overworld"], 0, 0,
        locations=[
            "WP/ME: Opaline Bubbletear - boss drop",
            "WP/ME: Crimsonburst Crystal Tear - boss drop"
        ]
    ),
    ERBossInfo("Deathbird (WP)", ["Weeping Peninsula", "Overworld"], 0, 0,
        locations=[
            "WP/CMR: Sacrificial Axe - night boss drop far to SW"
        ]
    ),
    ERBossInfo("Night's Cavalry (WP)", ["Weeping Peninsula", "Overworld"], 0, 0,
        locations=[
            "WP/CMR: Nightrider Flail - night boss drop to SW",
            "WP/CMR: Ash of War: Barricade Shield - night boss drop to SW"
        ]
    ),
    # weeping dungeons
    ERBossInfo("Cemetery Shade (WP/TCC)", ["Weeping Peninsula", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "WP/(TCC): Lhutel the Headless - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog (WP/IC)", ["Weeping Peninsula", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "WP/(IC): Demi-Human Ashes - boss drop"
        ]
    ),
    ERBossInfo("Runebear (WP/EC)", ["Weeping Peninsula", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "WP/(EC): Spelldrake Talisman - boss drop"
        ]
    ),
    ERBossInfo("Miranda the Blighted Bloom (WP/TCV)", ["Weeping Peninsula", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "WP/(TCV): Viridian Amber Medallion - boss drop"
        ]
    ),
    ERBossInfo("Scaly Misbegotten (WP/MT)", ["Weeping Peninsula", "Dungeon", "Tunnel"], 0, 0, dungeon=True,
        locations=[
            "WP/(MT): Rusted Anchor - boss drop"
        ]
    ),
    
    # MARK: SE Underground
    ERBossInfo("Ancestor Spirit (SR)", ["Siofra River", "Underground"], 0, 0,
        locations=[
            "SR/(HG): Ancestral Follower Ashes - boss drop"
        ]
    ),
    ERBossInfo("Dragonkin Soldier (SR)", ["Siofra River", "Underground"], 0, 0,
        locations=[
            "SR/WW: Dragon Halberd - upper siofra, boss drop"
        ]
    ),
    ERBossInfo("Mimic Tear (NR)", ["Nokron, Eternal City", "Underground"], 0, 0,
        locations=[
            "NR/NEC: Silver Tear Mask - boss drop",
            "NR/NEC: Larval Tear x2 - boss drop"
        ]
    ),
    ERBossInfo("Valiant Gargoyle (NR)", ["Nokron, Eternal City", "Underground"], 0, 0,
        locations=[
            "NR/(SA): Gargoyle's Greatsword - boss drop", "Gargoyle's Greatsword",
            "NR/(SA): Gargoyle's Twinblade - boss drop", "Gargoyle's Twinblade"
        ]
    ),
    ERBossInfo("Regal Ancestor Spirit (NR)", ["Nokron, Eternal City", "Underground", "Remembrance"], 0, 0,
        locations=[
            "NR/(HG): Remembrance of the Regal Ancestor - boss drop"
        ]
    ),
    
    # MARK: N Underground
    ERBossInfo("Crucible Knight Siluria (DD)", ["Deeproot Depths", "Underground"], 0, 0,
        locations=[
            "DD/TNEC: Siluria's Tree - boss drop way to W by tree stump"
        ]
    ),
    ERBossInfo("Fia's Champions (DD)", ["Deeproot Depths", "Underground"], 0, 0,
        locations=[
            "DD/AR: Fia's Mist - boss drop"
        ]
    ),
    ERBossInfo("Lichdragon Fortissax (DD)", ["Deeproot Depths", "Underground", "Remembrance"], 0, 0,
        locations=[
            "DD/PDT: Remembrance of the Lichdragon - mainboss drop"
        ]
    ),
    
    # MARK: Liurnia of The Lakes
    ERBossInfo("Erdtree Avatar (LL/MEW)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/MEW: Cerulean Crystal Tear - boss drop, Minor Erdtree W",
            "LL/MEW: Ruptured Crystal Tear - boss drop, Minor Erdtree W"
        ]
    ),
    ERBossInfo("Bols, Carian Knight (LL)", ["Liurnia of The Lakes", "Overworld", "Evergaol"], 0, 0,
        locations=[
            "LL/(CE): Greatblade Phalanx - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Glintstone Dragon Smarag (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/TQ: Dragon Heart - boss drop to N"
        ]
    ),
    ERBossInfo("Omenkiller (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/(VA): Crucible Knot Talisman - boss drop"
        ]
    ),
    ERBossInfo("Royal Knight Loretta (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/(CM): Loretta's Greatbow - boss drop",
            "LL/(CM): Ash of War: Loretta's Slash - boss drop"
        ]
    ),
    ERBossInfo("Death Rite Bird (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/GTN: Ancient Death Rancor - night boss drop to S"
        ]
    ),
    ERBossInfo("Deathbird (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/SeI: Red-Feathered Branchsword - night boss drop to NE"
        ]
    ),
    ERBossInfo("Bell Bearing Hunter (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/(CV): Meat Peddler's Bell Bearing - night boss drop"
        ]
    ),
    ERBossInfo("Adan, Thief of Fire (LL)", ["Liurnia of The Lakes", "Overworld", "Evergaol"], 0, 0,
        locations=[
            "LL/(ME): Flame of the Fell God - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Night's Cavalry (LL/GTB)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/GTB: Ash of War: Ice Spear - night boss drop to SE"
        ]
    ),
    ERBossInfo("Tibia Mariner (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/AS: Deathroot - boss drop SE of AS",
            "LL/AS: Skeletal Bandit Ashes - boss drop SE of AS"
        ]
    ),
    ERBossInfo("Night's Cavalry (LL/BC)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/BC: Nightrider Glaive - night boss drop S of BC",
            "LL/BC: Ash of War: Giant Hunt - night boss drop S of BC"
        ]
    ),
    ERBossInfo("Erdtree Avatar (LL/MEE)", ["Liurnia of The Lakes", "Overworld"], 0, 0,
        locations=[
            "LL/MEE: Magic-Shrouding Cracked Tear - boss drop, Minor Erdtree E",
            "LL/MEE: Lightning-Shrouding Cracked Tear - boss drop, Minor Erdtree E",
            "LL/MEE: Holy-Shrouding Cracked Tear - boss drop, Minor Erdtree E"
        ]
    ),
    ERBossInfo("Onyx Lord (LL)", ["Liurnia of The Lakes", "Overworld", "Evergaol"], 0, 0,
        locations=[
            "LL/(RGE): Meteorite - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Royal Revenant (LL/KR)", ["Liurnia of The Lakes", "Overworld", "Ruin"], 0, 0,
        locations=[
            "LL/(KR): Frozen Needle - in chest E side of ruins underground behind illusory floor"
        ]
    ),
    # liurnia dungeons
    ERBossInfo("Crystalians (LL/ACC)", ["Liurnia of The Lakes", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "LL/(ACC): Crystal Release - boss drop"
        ]
    ),
    ERBossInfo("Spirit-Caller Snail (LL/REC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LL/(REC): Glintstone Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Cemetery Shade (LL/BKC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LL/(BKC): Twinsage Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin (LL/BKC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LL/(BKC): Assassin's Cerulean Dagger - alt boss drop",
            "LL/(BKC): Black Knifeprint - alt boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog (LL/CC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 0, dungeon=True,
        locations=[
            "LL/(CC): Kaiden Sellsword Ashes - boss drop"
        ]
    ),
    ERBossInfo("Cleanrot Knight (LL/SC)", ["Liurnia of The Lakes", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "LL/(SC): Winged Sword Insignia - boss drop"
        ]
    ),
    ERBossInfo("Bloodhound Knight (LL/LCC)", ["Liurnia of The Lakes", "Dungeon", "Cave"], 0, 0, dungeon=True,
        locations=[
            "LL/(LCC): Cerulean Amber Medallion - boss drop"
        ]
    ),
    ERBossInfo("Crystalian (Ring Blade) (LL/RLCT)", ["Liurnia of The Lakes", "Dungeon", "Tunnel"], 0, 0, dungeon=True,
        locations=[
            "LL/(RLCT): Smithing-Stone Miner's Bell Bearing [1] - boss drop"
        ]
    ),
    ERBossInfo("Magma Wyrm Makar (RSP)", ["Liurnia of The Lakes", "Ruin-Strewn Precipice", "Dungeon"], 0, 0, dungeon=True,
        locations=[
            "RSP/RSPO: Magma Wyrm's Scalesword - boss drop",
            "RSP/RSPO: Dragon Heart - boss drop"
        ]
    ),
    # other
    ERBossInfo("Grafted Scion (CA)", ["Chapel of Anticipation"], 0, 0,
        locations=[
            "LL/(TFB/CA): Ornamental Straight Sword - boss drop",
            "LL/(TFB/CA): Golden Beast Crest Shield - boss drop"
        ]
    ),
    
    # MARK: SW Underground
    ERBossInfo("Dragonkin Soldier of Nokstella (AR)", ["Ainsel River", "Underground"], 0, 0,
        locations=[
            "AR/ARD: Frozen Lightning Spear - boss drop"
        ]
    ),
    ERBossInfo("Dragonkin Soldier (LR)", ["Lake of Rot", "Underground"], 0, 0,
        locations=[
            "LR/LRS: Dragonscale Blade - boss drop"
        ]
    ),
    ERBossInfo("Astel, Naturalborn of the Void (LR)", ["Lake of Rot", "Underground", "Remembrance"], 0, 0,
        locations=[
            "LR: Remembrance of the Naturalborn - mainboss drop"
        ]
    ),
    
    # MARK: Raya Lucaria Academy
    ERBossInfo("Red Wolf of Radagon", ["Raya Lucaria Academy"], 0, 0,
        locations=[
            "RLA/SC: Memory Stone - boss drop"
        ]
    ),
    ERBossInfo("Rennala, Queen of the Full Moon", ["Raya Lucaria Academy", "Remembrance", "Great Rune"], 0, 0,
        locations=[
            "RLA: Great Rune of the Unborn - mainboss drop",
            "RLA: Remembrance of the Full Moon Queen - mainboss drop"
        ]
    ),
    
    
    ERBossInfo("", [""], 0, 0,
        locations=[
        ]
    ),
    # MARK: End Game
    ERBossInfo("Sir Gideon Ofnir, The All-Knowing", ["Leyndell, Ashen Capital"], 0, 0,
        locations=[
            "LAC/LCA: Scepter of the All-Knowing - boss drop",
            "LAC/LCA: All-Knowing Helm - boss drop",
            "LAC/LCA: All-Knowing Armor - boss drop",
            "LAC/LCA: All-Knowing Gauntlets - boss drop",
            "LAC/LCA: All-Knowing Greaves - boss drop"
        ]
    ),
    ERBossInfo("Godfrey, First Elden Lord", ["Leyndell, Ashen Capital", "Remembrance"], 0, 0,
        locations=[
            "LAC/QB: Remembrance of Hoarah Loux - mainboss drop"
        ]
    ),
    ERBossInfo("Elden Beast", ["Erdtree", "Remembrance", "Final"], 0, 0,
        locations=[
            "ET: Elden Remembrance - mainboss drop"
        ]
    ),
]

dlc_bosses = [
    ERBossInfo("", [""], 0, 0,
        locations=[
        ]
    ),
    
    # MARK: Enir Ilim
    ERBossInfo("Promised Consort Radahn", ["Enir Ilim", "Remembrance", "DLC Final"], 0, 0,
        locations=[
            "EI/DGFS: Remembrance of a God and a Lord - mainboss drop"
        ]
    ),
]

for boss in dlc_bosses:
    boss.dlc = True
    
all_bosses = base_bosses + dlc_bosses