from dataclasses import dataclass, field
from typing import Optional


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
    
    allow_rykard: bool = False
    """Which bosses can be replaced by Rykard."""

    locations: list[str] = field(default_factory=list)
    """Locations the boss blocks so we can do can_get location."""

# https://github.com/vawser/Smithbox/blob/main/src/Smithbox.Data/Assets/Aliases/ER/EventFlags.json for flag id
base_bosses = [
    # MARK: Limgrave
    #ERBossInfo("Solder of Godrick", ["Limgrave"], 0, 18000850), # doesn't have an item behind it since emote spots dont count
    ERBossInfo("Tree Sentinel (LG)", ["Limgrave", "Overworld"], 0, 1042360800, allow_rykard=True,
        locations=[
            "LG/TFS: Golden Halberd - first field boss"
        ]
    ),
    ERBossInfo("Flying Dragon Agheel (LG)", ["Limgrave", "Overworld"], 0, 1043360800, allow_rykard=True,
        locations=[
            "LG/DBR: Dragon Heart - boss drop N of DBR"
        ]
    ),
    ERBossInfo("Night's Cavalry (LG)", ["Limgrave", "Overworld"], 0, 1043370800, allow_rykard=True,
        locations=[
            "LG/ALN: Ash of War: Repeating Thrust - night boss drop to SE"
        ]
    ),
    ERBossInfo("Bloodhound Knight Darriwil (LG)", ["Limgrave", "Overworld", "Evergaol"], 0, 1044350800,
        locations=[
            "LG/(FHE): Bloodhound's Fang - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Tibia Mariner (LG)", ["Limgrave", "Overworld"], 0, 1045390800, allow_rykard=True,
        locations=[
            "LG/(SWV): Deathroot - boss drop",
            "LG/(SWV): Skeletal Militiaman Ashes - boss drop"
        ]
    ),
    ERBossInfo("Mad Pumpkin Head (LG/WR)", ["Limgrave", "Overworld", "Ruin"], 0, 1044360800,
        locations=[
            "LG/(WR): Glintstone Pebble - Sellen Shop",
            "LG/(WR): Glintstone Stars - Sellen Shop",
            "LG/(WR): Crystal Barrage - Sellen Shop",
            "LG/(WR): Glintstone Arc - Sellen Shop",
            "LG/(WR): Scholar's Armament - Sellen Shop",
            "LG/(WR): Scholar's Shield - Sellen Shop",
        ]
    ),
    ERBossInfo("Crucible Knight (LG)", ["Limgrave", "Overworld", "Evergaol"], 0, 1042370800,
        locations=[
            "LG/(SE): Aspects of the Crucible: Tail - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Deathbird (LG)", ["Limgrave", "Overworld"], 0, 1042380800, allow_rykard=True,
        locations=[
            "LG/WS: Blue-Feathered Branchsword - night boss drop SE of WS"
        ]
    ),
    ERBossInfo("Bell Bearing Hunter (LG)", ["Limgrave", "Overworld"], 0, 1042380850, allow_rykard=True,
        locations=[
            "LG/(WS): Bone Peddler's Bell Bearing - night boss drop"
        ]
    ),
    # limgrave dungeons
    ERBossInfo("Ulcerated Tree Spirit (LG/FHG)", ["Limgrave", "Dungeon", "Grave"], 0, 18000800, dungeon=True, # maybe 18000800, no place name
        locations=[
            "LG/(FHG): Golden Seed - boss drop",
            "LG/(FHG): Banished Knight Oleg - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog (LG/SC)", ["Limgrave", "Dungeon", "Catacomb"], 0, 30020800, dungeon=True,
        locations=[
            "LG/(SC): Noble Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Grave Warden Duelist (LG/MCC)", ["Limgrave", "Dungeon", "Catacomb"], 0, 30040800, dungeon=True,
        locations=[
            "LG/(MCC): Banished Knight Engvall - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin (LG/DC)", ["Limgrave", "Dungeon", "Catacomb"], 0, 30110800, dungeon=True,
        locations=[
            "LG/(DC): Assassin's Crimson Dagger - boss drop"
        ]
    ),
    ERBossInfo("Beastman of Farum Azula (LG/GC)", ["Limgrave", "Dungeon", "Cave"], 0, 31030800, dungeon=True,
        locations=[
            "LG/(GC): Flamedrake Talisman - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Chief (LG/CC)", ["Limgrave", "Dungeon", "Cave"], 0, 31150800, dungeon=True,
        locations=[
            "LG/(CC): Tailoring Tools - boss drop",
            "LG/(CC): Sewing Needle - boss drop"
        ]
    ),
    ERBossInfo("Guardian Golem (LG/HC)", ["Limgrave", "Dungeon", "Cave"], 0, 31170800, dungeon=True,
        locations=[
            "LG/(HC): Blue Dancer Charm - boss drop"
        ]
    ),
    ERBossInfo("Stonedigger Troll (LG/LT)", ["Limgrave", "Dungeon", "Tunnel"], 0, 32010800, dungeon=True,
        locations=[
            "LG/(LT): Roar Medallion - boss drop"
        ]
    ),
    
    # MARK: Stormveil
    ERBossInfo("Margit, the Fell Omen (SV)", ["Stormveil Castle", "Main"], 0, 10000850, allow_rykard=True,
        locations=[
            "SV/CT: Talisman Pouch - boss drop" # + the entire castle, but im not doing all that
        ]
    ),
    ERBossInfo("Godrick the Grafted (SV)", ["Stormveil Castle", "Remembrance", "Great Rune", "Main"], 0, 10000800, allow_rykard=True,
        locations=[
            "SV/SeC: Godrick's Great Rune - mainboss drop",
            "SV/SeC: Remembrance of the Grafted - mainboss drop"
        ]
    ),

    # MARK: Weeping Peninsula
    ERBossInfo("Ancient Hero of Zamor (WP)", ["Weeping Peninsula", "Overworld", "Evergaol"], 0, 1042330800,
        locations=[
            "WP/(WE): Radagon's Scarseal - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Leonine Misbegotten (WP/CM)", ["Weeping Peninsula", "Castle Morne", "Overworld"], 0, 1043300800, allow_rykard=True,
        locations=[
            "WP/(CM): Grafted Blade Greatsword - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Avatar (WP)", ["Weeping Peninsula", "Overworld"], 0, 1043330800, allow_rykard=True,
        locations=[
            "WP/ME: Opaline Bubbletear - boss drop",
            "WP/ME: Crimsonburst Crystal Tear - boss drop"
        ]
    ),
    ERBossInfo("Deathbird (WP)", ["Weeping Peninsula", "Overworld"], 0, 1044320800, allow_rykard=True,
        locations=[
            "WP/CMR: Sacrificial Axe - night boss drop far to SW"
        ]
    ),
    ERBossInfo("Night's Cavalry (WP)", ["Weeping Peninsula", "Overworld"], 0, 1044320850, allow_rykard=True,
        locations=[
            "WP/CMR: Nightrider Flail - night boss drop to SW",
            "WP/CMR: Ash of War: Barricade Shield - night boss drop to SW"
        ]
    ),
    # weeping dungeons
    ERBossInfo("Cemetery Shade (WP/TCC)", ["Weeping Peninsula", "Dungeon", "Catacomb"], 0, 30000800, dungeon=True,
        locations=[
            "WP/(TCC): Lhutel the Headless - boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog (WP/IC)", ["Weeping Peninsula", "Dungeon", "Catacomb"], 0, 30010800, dungeon=True,
        locations=[
            "WP/(IC): Demi-Human Ashes - boss drop"
        ]
    ),
    ERBossInfo("Runebear (WP/EC)", ["Weeping Peninsula", "Dungeon", "Cave"], 0, 31010800, dungeon=True,
        locations=[
            "WP/(EC): Spelldrake Talisman - boss drop"
        ]
    ),
    ERBossInfo("Miranda the Blighted Bloom (WP/TCV)", ["Weeping Peninsula", "Dungeon", "Cave"], 0, 31020800, dungeon=True,
        locations=[
            "WP/(TCV): Viridian Amber Medallion - boss drop"
        ]
    ),
    ERBossInfo("Scaly Misbegotten (WP/MT)", ["Weeping Peninsula", "Dungeon", "Tunnel"], 0, 32000800, dungeon=True,
        locations=[
            "WP/(MT): Rusted Anchor - boss drop"
        ]
    ),
    
    # MARK: SE Underground
    ERBossInfo("Ancestor Spirit (SR)", ["Siofra River", "Underground"], 0, 12080800, allow_rykard=True,
        locations=[
            "SR/(HG): Ancestral Follower Ashes - boss drop"
        ]
    ),
    ERBossInfo("Dragonkin Soldier (SR)", ["Siofra River", "Underground"], 0, 12020830, allow_rykard=True,
        locations=[
            "SR/WW: Dragon Halberd - upper siofra, boss drop"
        ]
    ),
    ERBossInfo("Mimic Tear (NR)", ["Nokron, Eternal City", "Underground"], 0, 12020850, allow_rykard=True,
        locations=[
            "NR/NEC: Silver Tear Mask - boss drop",
            "NR/NEC: Larval Tear x2 - boss drop"
        ]
    ),
    ERBossInfo("Valiant Gargoyles (NR)", ["Nokron, Eternal City", "Underground"], 0, 12020800, allow_rykard=True,
        locations=[
            "NR/(SA): Gargoyle's Greatsword - boss drop",
            "NR/(SA): Gargoyle's Twinblade - boss drop",
        ]
    ),
    ERBossInfo("Regal Ancestor Spirit (NR)", ["Nokron, Eternal City", "Underground", "Remembrance"], 0, 12090800, allow_rykard=True,
        locations=[
            "NR/(HG): Remembrance of the Regal Ancestor - boss drop"
        ]
    ),
    
    # MARK: N Underground
    ERBossInfo("Crucible Knight Siluria (DD)", ["Deeproot Depths", "Underground"], 0, 12020390, allow_rykard=True, # maybe
        locations=[
            "DD/TNEC: Siluria's Tree - boss drop way to W by tree stump"
        ]
    ),
    ERBossInfo("Fia's Champions (DD)", ["Deeproot Depths", "Underground"], 0, 12030800, allow_rykard=True,
        locations=[
            "DD/AR: Fia's Mist - boss drop"
        ]
    ),
    # ERBossInfo("Lichdragon Fortissax (DD)", ["Deeproot Depths", "Underground", "Remembrance"], 0, 12030850, allow_rykard=True,
    #     locations=[
    #         "DD/PDT: Remembrance of the Lichdragon - mainboss drop"
    #     ]
    # ), # uncomment once made unmissable
    
    # MARK: Liurnia of The Lakes
    ERBossInfo("Erdtree Avatar (LL/MEW)", ["Liurnia of The Lakes", "Overworld"], 0, 1033430800, allow_rykard=True,
        locations=[
            "LL/MEW: Cerulean Crystal Tear - boss drop, Minor Erdtree W",
            "LL/MEW: Ruptured Crystal Tear - boss drop, Minor Erdtree W"
        ]
    ),
    ERBossInfo("Bols, Carian Knight (LL)", ["Liurnia of The Lakes", "Overworld", "Evergaol"], 0, 1033450800,
        locations=[
            "LL/(CE): Greatblade Phalanx - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Glintstone Dragon Smarag (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1034450800, allow_rykard=True,
        locations=[
            "LL/TQ: Dragon Heart - boss drop to N"
        ]
    ),
    ERBossInfo("Omenkiller (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1035420800,
        locations=[
            "LL/(VA): Crucible Knot Talisman - boss drop"
        ]
    ),
    ERBossInfo("Loretta, Royal Knight (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1035500800, allow_rykard=True,
        locations=[
            "LL/(CM): Loretta's Greatbow - boss drop",
            "LL/(CM): Ash of War: Loretta's Slash - boss drop"
        ]
    ),
    ERBossInfo("Death Rite Bird (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1036450340, allow_rykard=True,
        locations=[
            "LL/GTN: Ancient Death Rancor - night boss drop to S"
        ]
    ),
    ERBossInfo("Deathbird (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1037420340, allow_rykard=True,
        locations=[
            "LL/SeI: Red-Feathered Branchsword - night boss drop to NE"
        ]
    ),
    ERBossInfo("Bell Bearing Hunter (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1037460800, allow_rykard=True,
        locations=[
            "LL/(CV): Meat Peddler's Bell Bearing - night boss drop"
        ]
    ),
    ERBossInfo("Adan, Thief of Fire (LL)", ["Liurnia of The Lakes", "Overworld", "Evergaol"], 0, 1038410800, allow_rykard=True,
        locations=[
            "LL/(ME): Flame of the Fell God - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Night's Cavalry (LL/GTB)", ["Liurnia of The Lakes", "Overworld"], 0, 1036480340, allow_rykard=True,
        locations=[
            "LL/GTB: Ash of War: Ice Spear - night boss drop to SE"
        ]
    ),
    ERBossInfo("Tibia Mariner (LL)", ["Liurnia of The Lakes", "Overworld"], 0, 1039440800, allow_rykard=True,
        locations=[
            "LL/AS: Deathroot - boss drop SE of AS",
            "LL/AS: Skeletal Bandit Ashes - boss drop SE of AS"
        ]
    ),
    ERBossInfo("Night's Cavalry (LL/BC)", ["Liurnia of The Lakes", "Overworld"], 0, 1039430340, allow_rykard=True,
        locations=[
            "LL/BC: Nightrider Glaive - night boss drop S of BC",
            "LL/BC: Ash of War: Giant Hunt - night boss drop S of BC"
        ]
    ),
    ERBossInfo("Erdtree Avatar (LL/MEE)", ["Liurnia of The Lakes", "Overworld"], 0, 1038480800, allow_rykard=True,
        locations=[
            "LL/MEE: Magic-Shrouding Cracked Tear - boss drop, Minor Erdtree E",
            "LL/MEE: Lightning-Shrouding Cracked Tear - boss drop, Minor Erdtree E",
            "LL/MEE: Holy-Shrouding Cracked Tear - boss drop, Minor Erdtree E"
        ]
    ),
    ERBossInfo("Onyx Lord (LL)", ["Liurnia of The Lakes", "Overworld", "Evergaol"], 0, 1036500800,
        locations=[
            "LL/(RGE): Meteorite - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Royal Revenant (LL/KR)", ["Liurnia of The Lakes", "Overworld", "Ruin"], 0, 1034480800,
        locations=[
            "LL/(KR): Frozen Needle - in chest E side of ruins underground behind illusory floor"
        ]
    ),
    # liurnia dungeons
    ERBossInfo("Crystalians (LL/ACC)", ["Liurnia of The Lakes", "Dungeon", "Cave"], 0, 31060800, dungeon=True,
        locations=[
            "LL/(ACC): Crystal Release - boss drop"
        ]
    ),
    ERBossInfo("Spirit-Caller Snail (LL/REC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 30030800, dungeon=True,
        locations=[
            "LL/(REC): Glintstone Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Cemetery Shade (LL/BKC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 30050800, dungeon=True,
        locations=[
            "LL/(BKC): Twinsage Sorcerer Ashes - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin (LL/BKC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 30050850, dungeon=True,
        locations=[
            "LL/(BKC): Assassin's Cerulean Dagger - alt boss drop",
            "LL/(BKC): Black Knifeprint - alt boss drop"
        ]
    ),
    ERBossInfo("Erdtree Burial Watchdog (LL/CC)", ["Liurnia of The Lakes", "Dungeon", "Catacomb"], 0, 30060800, dungeon=True,
        locations=[
            "LL/(CC): Kaiden Sellsword Ashes - boss drop"
        ]
    ),
    ERBossInfo("Cleanrot Knight (LL/SC)", ["Liurnia of The Lakes", "Dungeon", "Cave"], 0, 31040800, dungeon=True,
        locations=[
            "LL/(SC): Winged Sword Insignia - boss drop"
        ]
    ),
    ERBossInfo("Bloodhound Knight (LL/LCC)", ["Liurnia of The Lakes", "Dungeon", "Cave"], 0, 31050800, dungeon=True,
        locations=[
            "LL/(LCC): Cerulean Amber Medallion - boss drop"
        ]
    ),
    ERBossInfo("Crystalian - Ring Blade (LL/RLCT)", ["Liurnia of The Lakes", "Dungeon", "Tunnel"], 0, 32020800, dungeon=True,
        locations=[
            "LL/(RLCT): Smithing-Stone Miner's Bell Bearing [1] - boss drop"
        ]
    ),
    ERBossInfo("Magma Wyrm Makar (RSP)", ["Liurnia of The Lakes", "Ruin-Strewn Precipice", "Dungeon", "Main"], 0, 39200800, dungeon=True, allow_rykard=True,
        locations=[
            "RSP/RSPO: Magma Wyrm's Scalesword - boss drop",
            "RSP/RSPO: Dragon Heart - boss drop"
        ]
    ),
    # other
    ERBossInfo("Grafted Scion (CA)", ["Chapel of Anticipation"], 0, 10010800, allow_rykard=True,
        locations=[
            "LL/(TFB/CA): Ornamental Straight Sword - boss drop",
            "LL/(TFB/CA): Golden Beast Crest Shield - boss drop"
        ]
    ),
    
    # MARK: SW Underground
    ERBossInfo("Dragonkin Soldier of Nokstella (AR)", ["Ainsel River", "Underground"], 0, 12010800, allow_rykard=True,
        locations=[
            "AR/ARD: Frozen Lightning Spear - boss drop"
        ]
    ),
    ERBossInfo("Dragonkin Soldier (LR)", ["Lake of Rot", "Underground"], 0, 12010850, allow_rykard=True,
        locations=[
            "LR/LRS: Dragonscale Blade - boss drop"
        ]
    ),
    ERBossInfo("Astel, Naturalborn of the Void (LR)", ["Lake of Rot", "Underground", "Remembrance"], 0, 12040800, allow_rykard=True,
        locations=[
            "LR: Remembrance of the Naturalborn - mainboss drop"
        ]
    ),
    
    # MARK: Moonlight Altar
    ERBossInfo("Alecto, Black Knife Ringleader (MA)", ["Moonlight Altar", "Evergaol"], 0, 1033420800,
        locations=[
            "MA/(RE): Black Knife Tiche - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Glintstone Dragon Adula (MA)", ["Moonlight Altar"], 0, 1034420800, allow_rykard=True,
        locations=[
            "MA/MA: Adula's Moonblade - boss drop to NE",
            "MA/MA: Dragon Heart x3 - boss drop to NE"
        ]
    ),
    
    # MARK: Raya Lucaria Academy
    ERBossInfo("Red Wolf of Radagon (RLA)", ["Raya Lucaria Academy", "Main"], 0, 14000850, allow_rykard=True,
        locations=[
            "RLA/SC: Memory Stone - boss drop"
        ]
    ),
    ERBossInfo("Rennala, Queen of the Full Moon (RLA)", ["Raya Lucaria Academy", "Remembrance", "Great Rune", "Main"], 0, 14000800, allow_rykard=True,
        locations=[
            "RLA: Great Rune of the Unborn - mainboss drop",
            "RLA: Remembrance of the Full Moon Queen - mainboss drop"
        ]
    ),
    
    # MARK: Caelid
    ERBossInfo("Erdtree Avatar (CL)", ["Caelid", "Overworld"], 0, 1047400800, allow_rykard=True,
        locations=[
            "CL/MEW: Greenburst Crystal Tear - boss drop",
            "CL/MEW: Flame-Shrouding Cracked Tear - boss drop"
        ]
    ),
    ERBossInfo("Decaying Ekzykes (CL)", ["Caelid", "Overworld"], 0, 1048370800, allow_rykard=True,
        locations=[
            "CL/CHS: Dragon Heart - boss drop to SE"
        ]
    ),
    ERBossInfo("Mad Pumpkin Head Duo (CL/CR)", ["Caelid", "Overworld", "Ruin"], 0, 1048400800,
        locations=[
            "CL/(CR): Visage Shield - in chest after boss"
        ]
    ),
    ERBossInfo("Night's Cavalry (CL)", ["Caelid", "Overworld"], 0, 1049370800, allow_rykard=True,
        locations=[
            "CL/SASB: Ash of War: Poison Moth Flight - night boss drop to SW"
        ]
    ),
    ERBossInfo("Death Rite Bird (CL)", ["Caelid", "Overworld"], 0, 1049370850, allow_rykard=True,
        locations=[
            "CL/SASB: Death's Poker - night boss drop to SE"
        ]
    ),
    ERBossInfo("Commander O'Neil (CL)", ["Caelid", "Overworld"], 0, 1049380800, allow_rykard=True,
        locations=[
            "CL/IA: Commander's Standard - boss drop to SE",
            "CL/IA: Unalloyed Gold Needle (Broken) - boss drop to SE"
        ]
    ),
    ERBossInfo("Nox Swordstress & Nox Priest (CL)", ["Caelid", "Overworld"], 0, 1049390800, allow_rykard=True,
        locations=[
            "CL/(STS): Nox Flowing Sword - boss drop",
            "CL/(STS): Lusat's Glintstone Staff - in chest after boss"
        ]
    ),
    # caelid dungeons
    ERBossInfo("Erdtree Burial Watchdog (CL/MEC)", ["Caelid", "Dungeon", "Catacomb"], 0, 30140800, dungeon=True,
        locations=[
            "CL/(MEC): Mad Pumpkin Head Ashes - boss drop"
        ]
    ),
    ERBossInfo("Cemetery Shade (CL/CCC)", ["Caelid", "Dungeon", "Catacomb"], 0, 30150800, dungeon=True,
        locations=[
            "CL/(CCC): Kindred of Rot Ashes - boss drop"
        ]
    ),
    ERBossInfo("Putrid Tree Spirit (CL/WDC)", ["Caelid", "Dungeon", "Catacomb"], 0, 30160800, dungeon=True,
        locations=[
            "CL/(WDC): Golden Seed - boss drop",
            "CL/(WDC): Redmane Knight Ogha - boss drop"
        ]
    ),
    ERBossInfo("Cleanrot Knight Duo (CL/AC)", ["Caelid", "Dungeon", "Cave"], 0, 31200800, dungeon=True,
        locations=[
            "CL/(AC): Gold Scarab - boss drop"
        ]
    ),
    ERBossInfo("Frenzied Duelist (CL/GC)", ["Caelid", "Dungeon", "Cave"], 0, 31210800, dungeon=True,
        locations=[
            "CL/(GC): Putrid Corpse Ashes - boss drop"
        ]
    ),
    ERBossInfo("Magma Wyrm (CL/GT)", ["Caelid", "Dungeon", "Tunnel"], 0, 32070800, dungeon=True,
        locations=[
            "CL/(GT): Moonveil - boss drop",
            "CL/(GT): Dragon Heart - boss drop"
        ]
    ),
    ERBossInfo("Fallingstar Beast (CL/SCT)", ["Caelid", "Dungeon", "Tunnel"], 0, 32080800, dungeon=True,
        locations=[
            "CL/(SCT): Gravity Stone Chunk x10 - boss drop",
            "CL/(SCT): Somberstone Miner's Bell Bearing [1] - boss drop",
            "CL/(SCT): Smithing Stone [7] x5 - boss drop",
            "CL/(SCT): Somber Smithing Stone [6] - boss drop"
        ]
    ),
    
    # Redmane Castle
    ERBossInfo("Crucible Knight / Misbegotten Warrior (CL/RC)", ["Caelid", "Overworld"], 0, 1051360800,
        locations=[
            "CL/(RC): Ruins Greatsword - boss drop"
        ]
    ),
    ERBossInfo("Starscourge Radahn (CL)", ["Caelid", "Overworld", "Remembrance", "Great Rune", "Main"], 0, 1252380800, allow_rykard=True,
        locations=[
            "CL/(WD): Radahn's Great Rune - mainboss drop",
            "CL/(WD): Remembrance of the Starscourge - mainboss drop"
        ]
    ),
    
    # MARK: Dragonbarrow
    ERBossInfo("Bell Bearing Hunter (DB)", ["Dragonbarrow", "Overworld"], 0, 1048410800, allow_rykard=True,
        locations=[
            "DB/(IMS): Gravity Stone Peddler's Bell Bearing - night boss drop"
        ]
    ),
    ERBossInfo("Battlemage Hugues (DB)", ["Dragonbarrow", "Overworld", "Evergaol"], 0, 1049390850, allow_rykard=True,
        locations=[
            "DB/(SE): Battlemage Hugues - Sellia Evergaol"
        ]
    ),
    ERBossInfo("Putrid Avatar (DB)", ["Dragonbarrow", "Overworld"], 0, 1051400800, allow_rykard=True,
        locations=[
            "DB/MEE: Opaline Hardtear - boss drop",
            "DB/MEE: Stonebarb Cracked Tear - boss drop"
        ]
    ),
    ERBossInfo("Black Blade Kindred (DB)", ["Dragonbarrow", "Overworld"], 0, 1051430800, allow_rykard=True,
        locations=[
            "DB/BS: Gargoyle's Blackblade - boss drop SE of BS",
            "DB/BS: Gargoyle's Black Halberd - boss drop SE of BS"
        ]
    ),
    ERBossInfo("Flying Dragon Greyll (DB)", ["Dragonbarrow", "Overworld"], 0, 1052410800, allow_rykard=True,
        locations=[
            "DB/FG: Dragon Heart - boss drop to S"
        ]
    ),
    ERBossInfo("Night's Cavalry (DB)", ["Dragonbarrow", "Overworld"], 0, 1052410850, allow_rykard=True,
        locations=[
            "DB/LR: Ash of War: Bloodhound's Step - night boss drop N of LR"
        ]
    ),
    # dragonbarrow dungeons
    ERBossInfo("Beastman of Farum Azula (DB/DC)", ["Dragonbarrow", "Dungeon", "Cave"], 0, 31100800, dungeon=True,
        locations=[
            "DB/(DC): Flamedrake Talisman +2 - boss drop"
        ]
    ),
    ERBossInfo("Crystalians - Trio (DB/SH)", ["Dragonbarrow", "Dungeon", "Cave"], 0, 31110800, dungeon=True,
        locations=[
            "DB/(SH): Crystal Torrent - boss drop"
        ]
    ),
    ERBossInfo("Godskin Apostle (DB/DT)", ["Dragonbarrow", "Dungeon", "Tunnel"], 0, 34130800, dungeon=True,
        locations=[
            "DB/(DT): Godskin Apostle Hood - boss drop",
            "DB/(DT): Godskin Apostle Robe - boss drop",
            "DB/(DT): Godskin Apostle Bracelets - boss drop",
            "DB/(DT): Godskin Apostle Trousers - boss drop",
        ]
    ),

    # MARK: Altus Plateau
    ERBossInfo("Ancient Dragon Lansseax (AP)", ["Altus Plateau", "Overworld"], 0, 1041520800, allow_rykard=True, # early altus 1037510800   late altus 1041520800
        locations=[
            "AP/RP: Lansseax's Glaive - boss drop up hill to SW or NE of AC grace"
        ]
    ),
    ERBossInfo("Tibia Mariner (AP)", ["Altus Plateau", "Overworld"], 0, 1038520800, allow_rykard=True,
        locations=[
            "AP/WhR: Deathroot - boss drop",
            "AP/WhR: Tibia's Summons - boss drop"
        ]
    ),
    ERBossInfo("Godefroy the Grafted (AP)", ["Altus Plateau", "Overworld", "Evergaol"], 0, 1039500800,
        locations=[
            "AP/GLE: Godfrey Icon - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Night's Cavalry (AP)", ["Altus Plateau", "Overworld"], 0, 1039510800, allow_rykard=True,
        locations=[
            "AP/AHJ: Ash of War: Shared Order - night boss drop to SW"
        ]
    ),
    ERBossInfo("Elemer of the Briar (AP)", ["Altus Plateau", "The Shaded Castle"], 0, 1039540800,
        locations=[
            "TSC/SCIG: Marais Executioner's Sword - boss drop",
            "TSC/SCIG: Briar Greatshield - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin (AP)", ["Altus Plateau", "Overworld"], 0, 1040520800, allow_rykard=True,
        locations=[
            "AP/SHG: Black Knife - boss drop guarding SHG"
        ]
    ),
    ERBossInfo("Sanguine Noble (AP/WbR)", ["Altus Plateau", "Overworld", "Ruin"], 0, 1040530800,
        locations=[
            "AP/(WbR): Bloody Helice - in chest after boss underground"
        ]
    ),
    ERBossInfo("Fallingstar Beast (AP)", ["Altus Plateau", "Overworld"], 0, 1041500800, allow_rykard=True,
        locations=[
            "AP/AHJ: Gravity Stone Chunk x10 - boss drop S of great stairs in meteor crater",
            "AP/AHJ: Smithing Stone [6] x5 - boss drop S of great stairs in meteor crater",
            "AP/AHJ: Somber Smithing Stone [5] - boss drop S of great stairs in meteor crater"
        ]
    ),
    ERBossInfo("Tree Sentinels (AP)", ["Altus Plateau", "Overworld"], 0, 1041510800, allow_rykard=True,
        locations=[
            "AP/AHJ: Erdtree Greatshield - boss drop duo to E top of great stairs",
            "AP/AHJ: Hero's Rune [1] - boss drop duo to E top of great stairs",
        ]
    ),
    ERBossInfo("Wormface (AP)", ["Altus Plateau", "Overworld"], 0, 1041530800, allow_rykard=True,
        locations=[
            "AP/ME: Crimsonspill Crystal Tear - boss drop, Minor Erdtree",
            "AP/ME: Speckled Hardtear - boss drop, Minor Erdtree"
        ]
    ),
    ERBossInfo("Godskin Apostle (AP)", ["Altus Plateau", "Overworld"], 0, 1042550800, allow_rykard=True,
        locations=[
            "AP/(DWV): Godskin Peeler - boss drop",
            "AP/(DWV): Scouring Black Flame - boss drop"
        ]
    ),
    # altus dungeons
    ERBossInfo("Ancient Hero of Zamor (AP/SHG)", ["Altus Plateau", "Dungeon", "Grave"], 0, 30080800, dungeon=True,
        locations=[
            "AP/(SHG): Ancient Dragon Knight Kristoff - boss drop"
        ]
    ),
    ERBossInfo("Perfumer Tricia & Misbegotten Warrior (AP/UC)", ["Altus Plateau", "Dungeon", "Catacomb"], 0, 30120800, dungeon=True,
        locations=[
            "AP/(UC): Perfumer Tricia - boss drop"
        ]
    ),
    ERBossInfo("Omenkiller & Miranda the Blighted Bloom (AP/PG)", ["Altus Plateau", "Dungeon", "Cave"], 0, 31180800, dungeon=True,
        locations=[
            "AP/(PG): Great Omenkiller Cleaver - boss drop"
        ]
    ),
    ERBossInfo("Black Knife Assassin (AP/SC)", ["Altus Plateau", "Dungeon", "Cave"], 0, 31190800, dungeon=True,
        locations=[
            "AP/(SC): Concealing Veil - boss drop"
        ]
    ),
    ERBossInfo("Necromancer Garris (AP/SC)", ["Altus Plateau", "Dungeon", "Cave"], 0, 31190850, dungeon=True,
        locations=[
            "AP/(SC): Family Heads - hidden boss drop"
        ]
    ),
    ERBossInfo("Stonedigger Troll (AP/OAT)", ["Altus Plateau", "Dungeon", "Tunnel"], 0, 32040800, dungeon=True,
        locations=[
            "AP/(OAT): Great Club - boss drop"
        ]
    ),
    ERBossInfo("Crystalians - Ringblade/Spear (AP/AT)", ["Altus Plateau", "Dungeon", "Tunnel"], 0, 32050800, dungeon=True,
        locations=[
            "AP/(AT): Somberstone Miner's Bell Bearing [2] - boss drop"
        ]
    ),
   
    # MARK: Capital Outskirts
    ERBossInfo("Deathbird (CO)", ["Capital Outskirts", "Overworld"], 0, 1044530800, allow_rykard=True,
        locations=[
            "CO/HMS: Twinbird Kite Shield - night boss drop to NE in block flower field"
        ]
    ),
    ERBossInfo("Bell Bearing Hunter (CO)", ["Capital Outskirts", "Overworld"], 0, 1043530800, allow_rykard=True,
        locations=[
            "CO/(HMS): Medicine Peddler's Bell Bearing - night boss drop"
        ]
    ),
    ERBossInfo("Draconic Tree Sentinel (CO)", ["Capital Outskirts", "Overworld", "Main"], 0, 1045520800, allow_rykard=True,
        locations=[
            "CO: Dragon Greatclaw - capital great rune gate boss drop",
            "CO: Dragonclaw Shield - capital great rune gate boss drop"
        ]
    ),
    # capital outskirts dungeons
    ERBossInfo("Crucible Knight & Crucible Knight Ordovis (CO/AHG)", ["Capital Outskirts", "Dungeon", "Grave"], 0, 30100800, dungeon=True,
        locations=[
            "CO/(AHG): Ordovis's Greatsword - boss drop",
            "CO/(AHG): Crucible Axe Helm - boss drop",
            "CO/(AHG): Crucible Axe Armor - boss drop",
            "CO/(AHG): Crucible Gauntlets - boss drop",
            "CO/(AHG): Crucible Greaves - boss drop"
        ]
    ),
    ERBossInfo("Grave Warden Duelist (CO/AST)", ["Capital Outskirts", "Dungeon", "Catacomb"], 0, 30130800, dungeon=True,
        locations=[
            "CO/(AST): Soldjars of Fortune Ashes - boss drop"
        ]
    ),
    ERBossInfo("Onyx Lord (CO/ST)", ["Capital Outskirts", "Dungeon", "Tunnel"], 0, 34120800, dungeon=True,
        locations=[
            "CO/(ST): Onyx Lord's Greatsword - boss drop"
        ]
    ),
    
    # MARK: Mt. Gelmir
    ERBossInfo("Magma Wyrm (MtG)", ["Mt. Gelmir", "Overworld"], 0, 1035530800, allow_rykard=True,
        locations=[
            "MtG/FL: Dragon Heart - boss drop S of FL in magma lake"
        ]
    ),
    ERBossInfo("Full-Grown Fallingstar Beast (MtG)", ["Mt. Gelmir", "Overworld"], 0, 1036540800, allow_rykard=True,
        locations=[
            "MtG/NMGC: Fallingstar Beast Jaw - boss drop",
            "MtG/NMGC: Smithing Stone [6] x5 - boss drop",
            "MtG/NMGC: Somber Smithing Stone [6] - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Queen Maggie (MtG)", ["Mt. Gelmir", "Overworld"], 0, 1037530800, allow_rykard=True,
        locations=[
            "MtG/PSA: Memory Stone - boss drop to S"
        ]
    ),
    ERBossInfo("Ulcerated Tree Spirit (MtG)", ["Mt. Gelmir", "Overworld"], 0, 1037540810, allow_rykard=True,
        locations=[
            "MtG/ME: Leaden Hardtear - boss drop, Minor Erdtree",
            "MtG/ME: Cerulean Hidden Tear - boss drop, Minor Erdtree"
        ]
    ),
    # gelmir dungeons
    ERBossInfo("Erdtree Burial Watchdog (MtG/WC)", ["Mt. Gelmir", "Dungeon", "Catacomb"], 0, 30070800, dungeon=True,
        locations=[
            "MtG/(WC): Glovewort Picker's Bell Bearing [1] - boss drop"
        ]
    ),
    ERBossInfo("Red Wolf of the Champion (MtG/GHG)", ["Mt. Gelmir", "Dungeon", "Grave"], 0, 30090800, dungeon=True,
        locations=[
            "MtG/(GHG): Bloodhound Knight Floh - boss drop"
        ]
    ),
    ERBossInfo("Kindred of Rot (MtG/SC)", ["Mt. Gelmir", "Dungeon", "Cave"], 0, 31070800, dungeon=True,
        locations=[
            "MtG/(SC): Kindred of Rot's Exultation - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Queen Margot (MtG/VC)", ["Mt. Gelmir", "Dungeon", "Cave"], 0, 31090800, dungeon=True,
        locations=[
            "MtG/(VC): Jar Cannon - boss drop"
        ]
    ),
    
    # MARK: Volcano Manor
    ERBossInfo("Rykard, Lord of Blasphemy (VM)", ["Volcano Manor", "Remembrance", "Great Rune", "Main"], 0, 16000800,
        locations=[
            "VM/AP: Rykard's Great Rune - mainboss drop",
            "VM/AP: Remembrance of the Blasphemous - mainboss drop"
        ]
    ),
    ERBossInfo("Abductor Virgins (VM)", ["Volcano Manor", "Dungeon"], 0, 16000860, dungeon=True, allow_rykard=True,
        locations=[
            "(VM)/SIC: Inquisitor's Girandole - boss drop, from RLA warp"
        ]
    ),
    ERBossInfo("Godskin Noble (VM)", ["Volcano Manor", "Main"], 0, 16000850, allow_rykard=True,
        locations=[
            "VM/GH: Godskin Stitcher - boss drop",
            "VM/GH: Noble Presence - boss drop"
        ]
    ),
    
    # MARK: Leyndell, Royal Capital
    ERBossInfo("Godfrey, First Elden Lord (LRC)", ["Leyndell, Royal Capital", "Main"], 0, 11000850, allow_rykard=True,
        locations=[
            "LRC/WCR: Talisman Pouch - mainboss drop"
        ]
    ),
    ERBossInfo("Morgott, The Omen King (LRC)", ["Leyndell, Royal Capital", "Remembrance", "Great Rune", "Main"], 0, 11000800, allow_rykard=True,
        locations=[
            "LRC/QB: Morgott's Great Rune - mainboss drop",
            "LRC/QB: Remembrance of the Omen King - mainboss drop"
        ]
    ),
    
    # MARK: Subterranean Shunning-Grounds
    ERBossInfo("Mohg, the Omen (SSG)", ["Subterranean Shunning-Grounds"], 0, 35000800,
        locations=[
            "SSG/FD: Bloodflame Talons - boss drop"
        ]
    ),
    ERBossInfo("Esgar, Priest of Blood (SSG/LC)", ["Subterranean Shunning-Grounds", "Dungeon", "Catacomb"], 0, 35000850, dungeon=True,
        locations=[
            "SSG/(LC): Lord of Blood's Exultation - boss drop"
        ]
    ),
    
    # MARK: Forbidden Lands
    ERBossInfo("Fell Twins (FL)", ["Forbidden Lands", "Overworld"], 0, 34140850, allow_rykard=True,
        locations=[
            "DTEA: Omenkiller Rollo - boss drop on way to divine tower"
        ]
    ),
    ERBossInfo("Night's Cavalry (FL)", ["Forbidden Lands", "Overworld"], 0, 1048510800, allow_rykard=True,
        locations=[
            "FL/FL: Ash of War: Phantom Slash - night boss drop to E"
        ]
    ),
    ERBossInfo("Black Blade Kindred (FL)", ["Forbidden Lands", "Overworld"], 0, 1049520800, allow_rykard=True,
        locations=[
            "FL/GLR: Gargoyle's Black Blades - boss drop to S",
            "FL/GLR: Gargoyle's Black Axe - boss drop to S"
        ]
    ),
    
    # MARK: Mountaintops of the Giants
    ERBossInfo("Death Rite Bird (MotG)", ["Mountaintops of the Giants", "Overworld"], 0, 1050570800, allow_rykard=True,
        locations=[
            "MotG/CSMG: Death Ritual Spear - boss drop to W by statue"
        ]
    ),
    ERBossInfo("Commander Niall (MotG/CS)", ["Mountaintops of the Giants", "Overworld", "Main"], 0, 1051570800,
        locations=[
            "MotG/(CS): Veteran's Prosthesis - mainboss drop",
            "MotG/(CS): Haligtree Secret Medallion (Left) - after boss"
        ]
    ),
    ERBossInfo("Erdtree Avatar (MotG)", ["Mountaintops of the Giants", "Overworld"], 0, 1052560800, allow_rykard=True,
        locations=[
            "MotG/(ME): Cerulean Crystal Tear - boss drop",
            "MotG/(ME): Crimson Bubbletear - boss drop"
        ]
    ),
    ERBossInfo("Roundtable Knight Vyke (MotG)", ["Mountaintops of the Giants", "Overworld", "Evergaol"], 0, 1053560800,
        locations=[
            "MotG/(LCE): Fingerprint Helm - boss drop Evergaol",
            "MotG/(LCE): Fingerprint Armor - boss drop Evergaol",
            "MotG/(LCE): Fingerprint Gauntlets - boss drop Evergaol",
            "MotG/(LCE): Fingerprint Greaves - boss drop Evergaol",
            "MotG/(LCE): Vyke's Dragonbolt - boss drop Evergaol"
        ]
    ),
    ERBossInfo("Borealis the Freezing Fog (MotG)", ["Mountaintops of the Giants", "Overworld"], 0, 1254560800, allow_rykard=True,
        locations=[
            "MotG/FR: Dragon Heart - boss drop to SE"
        ]
    ),
    ERBossInfo("Fire Giant (FP)", ["Mountaintops of the Giants", "Overworld", "Remembrance", "Main"], 0, 1052520800, allow_rykard=True,
        locations=[
            "FP/FF: Remembrance of the Fire Giant - mainboss drop"
        ]
    ),
    # mountain dungeons
    ERBossInfo("Ancient Hero of Zamor (FP/GCHG)", ["Mountaintops of the Giants", "Dungeon", "Grave"], 0, 30170800, dungeon=True,
        locations=[
            "FP/(GCHG): Zamor Curved Sword - boss drop",
            "FP/(GCHG): Zamor Mask - boss drop",
            "FP/(GCHG): Zamor Armor - boss drop",
            "FP/(GCHG): Zamor Bracelets - boss drop",
            "FP/(GCHG): Zamor Legwraps - boss drop"
        ]
    ),
    ERBossInfo("Ulcerated Tree Spirit (MotG/GMC)", ["Mountaintops of the Giants", "Dungeon", "Catacomb"], 0, 30180800, dungeon=True,
        locations=[
            "MotG/(GMC): Glovewort Picker's Bell Bearing [2] - boss drop",
            "MotG/(GMC): Golden Seed - boss drop"
        ]
    ),
    ERBossInfo("Spirit-Caller Snail (MotG/SC)", ["Mountaintops of the Giants", "Dungeon", "Cave"], 0, 31220800, dungeon=True,
        locations=[
            "MotG/(SC): Godskin Swaddling Cloth - boss drop",
            "MotG/(SC): Black Flame Ritual - boss drop"
        ]
    ),
    
    # MARK: Farum Azula
    ERBossInfo("Dragonlord Placidusax (FA)", ["Farum Azula", "Remembrance"], 0, 13000830, allow_rykard=True,
        locations=[
            "FA/BGB: Remembrance of the Dragonlord - alt mainboss drop"
        ]
    ),
    ERBossInfo("Maliketh, The Black Blade (FA)", ["Farum Azula", "Remembrance", "Main"], 0, 13000800, allow_rykard=True,
        locations=[
            "FA/BGB: Remembrance of the Black Blade - mainboss drop"
        ]
    ),
    ERBossInfo("Godskin Duo (FA)", ["Farum Azula", "Main"], 0, 13000850, allow_rykard=True,
        locations=[
            "FA/DTT: Smithing-Stone Miner's Bell Bearing [4] - boss drop",
            "FA/DTT: Ash of War: Black Flame Tornado - boss drop"
        ]
    ),
    
    # MARK: Consecrated Snowfield
    ERBossInfo("Night's Cavalry Duo (CS)", ["Consecrated Snowfield", "Overworld"], 0, 1248550800, allow_rykard=True,
        locations=[
            "CS/ICS: Ancient Dragon Smithing Stone - night boss drop, following caravan to SW",
            "CS/ICS: Night's Cavalry Helm - night boss drop, following caravan to SW",
            "CS/ICS: Night's Cavalry Armor - night boss drop, following caravan to SW",
            "CS/ICS: Night's Cavalry Gauntlets - night boss drop, following caravan to SW",
            "CS/ICS: Night's Cavalry Greaves - night boss drop, following caravan to SW"
        ]
    ),
    ERBossInfo("Death Rite Bird (CS)", ["Consecrated Snowfield", "Overworld"], 0, 1048570800, allow_rykard=True,
        locations=[
            "CS/AD: Explosive Ghostflame - night boss drop to SE on frozen river"
        ]
    ),
    ERBossInfo("Great Wyrm Theodorix (CS)", ["Consecrated Snowfield", "Overworld"], 0, 1050560800, allow_rykard=True,
        locations=[
            "CS/CF: Dragon Heart x3 - boss drop E of CF"
        ]
    ),
    ERBossInfo("Putrid Avatar (CS)", ["Consecrated Snowfield", "Overworld"], 0, 1050570850, allow_rykard=True,
        locations=[
            "CS/ME: Thorny Cracked Tear - boss drop N of ME",
            "CS/ME: Ruptured Crystal Tear - boss drop N of ME"
        ]
    ),
    # snowfield dungeons
    ERBossInfo("Putrid Grave Warden Duelist (CS/CSC)", ["Consecrated Snowfield", "Dungeon", "Catacomb"], 0, 30190800, dungeon=True,
        locations=[
            "CS/(CSC): Rotten Gravekeeper Cloak - boss drop",
            "CS/(CSC): Great Grave Glovewort x2 - boss drop"
        ]
    ),
    ERBossInfo("Stray Mimic Tear (CS/HPH)", ["Consecrated Snowfield", "Dungeon", "Catacomb"], 0, 30200810, dungeon=True,
        locations=[
            "CS/(HPH): Blackflame Monk Amon - boss drop"
        ]
    ),
    ERBossInfo("Misbegotten Crusader (CS/CF)", ["Consecrated Snowfield", "Dungeon", "Cave"], 0, 31120800, dungeon=True,
        locations=[
            "CS/(CF): Golden Order Greatsword - boss drop"
        ]
    ),
    ERBossInfo("Astel, Stars of Darkness (CS/YAT)", ["Consecrated Snowfield", "Dungeon", "Tunnel"], 0, 32110800, dungeon=True,
        locations=[
            "CS/(YAT): Meteorite of Astel - boss drop"
        ]
    ),
    
    # MARK: Mohgwyn Palace
    ERBossInfo("Mohg, Lord of Blood (MP)", ["Mohgwyn Palace", "Remembrance", "Great Rune", "Main"], 0, 12050800, allow_rykard=True,
        locations=[
            "MP/(MDM): Mohg's Great Rune - mainboss drop",
            "MP/(MDM): Remembrance of the Blood Lord - mainboss drop"
        ]
    ),
    
    # MARK: Miquella's Haligtree
    ERBossInfo("Malenia, Blade of Miquella (EBH)", ["Miquella's Haligtree", "Remembrance", "Great Rune", "Main"], 0, 15000800, allow_rykard=True,
        locations=[
            "EBH/HR: Malenia's Great Rune - mainboss drop",
            "EBH/HR: Remembrance of the Rot Goddess - mainboss drop"
        ]
    ),
    ERBossInfo("Loretta, Knight of the Haligtree (MH)", ["Miquella's Haligtree", "Main"], 0, 15000850, allow_rykard=True,
        locations=[
            "MH/HTP: Loretta's War Sickle - boss drop",
            "MH/HTP: Loretta's Mastery - boss drop"
        ]
    ),

    # MARK: Leyndell, Ashen Capital
    ERBossInfo("Sir Gideon Ofnir, The All-Knowing (LAC)", ["Leyndell, Ashen Capital", "Main"], 0, 11050850, allow_rykard=True,
        locations=[
            "LAC/LCA: Scepter of the All-Knowing - boss drop",
            "LAC/LCA: All-Knowing Helm - boss drop",
            "LAC/LCA: All-Knowing Armor - boss drop",
            "LAC/LCA: All-Knowing Gauntlets - boss drop",
            "LAC/LCA: All-Knowing Greaves - boss drop"
        ]
    ),
    ERBossInfo("Godfrey, First Elden Lord (LAC)", ["Leyndell, Ashen Capital", "Remembrance", "Main"], 0, 11050800, allow_rykard=True,# 11000850 is phase 1 11050800 phase 2
        locations=[
            "LAC/QB: Remembrance of Hoarah Loux - mainboss drop"
        ]
    ),
    ERBossInfo("Elden Beast (ET)", ["Erdtree", "Remembrance", "Final", "Main"], 0, 19000800, allow_rykard=True,
        locations=[
            "ET: Elden Remembrance - mainboss drop"
        ]
    ),
]

dlc_bosses = [
    # MARK: Gravesite Plain
    ERBossInfo("Ghostflame Dragon (GP)", ["Gravesite Plain", "Overworld"], 0, 2045440800, allow_rykard=True,
        locations=[
            "GP/BG: Dragon Heart - boss drop E of BG",
        ]
    ),
    ERBossInfo("Knight of the Solitary Gaol (GP)", ["Gravesite Plain", "Overworld", "Mausoleum"], 0, 2046410800,
        locations=[
            "GP/(WNM): Greatsword of Solitude - boss drop",
            "GP/(WNM): Helm of Solitude - boss drop",
            "GP/(WNM): Armor of Solitude - boss drop",
            "GP/(WNM): Gauntlets of Solitude - boss drop",
            "GP/(WNM): Greaves of Solitude - boss drop"
        ]
    ),
    ERBossInfo("Death Knight (GP/FRC)", ["Gravesite Plain", "Dungeon", "Catacomb"], 0, 40000800, dungeon=True,
        locations=[
            "GP/(FRC): Death Knight's Twin Axes - boss drop",
            "GP/(FRC): Crimson Amber Medallion +3 - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Swordmaster Onze (GP/BG)", ["Gravesite Plain", "Dungeon", "Gaol"], 0, 41000800, dungeon=True,
        locations=[
            "GP/(BG): Demi-Human Swordsman Yosh - boss drop"
        ]
    ),
    ERBossInfo("Ancient Dragon-Man (GP/DP)", ["Gravesite Plain", "Dungeon", "Cave"], 0, 43010800, dungeon=True,
        locations=[
            "GP/(DP): Dragon-Hunter's Great Katana - boss drop"
        ]
    ),
    
    # MARK: Belurat
    ERBossInfo("Divine Beast Dancing Lion (BTS)", ["Belurat", "DLC Remembrance"], 0, 20000800, allow_rykard=True,
        locations=[
            "BTS/SF: Remembrance of the Dancing Lion - mainboss drop",
            "BTS/BTS: Divine Beast Head - boss drop",
            "BTS/TDB: Revered Spirit Ash - on statue after boss",
            "BTS/TDB: Tower of Shadow Message - at the top of the stairs after boss"
        ]
    ),
    
    # MARK: Castle Ensis
    ERBossInfo("Rellana, Twin Moon Knight (CE)", ["Castle Ensis", "DLC Remembrance", "DLC Main"], 0, 2048440800, allow_rykard=True,
        locations=[
            "CE/CLC: Remembrance of the Twin Moon Knight - mainboss drop"
        ]
    ),
    ERBossInfo("Black Knight Garrew (CE)", ["Castle Ensis", "Fort"], 0, 2047450800, allow_rykard=True, # requires scadu altus access
        locations=[
            "CE/(FRF): Black Steel Greatshield - boss drop"
        ]
    ),
    
    # MARK: Ellac River
    ERBossInfo("Chief Bloodfiend (ER)", ["Ellac River", "Dungeon", "Cave"], 0, 43000800, dungeon=True,
        locations=[
            "ER/(RC): Bloodfiend Hexer's Ashes - boss drop"
        ]
    ),
    
    # MARK: Cerulean Coast
    ERBossInfo("Dancer of Ranah (CC)", ["Cerulean Coast", "Overworld", "Mausoleum"], 0, 2046380800,
        locations=[
            "CC/CCW: Dancing Blade of Ranah - boss drop",
            "CC/CCW: Dancer's Hood - boss drop",
            "CC/CCW: Dancer's Dress - boss drop",
            "CC/CCW: Dancer's Bracer - boss drop",
            "CC/CCW: Dancer's Trousers - boss drop"
        ]
    ),
    ERBossInfo("Demi-Human Queen Marigga (CC)", ["Cerulean Coast", "Overworld"], 0, 2046400800, allow_rykard=True,
        locations=[
            "CC/CCW: Star-Lined Sword - boss drop"
        ]
    ),
    ERBossInfo("Ghostflame Dragon (CC)", ["Cerulean Coast", "Overworld"], 0, 2048380850, allow_rykard=True,
        locations=[
            "CC/CC: Dragon Heart - boss drop",
            "CC/CC: Somber Ancient Dragon Smithing Stone - boss drop"
        ]
    ),
    
    # Stone Coffin Fissure
    ERBossInfo("Putrescent Knight (SCF)", ["Stone Coffin Fissure", "DLC Remembrance"], 0, 22000800, allow_rykard=True,
        locations=[
            "SCF/FD: Remembrance of Putrescence - mainboss drop",
            "SCF/GDP: St. Trina Disciple's Cookbook [3] - right of St. Trina",
            "SCF/GDP: St. Trina's Smile - Thiollier invader drop, after you die to St. Trina four times and tell him your findings",
            "SCF/GDP: St. Trina's Blossom - on St. Trina's body after EI mainboss"
        ]
    ),
    
    # MARK: Jagged Peak
    ERBossInfo("Jagged Peak Drake (JP/DPT)", ["Jagged Peak", "Overworld"], 0, 2049410800, allow_rykard=True,
        locations=[
            "JP/DPT: Dragon Heart - boss drop to E",
            "JP/DPT: Dragonscale Flesh - boss drop to E"
        ]
    ),
    ERBossInfo("Jagged Peak Drake (JP/FJP)", ["Jagged Peak", "Overworld"], 0, 2052400800, allow_rykard=True, # the fighting one
        locations=[
            "JP/FJP: Dragon Heart - boss drop to SE",
            "JP/FJP: Dragonscale Flesh - boss drop to SE"
        ]
    ),
    ERBossInfo("Bayle the Dread (JP)", ["Jagged Peak", "Overworld", "DLC Remembrance"], 0, 2054390800, allow_rykard=True,
        locations=[
            "JP/JPS: Heart of Bayle - mainboss drop"
        ]
    ),
    ERBossInfo("Ancient Dragon Senessax (JP)", ["Jagged Peak", "Overworld"], 0, 2054390850, allow_rykard=True,
        locations=[
            "JP/JPM: Ancient Dragon Smithing Stone - boss drop to S",
            "JP/JPM: Somber Ancient Dragon Smithing Stone - boss drop to S"
        ]
    ),
    
    # MARK: Charo's Hidden Grave
    ERBossInfo("Death Rite Bird (CHG)", ["Charo's Hidden Grave", "Overworld"], 0, 2047390800, allow_rykard=True,
        locations=[
            "CHG/CHG: Ash of War: Ghostflame Call - boss drop to NW in lake"
        ]
    ),
    ERBossInfo("Lamenter (CHG/LG)", ["Charo's Hidden Grave", "Dungeon", "Gaol"], 0, 41020800, dungeon=True,
        locations=[
            "CHG/(LG): Lamenter's Mask - boss drop"
        ]
    ),
    
    # MARK: Scadu Altus
    ERBossInfo("Ghostflame Dragon (SA)", ["Scadu Altus", "Overworld"], 0, 2049430800, allow_rykard=True,
        locations=[
            "SA/MR: Dragon Heart - boss drop to S",
            "SA/MR: Somber Ancient Dragon Smithing Stone - boss drop to S"
        ]
    ),
    ERBossInfo("Black Knight Edreed (SA)", ["Scadu Altus", "Overworld", "Fort"], 0, 2049430850,
        locations=[
            "SA/FR: Ash of War: Aspects of the Crucible: Wings - boss drop to S inside"
        ]
    ),
    ERBossInfo("Ralva the Great Red Bear (SA)", ["Scadu Altus", "Overworld"], 0, 2049450800, allow_rykard=True,
        locations=[
            "SA/HC: Pelt of Ralva - boss drop to N, E before camp, deep woods"
        ]
    ),
    ERBossInfo("Curseblade Labirith (SA/BG)", ["Scadu Altus", "Dungeon", "Gaol"], 0, 41010800, dungeon=True,
        locations=[
            "SA/(BG): Curseblade Meera - boss drop"
        ]
    ),
    
    # MARK: Rauh Base
    ERBossInfo("Rugalea the Great Red Bear (RB)", ["Rauh Base", "Overworld"], 0, 2044470800, allow_rykard=True,
        locations=[
            "RB/RN: Roar of Rugalea - boss drop to NW"
        ]
    ),
    ERBossInfo("Red Bear (RB)", ["Rauh Base", "Overworld", "Mausoleum"], 0, 2046450800,
        locations=[
            "RB/(NNM): Red Bear's Claw - boss drop",
            "RB/(NNM): Iron Rivet Armor - boss drop",
            "RB/(NNM): Iron Rivet Gauntlets - boss drop",
            "RB/(NNM): Iron Rivet Greaves - boss drop",
            "RB/(NNM): Fang Helm - boss drop"
        ]
    ),
    ERBossInfo("Death Knight (RB/SRC)", ["Rauh Base", "Dungeon", "Catacomb"], 0, 40010800, dungeon=True,
        locations=[
            "RB/(SRC): Death Knight's Longhaft Axe - boss drop",
            "RB/(SRC): Cerulean Amber Medallion +3 - boss drop"
        ]
    ),
    
    # MARK: Shadow Keep
    ERBossInfo("Messmer the Impaler (SK)", ["Shadow Keep", "DLC Remembrance"], 0, 21010800, allow_rykard=True,
        locations=[
            "SK/DCE: Remembrance of the Impaler - mainboss drop",
            "SK/DCE: Messmer's Kindling - mainboss drop"
        ]
    ),
    ERBossInfo("Golden Hippopotamus (SK)", ["Shadow Keep"], 0, 21000850, allow_rykard=True,
        locations=[
            "SK/SKMG: Aspects of the Crucible: Thorns - boss drop",
            "SK/SKMG: Scadutree Fragment x2 - boss drop"
        ]
    ),
    ERBossInfo("Commander Gaius (SK)", ["Shadow Keep", "DLC Remembrance"], 0, 2049480800, allow_rykard=True,
        locations=[
            "SV/SKBG: Remembrance of the Wild Boar Rider - mainboss drop"
        ]
    ),
    ERBossInfo("Scadutree Avatar (SK)", ["Shadow Keep", "DLC Remembrance"], 0, 2050480800, allow_rykard=True,
        locations=[
            "SK/TWS: Remembrance of the Shadow Sunflower - mainboss drop",
            "SK/TWS: Miquella's Great Rune - mainboss drop"
        ]
    ),
    
    # MARK: Hinterland
    ERBossInfo("Tree Sentinel (HL hill)", ["Hinterland", "Overworld"], 0, 2050470800, allow_rykard=True, # these could be wrong but doesn't matter
        locations=[
            "HL/HL: Blessing of Marika - boss drop on hill"
        ]
    ),
    ERBossInfo("Tree Sentinel (HL bridge)", ["Hinterland", "Overworld"], 0, 2050480860, allow_rykard=True, #
        locations=[
            "HL/HL: Blessing of Marika - boss drop by bridge"
        ]
    ),
    ERBossInfo("Fallingstar Beast (HL)", ["Hinterland", "Overworld"], 0, 2052480800, allow_rykard=True,
        locations=[
            "HL/FH: Gravitational Missile - boss drop to NE"
        ]
    ),
    
    # MARK: Finger Ruins
    ERBossInfo("Metyr, Mother of Fingers (FRM)", ["Finger Ruins", "DLC Remembrance"], 0, 25000800, allow_rykard=True,
        locations=[
            "FRM: Remembrance of the Mother of Fingers - mainboss drop",
            "SA/(CMM): Maternal Staff - kill invader Ymir",
            "SA/(CMM): High Priest Hat - kill invader Ymir",
            "SA/(CMM): High Priest Robe - kill invader Ymir",
            "SA/(CMM): High Priest Gloves - kill invader Ymir",
            "SA/(CMM): High Priest Undergarments - kill invader Ymir"
        ]
    ),
    # ERBossInfo("Count Ymir, Mother of Fingers (CMM)", ["Finger Ruins"], 0, 0,
    #     locations=[
    #         "SA/(CMM): Maternal Staff - kill invader Ymir",
    #         "SA/(CMM): High Priest Hat - kill invader Ymir",
    #         "SA/(CMM): High Priest Robe - kill invader Ymir",
    #         "SA/(CMM): High Priest Gloves - kill invader Ymir",
    #         "SA/(CMM): High Priest Undergarments - kill invader Ymir"
    #     ]
    # ),
    
    # MARK: Recluses' River
    ERBossInfo("Rakshasa (RR)", ["Recluses' River", "Overworld", "Mausoleum"], 0, 2051440800,
        locations=[
            "RR/(ENM): Rakshasa's Great Katana - boss drop",
            "RR/(ENM): Rakshasa Helm - boss drop",
            "RR/(ENM): Rakshasa Armor - boss drop",
            "RR/(ENM): Rakshasa Gauntlets - boss drop",
            "RR/(ENM): Rakshasa Greaves - boss drop"
        ]
    ),
    ERBossInfo("Jori, Elder Inquisitor (RR/DC)", ["Recluses' River", "Dungeon", "Catacomb"], 0, 2052430800, dungeon=True, allow_rykard=True,
        locations=[
            "RR/(DC): Barbed Staff-Spear - boss drop"
        ]
    ),
    
    # MARK: Midra's Manse
    ERBossInfo("Midra, Lord of Frenzied Flame (MM)", ["Midra's Manse", "DLC Remembrance"], 0, 28000800, allow_rykard=True,
        locations=[
            "MM/SFC: Remembrance of the Lord of Frenzied Flame - mainboss drop"
        ]
    ),
    
    # MARK: Ancient Ruins of Rauh
    ERBossInfo("Romina, Saint of the Bud (ARR)", ["Ancient Ruins of Rauh", "Overworld", "DLC Remembrance", "DLC Main"], 0, 2044450800, allow_rykard=True,
        locations=[
            "ARR/CBME: Remembrance of the Saint of the Bud - mainboss drop"
        ]
    ),
    ERBossInfo("Divine Beast Dancing Lion (ARR)", ["Ancient Ruins of Rauh", "Overworld"], 0, 2046460800, allow_rykard=True,
        locations=[
            "ARR/ARGS: Divine Beast Tornado - boss drop to NE"
        ]
    ),
    
    # MARK: Enir Ilim
    ERBossInfo("Promised Consort Radahn (EI)", ["Enir Ilim", "DLC Remembrance", "DLC Final", "DLC Main"], 0, 20010800, allow_rykard=True,
        locations=[
            "EI/DGFS: Remembrance of a God and a Lord - mainboss drop"
        ]
    ),
]

default_rykard_location = ""
for boss in base_bosses: 
    boss.type.append("All Base")
    if boss.name == "Rykard, Lord of Blasphemy (VM)":
        default_rykard_location = boss
for boss in dlc_bosses: 
    boss.dlc = True
    boss.type.append("All DLC")
    
all_bosses = base_bosses + dlc_bosses

all_boss_locations = []
all_boss_locations.extend(boss.locations for boss in all_bosses)