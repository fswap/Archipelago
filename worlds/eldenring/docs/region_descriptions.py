# python -m worlds.eldenring.docs.region_descriptions

from typing import Dict
import os
import html

from worlds.eldenring.locations import location_tables

# region to inital to description
region_initals_to_description: Dict[str, Dict[str, str]] = {}

# add descriptions to initials
def find_description(initial: str) -> str:
    match initial:
        # Limgrave
        case "LG/(AS)": return "Artist's Shack landmark, Mid Limgrave."
        case "LG/(BS)": return "Bridge of Sacrifice landmark, connection point between S Limgrave and Weeping Peninsula."
        case "LG/(CE)": return "Church of Elleh landmark, W Limgrave."
        case "LG/(DBR)": return "Dragon-Burnt Ruins landmark, S Limgrave."
        case "LG/(FH)": return "Fort Haight landmark, E Limgrave."
        case "LG/(FHE)": return "Forlorn Hound Evergaol, S Limgrave."
        case "LG/(GR)": return "Gatefront Ruins landmark, Mid Limgrave."
        case "LG/(MR)": return "Mistwood Ruins landmark, E Limgrave."
        case "LG/(SGr)": return "Stranded Graveyard landmark, SW Limgrave."
        case "LG/(SWV)": return "Summonwater Village landmark, NE Limgrave."
        case "LG/(TCM)": return "Third Church of Marika landmark, E Limgrave."
        case "LG/(WR)": return "Waypoint Ruins landmark, Mid Limgrave."
        case "LG/ALN": return "Agheel Lake North grace, Mid Limgrave."
        case "LG/ALS": return "Agheel Lake South grace, S Limgrave."
        case "LG/AS": return "Artist's Shack landmark, Mid Limgrave."
        case "LG/CC": return "Coastal Cave landmark, SW Limgrave."
        case "LG/CE": return "Church of Elleh landmark, W Limgrave."
        case "LG/DBR": return "Dragon-Burnt Ruins landmark, S Limgrave."
        case "LG/FHE": return "Forlorn Hound Evergaol, S Limgrave."
        case "LG/FHW": return "Fort Haight West grave, SE Limgrave."
        case "LG/GC": return "Groveside Cave landmark, W Limgrave."
        case "LG/HC": return "Highroad Cave landmark, N Limgrave."
        case "LG/MCO": return "Murkwater Coast grace, Mid Limgrave."
        case "LG/MCV": return "Murkwater Cave landmark, Mid Limgrave."
        case "LG/ME": return "Minor Erdtree, E Limgrave."
        case "LG/MO": return "Mistwood Outskirts grace, E Limgrave."
        case "LG/MR": return "Waypoint Ruins landmark, Mid Limgrave."
        case "LG/SC": return "Stormfoot Catacombs landmark, Mid Limgrave."
        case "LG/SGr": return "Stranded Graveyard landmark, SW Limgrave."
        case "LG/SR": return "Seaside Ruins grace, SW Limgrave."
        case "LG/SRW": return "Siofra River Well landmark, E Limgrave."
        case "LG/SWV": return "Summonwater Village landmark, NE Limgrave."
        case "LG/SWVO": return "Summonwater Village Outskirts grace, NE Limgrave."
        case "LG/TCM": return "Third Church of Marika landmark, E Limgrave."
        case "LG/TFS": return "The First Step grace, SW Limgrave."
        case "LG/WR": return "Waypoint Ruins landmark, Mid Limgrave."

        # Stormhill
        case "LG/(SE)": return "Stormhill Evergaol, S Stormhill."
        case "LG/(SGa)": return "Stormgate landmark, S Stormhill."
        case "LG/(SS)": return "Stormhill Shack landmark, W Stormhill."
        case "LG/(WS)": return "Warmaster's Shack landmark, mid Stormhill."
        case "LG/DC": return "Deathtouched Catacombs landmark, NE Stormhill."
        case "LG/LC": return "Limgrave Colosseum landmark, N Stormhill."
        case "LG/SB": return "Saintsbridge grace, E Stormhill."
        case "LG/SS": return "Stormhill Shack grace, W Stormhill."
        case "LG/SV": return "Stormveil landmark, area S of Margit arena."
        case "LG/WS": return "Warmaster's Shack grace, mid Stormhill."
        case "SV/CT": return "Castleward Tunnel grace, Stormveil enterance."

        # Limgrave Dungeons
        # Coastal Cave
        case "LG/(CC)": return "Coastal Cave, SW Limgrave."

        # Church of Dragon Communion
        case "LG/(CDC)": return "Church of Dragon Communion, through Coastal Cave SW Limgrave."

        # Groveside Cave
        case "LG/(GC)": return "Groveside Cave, W Limgrave."

        # Stormfoot Catacombs
        case "LG/(SC)": return "Stormfoot Catacombs, W Limgrave."

        # Limgrave Tunnels
        case "LG/(LT)": return "Limgrave Tunnels, W Limgrave."

        # Murkwater Cave
        case "LG/(MCV)": return "Murkwater Cave, Mid Limgrave."

        # Murkwater Catacombs
        case "LG/(MCC)": return "Murkwater Catacombs, Mid Limgrave."

        # Highroad Cave
        case "LG/(HC)": return "Highroad Cave, N Limgrave."

        # Deathtouched Catacombs
        case "LG/(DC)": return "Deathtouched Catacombs, E Stormhill."

        # Fringefolk Hero's Grave
        case "LG/(FHG)": return "Fringefolk Hero's Grave, W Limgrave."

        # Roundtable Hold
        case "RH": return "Roundtable Hold."

        # Stormveil Castle
        case "SV/GC": return "Gateside Chamber grace."
        case "SV/LC": return "Liftside Chamber grace."
        case "SV/LTB": return "Limgrave Tower Bridge grace."
        case "SV/RT": return "Rampart Tower grace."
        case "SV/SMG": return "Stormveil Main Gate grace."
        case "SV/SeC": return "Secluded Cell grace."
        case "SV/StC": return "Stormveil Cliffside grace."

        # Stormveil Throne
        case "SV/GG": return "Godrick the Grafted grace, in Godrick's arena."
        case "SV/LL": return "Liurnia side of Stormveil, after Godrick's arena."

        # Divine Tower of Limgrave
        case "SV/(DTL)": return "Divine Tower of Limgrave landmark."

        # Weeping Peninsula
        case "WP/(AV)": return "Ailing Village landmark, NE Weeping."
        case "WP/(CBC)": return "Callu Baptismal Church landmark, E Weeping."
        case "WP/(CM)": return "Castle Morne, S Weeping."
        case "WP/(CP)": return "Church of Pilgrimage landmark, N Weeping."
        case "WP/(DHFR)": return "Demi-Human Forest Ruins landmark, N Weeping."
        case "WP/(FCM)": return "Fourth Church of Marika landmark, NW Weeping."
        case "WP/(FLT)": return "Forest Lookout Tower landmark, NE Weeping."
        case "WP/(IMS)": return "Isolated Merchant's Shack, W Weeping."
        case "WP/(OR)": return "Oridys's Rise landmark, E Weeping."
        case "WP/(TwR)": return "Tombsward Ruins landmark, NW Weeping."
        case "WP/(WE)": return "Weeping Evergaol, NW Weeping."
        case "WP/(WR)": return "Witchbane Ruins landmark, NW Weeping."
        case "WP/AV": return "Ailing Village Outskirts grace, E Weeping."
        case "WP/BCPG": return "Beside the Crater-Pocked Glade grace, NE Weeping."
        case "WP/BS": return "Bridge of Sacrifice grace."
        case "WP/CM": return "Castle Morne grace, SE Weeping."
        case "WP/CMR": return "Castle Morne Rampart grace, E Weeping."
        case "WP/CP": return "Church of Pilgrimage grace, N Weeping."
        case "WP/DHFR": return "Demi-Human Forest Ruins area, NE Weeping."
        case "WP/EC": return "Earthbore Cave entrance, NE Weeping."
        case "WP/FLT": return "Forest Lookout Tower area, NE Weeping."
        case "WP/ME": return "Minor Erdtree, N Weeping."
        case "WP/MT": return "Morne Tunnel entrance, NE Weeping."
        case "WP/OR": return "Oridys's Rise area, E Weeping."
        case "WP/SLT": return "South of the Lookout Tower grace, NE Weeping."
        case "WP/ToR": return "Tower of Return grace, W Weeping."
        case "WP/TwR": return "Tombsward Ruins grace, NW Weeping."
        case "WP/WR": return "Witchbane Ruins grace, NW Weeping."

        # Weeping Peninsula Dungeons
        # Impaler's Catacombs
        case "WP/(IC)": return "Impaler's Catacombs, NE Weeping."

        # Tombsward Catacombs
        case "WP/(TCC)": return "Tombsward Catacombs, mid Weeping."

        # Tombsward Cave
        case "WP/(TCV)": return "Tombsward Cave, W Weeping."

        # Morne Tunnel
        case "WP/(MT)": return "Morne Tunnel, mid Weeping."

        # Earthbore Cave
        case "WP/(EC)": return "Earthbore Cave, N Weeping."

        # Siofra River
        case "SR/(HG)": return "Hallowhorn Grounds landmark, SE Siofra."
        case "SR/BW": return "Below The Well grace, N Siofra."
        case "SR/SRB": return "Siofra River Bank grace, S Siofra."
        case "SR/SRWD": return "Siofra River Well Depths grace, SW Siofra."
        case "SR/WW": return "Worshippers' Woods grace, mid Siofra."

        # Liurnia of The Lakes
        case "LL/(AGT)": return "Academy Gate Town landmark, SW of Raya Lucaria."
        case "LL/(AS)": return "Artist's Shack landmark, SE Liurnia."
        case "LL/(CE)": return "Cuckoo's Evergaol, W Liurnia."
        case "LL/(CFT)": return "Converted Fringe Tower, NE Liurnia."
        case "LL/(CIr)": return "Church of Irith, SE Liurnia."
        case "LL/(CM)": return "Caria Manor, NW Liurnia."
        case "LL/(CT)": return "Converted Tower landmark, SW Liurnia."
        case "LL/(CV)": return "Church of Vows landmark, mid Liurnia."
        case "LL/(FFV)": return "Frenzied Flame Village, NE Liurnia."
        case "LL/(HLT)": return "Highway Lookout Tower landmark, SE Liurnia."
        case "LL/(KR)": return "Kingsrealm Ruins landmark, NW Liurnia."
        case "LL/(LR)": return "Laskyar Ruins landmark, SE Liurnia."
        case "LL/(ME)": return "Malefactor's Evergaol, SE Liurnia."
        case "LL/(PR)": return "Purified Ruins landmark, SE Liurnia."
        case "LL/(RC)": return "Rose Church landmark, SW Liurnia."
        case "LL/(RS)": return "Revenger's Shack landmark, SW Liurnia."
        case "LL/(SWS)": return "Slumbering Wolf's Shack landmark, S Liurnia."
        case "LL/(TFB)": return "The Four Belfries landmark, W Liurnia."
        case "LL/(VA)": return "Village of the Albinaurics landmark, SW Liurnia."
        case "LL/AGT": return "Academy Gate Town grace, mid Liurnia."
        case "LL/ARW": return "Ainsel River Well grace, E Liurnia."
        case "LL/AS": return "Artist's Shack grace, SE Liurnia."
        case "LL/BC": return "Bellum Church grace, N Liurnia."
        case "LL/BCM": return "Behind Caria Manor grace, N Liurnia."
        case "LL/BS": return "Boilprawn Shack grace, S Liurnia."
        case "LL/CC": return "Cliffbottom Catacombs entrance, SE Liurnia."
        case "LL/CFT": return "Converted Fringe Tower landmark, NE Liurnia."
        case "LL/CIn": return "Church of Inhibition grace, N Liurnia."
        case "LL/CIr": return "Church of Irith landmark, SE Liurnia."
        case "LL/CT": return "Converted Tower grace, SW Liurnia."
        case "LL/CV": return "Church of Vows grace, mid Liurnia."
        case "LL/CW": return "Crystalline Woods grace, W Liurnia."
        case "LL/EGBT": return "East Gate Bridge Trestle grace, W Liurnia."
        case "LL/ELLS": return "Eastern Liurnia Lake Shore grace, E Liurnia."
        case "LL/ERLG": return "East Raya Lucaria Gate grace, N Liurnia."
        case "LL/ET": return "Eastern Tableland grace, E Liurnia."
        case "LL/FFB": return "Foot of the Four Belfries grace, W Liurnia."
        case "LL/FFV": return "Frenzied Flame Village landmark, NE Liurnia."
        case "LL/FFVO": return "Frenzied Flame Village Outskirts grace, NE Liurnia."
        case "LL/FL": return "Folly on the Lake grace, SW Liurnia."
        case "LL/FRL": return "Fallen Ruins of the Lake grace, S Liurnia."
        case "LL/GLD": return "Grand Lift of Dectus grace, NE Liurnia."
        case "LL/GTB": return "Gate Town Bridge grace, SE Liurnia."
        case "LL/GTN": return "Gate Town North grace, W Liurnia."
        case "LL/JB": return "Jarburg grace, SE Liurnia."
        case "LL/LFC": return "Lake-Facing Cliffs grace, SE Liurnia."
        case "LL/LHN": return "Liurnia Highway North grace, SE Liurnia."
        case "LL/LHS": return "Liurnia Highway South grace, SE Liurnia."
        case "LL/LLS": return "Liurnia Lake Shore grace, SE Liurnia."
        case "LL/LR": return "Laskyar Ruins grace, SE Liurnia."
        case "LL/MC": return "Mausoleum Compound grace, N Liurnia."
        case "LL/MCMG": return "Main Caria Manor Gate grace, N Liurnia."
        case "LL/MEW": return "Minor Erdtree, W Liurnia, N of Converted Tower."
        case "LL/NLLS": return "Northern Liurnia Lake Shore grace, NW Liurnia."
        case "LL/RC": return "Rose Church grace, SW Liurnia."
        case "LL/REC": return "Road's End Catacombs entrance, SW Liurnia."
        case "LL/RL": return "Ruined Labyrinth grace, E Liurnia."
        case "LL/RM": return "Road to the Manor grace, NW Liurnia."
        case "LL/RVV": return "Ravine-Veiled Village grace, NE Liurnia."
        case "LL/SHE": return "Study Hall Entrance grace, E Liurnia."
        case "LL/SRLG": return "South Raya Lucaria Gate grace, W Liurnia."
        case "LL/SeI": return "Scenic Isle grace, S Liurnia."
        case "LL/SoI": return "Sorcerer's Isle grace, W Liurnia."
        case "LL/TQ": return "Temple Quarter grace, W Liurnia."
        case "LL/TR": return "The Ravine grace, NW Liurnia."
        case "LL/VA": return "Village of the Albinaurics grace, SW Liurnia."

        # Bellum Highway
        case "LL/(BC)": return "Bellum Church, N Liurnia."
        case "LL/(CIn)": return "Church of Inhibition, NE Liurnia."
        case "LL/(FFT)": return "Frenzy-Flaming Tower, NE Liurnia."
        case "LL/MEE": return "Minor Erdtree, E Liurnia, S of Frenzied Flame Village."

        # Liurnia of The Lakes Dungeons
        # Road's End Catacombs
        case "LL/(REC)": return "Road's End Catacombs, SW Liurnia."

        # Black Knife Catacombs
        case "LL/(BKC)": return "Black Knife Catacombs, NE Liurnia."

        # Cliffbottom Catacombs
        case "LL/(CC)": return "Cliffbottom Catacombs, SE Liurnia."

        # Stillwater Cave
        case "LL/(SC)": return "Stillwater Cave, SE Liurnia."

        # Lakeside Crystal Cave
        case "LL/(LCC)": return "Lakeside Crystal Cave, S Liurnia."

        # Academy Crystal Cave
        case "LL/(ACC)": return "Academy Crystal Cave, NW Liurnia."

        # Raya Lucaria Crystal Tunnel
        case "LL/(RLCT)": return "Raya Lucaria Crystal Tunnel, N Liurnia."

        # Caria Manor
        case "LL/(RGE)": return "Royal Grave Evergaol, N Liurnia."
        case "LL/(RaR)": return "Ranni's Rise, NW Liurnia."
        case "LL/(ReR)": return "Renna's Rise, NW Liurnia."
        case "LL/(SR)": return "Seluvis's Rise, NW Liurnia."
        case "LL/RMG": return "Royal Moongazing Grounds grace, NW Liurnia."
        case "LL/RaR": return "Ranni's Rise grace, NW Liurnia."
        case "LL/SR": return "Seluvis's Rise landmark, NW Liurnia."

        # Carian Study Hall
        case "LL/(CSH)N": return "Carian Study Hall normal."

        # Carian Study Hall (Inverted)
        case "LL/(CSH)I": return "Carian Study Hall inverted."
        case "LL/(DV)": return "Divine Tower of Liurnia."
        case "LL/LTB": return "Liurnia Tower Bridge grace, after CSH."

        # Ainsel River
        case "AR/(UPR)": return "Uhl Palace Ruins landmark, S Ainsel River."
        case "AR/ARD": return "Ainsel River Downstream grace, W Ainsel River."
        case "AR/ARSG": return "Ainsel River Sluice Gate grace, SE Ainsel River."
        case "AR/ARWD": return "Ainsel River Well Depths grace, SE Ainsel River."
        case "AR/UPR": return "Uhl Palace Ruins grace, NW Ainsel River."

        # Ruin-Strewn Precipice
        case "RSP/RSP": return "Ruin-Strewn Precipice grace."
        case "RSP/RSPO": return "Ruin-Strewn Precipice Overlook grace, before Magma Wyrm Makar."
        case "RSP/RVV": return "Ravine-Veiled Village side of Ruin-Strewn Precipice, before the first elevator."

        # The Four Belfries
        # The Four Belfries (Chapel of Anticipation)
        case "LL/(TFB/CA)": return "The Four Belfries (Chapel of Anticipation)."

        # The Four Belfries (Nokron)
        case "LL/(TFB/NEC)": return "The Four Belfries (Nokron)."

        # The Four Belfries (Farum Azula)
        case "LL/(TFB/FA)": return "The Four Belfries (Farum Azula)."

        # Raya Lucaria Academy
        case "RLA/CC": return "Church of the Cuckoo grace."
        case "RLA/MAG": return "Main Academy Gate grace."
        case "RLA/SC": return "Schoolhouse Classroom grace."

        # Raya Lucaria Academy Main
        case "RLA/DB": return "Debate Parlor grace."

        # Raya Lucaria Academy Library
        case "RLA/RLGL": return "Raya Lucaria Grand Library grace."

        # Caelid
        case "CL/(CDC)": return "Cathedral of Dragon Communion, S Caelid."
        case "CL/(CP)": return "Church of the Plague landmark, E Caelid."
        case "CL/(CR)": return "Caelem Ruins landmark, NW Caelid."
        case "CL/(CWR)": return "Caelid Waypoint Ruins landmark, W Caelid."
        case "CL/(FG)": return "Fort Gael, W Caelid."
        case "CL/(FR)": return "Forsaken Ruins landmark, NW Caelid."
        case "CL/(GS)": return "Gowry's Shack, E Caelid."
        case "CL/(RC)": return "Redmane Castle, SE Caelid."
        case "CL/(SC)": return "Smoldering Church landmark, NW Caelid."
        case "CL/(SG)": return "Sellia Gateway, mid Caelid."
        case "CL/(SLT)": return "Swamp Lookout Tower landmark, mid Caelid."
        case "CL/(SSR)": return "Street of Sages Ruins landmark, mid Caelid."
        case "CL/(STS)": return "Sellia, Town of Sorcery, N Caelid."
        case "CL/ACHN": return "Astray from Caelid Highway North grace, W Caelid."
        case "CL/ASS": return "Aeonia Swamp Shore grace, mid Caelid."
        case "CL/CCC": return "Caelid Catacombs entrance, S Caelid."
        case "CL/CHS": return "Caelid Highway South grace, SW Caelid."
        case "CL/CP": return "Church of the Plague grace, E Caelid."
        case "CL/CR": return "Caelem Ruins grace, NW Caelid."
        case "CL/CWR": return "Caelid Waypoint Ruins grace, W Caelid."
        case "CL/DSW": return "Deep Siofra Well grace, N Caelid."
        case "CL/DW": return "Dragonbarrow West grace, N Caelid."
        case "CL/FGN": return "Fort Gael North grace, NW Caelid."
        case "CL/FR": return "Forsaken Ruins area, NW Caelid."
        case "CL/IA": return "Inner Aeonia grace, mid Caelid."
        case "CL/IG": return "Impassable Greatbridge grace, SE Caelid."
        case "CL/MEW": return "Minor Erdtree, NW Caelid, NE of Smoldering Church."
        case "CL/RB": return "Rotview Balcony grace, NW Caelid."
        case "CL/SASB": return "Southern Aeonia Swamp Bank grace, S Caelid."
        case "CL/SG": return "Sellia Gateway landmark, mid Caelid."
        case "CL/SH": return "Sellia Hideaway area, NE Caelid."
        case "CL/SSR": return "Street of Sages Ruins grace, mid Caelid."
        case "CL/SUS": return "Sellia Under-Stair grace, N Caelid."
        case "CL/SW": return "Smoldering Wall grace, NW Caelid."

        # Caelid Dungeons
        # Caelid Catacombs
        case "CL/(CCC)": return "Caelid Catacombs, S Caelid."

        # Gaol Cave
        case "CL/(GC)": return "Gaol Cave, SW Caelid."

        # Sellia Crystal Tunnel
        case "CL/(SCT)": return "Sellia Crystal Tunnel, mid Caelid."

        # Abandoned Cave
        case "CL/(AC)": return "Abandoned Cave, mid Caelid."

        # Minor Erdtree Catacombs
        case "CL/(MEC)": return "Minor Erdtree Catacombs, NW Caelid."

        # Gael Tunnel
        case "CL/(GT)": return "Gael Tunnel, W Caelid."

        # Great-Jar
        case "CL/CCO": return "Caelid Colosseum, by Great-Jar, NW Caelid."
        case "CL/SE": return "Sellia Evergaol area, N Caelid."

        # Radahn Festival
        # Wailing Dunes
        case "CL/(WD)": return "Wailing Dunes."

        # War-Dead Catacombs
        case "CL/(WDC)": return "War-Dead Catacombs, N of Wailing Dunes."

        # Dragonbarrow
        case "DB/(BS)": return "Bestial Sanctum, Gurranq, NE Dragonbarrow."
        case "DB/(FF)": return "Fort Faroth, SE Dragonbarrow."
        case "DB/(IMS)": return "Isolated Merchant's Shack, W Dragonbarrow."
        case "DB/(LR)": return "Lenne's Rise landmark, E Dragonbarrow."
        case "DB/(SE)": return "Sellia Evergaol, on a cliff above Sellia, S Dragonbarrow."
        case "DB/BS": return "Bestial Sanctum grace, NE Dragonbarrow."
        case "DB/DT": return "Divine Tower of Caelid area, S Dragonbarrow."
        case "DB/DW": return "Dragonbarrow West grace, S Dragonbarrow."
        case "DB/FF": return "Fort Faroth grace, S Dragonbarrow."
        case "DB/FG": return "Farum Greatbridge grace, NE Dragonbarrow."
        case "DB/IMS": return "Isolated Merchant's Shack grace, W Dragonbarrow."
        case "DB/LR": return "Lenne's Rise grace, E Dragonbarrow."
        case "DB/MEE": return "Minor Erdtree, SE Dragonbarrow."

        # Dragonbarrow Dungeons
        # Dragonbarrow Cave
        case "DB/(DC)": return "Dragonbarrow Cave."

        # Sellia Hideaway
        case "DB/(SH)": return "Sellia Hideaway."

        # Divine Tower of Caelid
        case "DB/(DT)": return "Divine Tower of Caelid."

        # Nokron, Eternal City
        # Nokron, Eternal City Start
        case "NR/LG": return "Nokron, Eternal City start, entered from the Limgrave star crater after Radahn."
        case "NR/NEC": return "Nokron, Eternal City grace."

        case "NR/(HG)": return "Hallowhorn Grounds, Regal Ancestor Spirit, NE Nokron."
        case "NR/(NSG)": return "Night's Sacred Ground, S Nokron."
        case "NR/(SA)": return "Siofra Aqueduct, NE Nokron."
        case "NR/AFC": return "Aqueduct-Facing Cliffs grace, NE Nokron."
        case "NR/AW": return "Ancestral Woods grace, mid Nokron."
        case "NR/HG": return "Hallowhorn Grounds area, E Nokron."
        case "NR/MT": return "Mimic Tear grace, SE Nokron."

        # Deeproot Depths
        # Deeproot Depths Upper
        case "DD/RFC": return "Root-Facing Cliffs grace, SE Deeproot Depths."

        case "DD/DD": return "Deeproot Depths grace."
        case "DD/GWC": return "Great Waterfall Crest grace, E Deeproot Depths."
        case "DD/TNEC": return "The Nameless Eternal City grace, NW Deeproot Depths."

        # Deeproot Depths Boss
        case "DD/AR": return "Across the Roots grace, Deeproot Depths."
        case "DD/PDT": return "Prince of Death's Throne grace, Deeproot Depths."

        # Ainsel River Main
        case "ARM/(UPR)": return "Uhl Palace Ruins landmark, NE platform."
        case "ARM/ARM": return "Ainsel River Main grace."
        case "ARM/UPR": return "Uhl Palace Ruins, Ainsel River Main side."
        case "NS/NEC": return "Nokstella, Eternal City grace."
        case "NS/NWB": return "Nokstella Waterfall Basin grace."

        # Lake of Rot
        case "LR": return "Lake of Rot, Astel boss arena below Grand Cloister."
        case "LR/GC": return "Grand Cloister grace, S Lake of Rot."
        case "LR/LRS": return "Lake of Rot Shoreside grace."

        # Moonlight Altar
        case "MA/(CMC)": return "Cathedral of Manus Celes, NE Moonlight Altar."
        case "MA/(CR)": return "Chelona's Rise, SW Moonlight Altar."
        case "MA/(LER)": return "Lunar Estate Ruins, E Moonlight Altar."
        case "MA/(MR)": return "Moonfolk Ruins landmark, N Moonlight Altar."
        case "MA/(RE)": return "Ringleader's Evergaol, NW Moonlight Altar."
        case "MA/MA": return "Moonlight Altar grace."

        # Altus Plateau
        case "AP/(DWV)": return "Dominula, Windmill Village, NE Altus."
        case "AP/(HLT)": return "Highway Lookout Tower landmark, NE Altus."
        case "AP/(MR)": return "Mirage Rise landmark, mid Altus."
        case "AP/(SCM)": return "Second Church of Marika landmark, mid Altus."
        case "AP/(ScC)": return "Stormcaller Church landmark, S Altus."
        case "AP/(WbR)": return "Writheblood Ruins landmark, N Altus."
        case "AP/(WfR)": return "Woodfolk Ruins landmark, E Altus."
        case "AP/AC": return "Abandoned Coffin grace, SW Altus."
        case "AP/AHJ": return "Altus Highway Junction grace, S Altus."
        case "AP/AP": return "Altus Plateau grace, SW Altus."
        case "AP/BB": return "Bower of Bounty grace, mid Altus."
        case "AP/EGH": return "Erdtree-Gazing Hill grace, SW Altus."
        case "AP/EWP": return "East Windmill Pasture grace, NE Altus."
        case "AP/FSG": return "Forest-Spanning Greatbridge grace, E Altus."
        case "AP/GLE": return "Golden Lineage Evergaol grace, SW Altus."
        case "AP/HLT": return "Highway Lookout Tower area, NE Altus, before Capital Outskirts."
        case "AP/LR": return "Lux Ruins grace, SW Altus."
        case "AP/ME": return "Minor Erdtree, E Altus."
        case "AP/MR": return "Mirage Rise grace, mid Altus."
        case "AP/OAT": return "Old Altus Tunnel grace, W Altus."
        case "AP/PR": return "Perfumer's Ruins landmark, SW Altus."
        case "AP/RISP": return "Road of Iniquity Side Path grace, N Altus."
        case "AP/RP": return "Rampartside Path grace, E Altus, near Ancient Dragon Lansseax."
        case "AP/SCM": return "Second Church of Marika grace, mid Altus."
        case "AP/SCR": return "Shaded Castle Ramparts, outside the castle walls, N Altus."
        case "AP/SH": return "Shaded Castle area, NW Altus."
        case "AP/SHG": return "Sainted Hero's Grave grace, S Altus."
        case "AP/SR": return "Seethewater River grace, W Altus."
        case "AP/STH": return "St. Trina's Hideaway landmark, S Altus."
        case "AP/TSC": return "The Shaded Castle landmark, NW Altus."
        case "AP/VWP": return "Village Windmill Pasture landmark, NE Altus."
        case "AP/WV": return "Windmill Village grace, NE Altus."
        case "AP/WWP": return "West Windmill Pasture grace, N Altus."
        case "AP/WbR": return "Writheblood Ruins grace, mid Altus."
        case "AP/WhR": return "Wyndham Ruins grace, W Altus."
        case "TSC/CI": return "Outside Castellan's Hall boss arena, past Shaded Castle Inner Gate grace."
        case "TSC/SCIG": return "Shaded Castle Inner Gate grace."
        case "TSC/SCR": return "Shaded Castle Ramparts grace."

        # Altus Plateau Dungeons
        # Sainted Hero's Grave
        case "AP/(SHG)": return "Sainted Hero's Grave, S Altus."

        # Unsightly Catacombs
        case "AP/(UC)": return "Unsightly Catacombs, SW Altus."

        # Perfumer's Grotto
        case "AP/(PG)": return "Perfumer's Grotto, SW Altus."

        # Sage's Cave
        case "AP/(SCV)": return "Sage's Cave, SW Altus."

        # Old Altus Tunnel
        case "AP/(OAT)": return "Old Altus Tunnel, W Altus."

        # Altus Tunnel
        case "AP/(AT)": return "Altus Tunnel, SE Altus."

        # Wyndham Catacombs
        case "AP/(WC)": return "Wyndham Catacombs, NW Altus."

        # Mt. Gelmir
        case "MtG/(CS)": return "Craftsman's Shack landmark, S Mt. Gelmir."
        case "MtG/(CSS)": return "Corpse-Stench Shack landmark, NE Mt. Gelmir."
        case "MtG/(FL)": return "Fort Laiedd landmark, W Mt. Gelmir."
        case "MtG/(HS)": return "Hermit's Shack, SW Mt. Gelmir."
        case "MtG/(HV)": return "Hermit Village landmark, S Mt. Gelmir."
        case "MtG/BI": return "Bridge of Iniquity grace, E Mt. Gelmir."
        case "MtG/FL": return "Fort Laiedd grace, SW Mt. Gelmir."
        case "MtG/FMGC": return "First Mt. Gelmir Campsite grace, NE Mt. Gelmir."
        case "MtG/GHG": return "Gelmir Hero's Grave grace, E Mt. Gelmir."
        case "MtG/HS": return "Hermit's Shack landmark, SW Mt. Gelmir."
        case "MtG/HV": return "Hermit Village grace, S Mt. Gelmir."
        case "MtG/ME": return "Minor Erdtree, N Mt. Gelmir."
        case "MtG/NMGC": return "Ninth Mt. Gelmir Campsite grace, N Mt. Gelmir."
        case "MtG/PSA": return "Primeval Sorcerer Azur grace, S Mt. Gelmir."
        case "MtG/RI": return "Road of Iniquity grace, NW Mt. Gelmir."
        case "MtG/SR": return "Seethewater River grace, mid Mt. Gelmir."
        case "MtG/ST": return "Seethewater Terminus grace, W Mt. Gelmir."
        case "MtG/VC": return "Volcano Cave entrance, N Mt. Gelmir."
        case "MtG/VM": return "Volcano Manor grace, outside the manor, NW Mt. Gelmir."

        # Mt. Gelmir Dungeons
        # Gelmir Hero's Grave
        case "MtG/(GHG)": return "Gelmir Hero's Grave, E Mt. Gelmir."

        # Seethewater Cave
        case "MtG/(SC)": return "Seethewater Cave, mid Mt. Gelmir."

        # Volcano Cave
        case "MtG/(VC)": return "Volcano Cave, N Mt. Gelmir."

        # Volcano Manor
        # Volcano Manor Dungeon
        case "(VM)/RLA": return "Arrival point of the Abductor Virgin warp from Raya Lucaria."
        case "(VM)/SIC": return "Subterranean Inquisition Chamber grace, from the Abductor Virgin warp."

        # Volcano Manor Drawing Room
        case "VM/VM": return "Volcano Manor grace, inside the manor."

        case "VM/GH": return "Guest Hall grace."
        case "VM/PTC": return "Prison Town Church grace."

        # Volcano Manor Upper
        case "VM/AP": return "Audience Pathway grace, before Rykard."
        case "VM/RLB": return "Rykard, Lord of Blasphemy grace, Rykard's arena."
        case "VM/TE": return "Temple of Eiglay grace."

        # Capital Outskirts
        case "CO": return "Capital Outskirts, Capital great rune gate, guarded by the Draconic Tree Sentinel."
        case "CO/(HMS)": return "Hermit Merchant's Shack, N Capital Outskirts."
        case "CO/(ME)": return "Minor Erdtree landmark, NE Capital Outskirts."
        case "CO/(MEC)": return "Minor Erdtree Church landmark, SW Capital Outskirts."
        case "CO/AHG": return "Auriza Hero's Grave grace, E Capital Outskirts."
        case "CO/HMS": return "Hermit Merchant's Shack grace, N Capital Outskirts."
        case "CO/ME": return "Minor Erdtree, NE Capital Outskirts."
        case "CO/MEC": return "Minor Erdtree Church grace, S Capital Outskirts."
        case "CO/OWB": return "Outer Wall Battleground grace, W Capital Outskirts."
        case "CO/OWPT": return "Outer Wall Phantom Tree grace, SW Capital Outskirts."

        # Capital Outskirts Dungeons
        # Auriza Hero's Grave
        case "CO/(AHG)": return "Auriza Hero's Grave, E Capital Outskirts."

        # Auriza Side Tomb
        case "CO/(AST)": return "Auriza Side Tomb, E Capital Outskirts."

        # Sealed Tunnel
        case "CO/(ST)": return "Sealed Tunnel, SW Capital Outskirts."

        # Leyndell, Royal Capital
        case "LRC/AB": return "Avenue Balcony grace."
        case "LRC/ECR": return "East Capital Rampart grace."
        case "LRC/FMFF": return "Fortified Manor, First Floor grace."
        case "LRC/LCC": return "Lower Capital Church grace."
        case "LRC/QB": return "Queen's Bedchamber grace."
        case "LRC/WCR": return "West Capital Rampart grace."
        case "LRC|LAC/RC": return "Royal Colosseum area, Corhyn and Goldmask spot, Royal or Ashen Capital."

        # Leyndell, Royal Capital Unmissable
        case "DTEA": return "Divine Tower of East Altus approach, top of the stairs from Leyndell."
        case "LRC|LAC/AB": return "Avenue Balcony grace, Royal or Ashen Capital."
        case "LRC|LAC/ECR": return "East Capital Rampart grace, Royal or Ashen Capital."
        case "LRC|LAC/FMFF": return "Fortified Manor, First Floor grace, Royal or Ashen Capital."
        case "LRC|LAC/WCR": return "West Capital Rampart grace, Royal or Ashen Capital."

        # Leyndell, Royal Capital Throne
        case "LRC/ES": return "Erdtree Sanctuary grace."
        case "LRC/ET": return "Elden Throne grace."
        case "LRC|LAC/ES": return "Erdtree Sanctuary grace, Royal or Ashen Capital."

        # Divine Bridge
        case "LRC|LAC/(DB)": return "Divine Bridge, Royal or Ashen Capital."

        # Subterranean Shunning-Grounds
        case "SSG/(LC)": return "Leyndell Catacombs."
        case "SSG/FD": return "Forsaken Depths grace, before Mohg, the Omen."
        case "SSG/LC": return "Leyndell Catacombs grace."
        case "SSG/UR": return "Underground Roadside grace."

        # Frenzied Flame Proscription
        case "FFP/CF": return "Cathedral of the Forsaken grace."
        case "FFP/FFP": return "Frenzied Flame Proscription grace."

        # Forbidden Lands
        case "FL/FL": return "Forbidden Lands grace."
        case "FL/GLR": return "Grand Lift of Rold grace."

        # Hidden Path to the Haligtree
        case "CS/(HPH)": return "Hidden Path to the Haligtree, S Snowfield."

        # Mountaintops of the Giants
        case "MotG/(CS)": return "Castle Sol, N Mountaintops."
        case "MotG/(FCM)": return "First Church of Marika landmark, E Mountaintops."
        case "MotG/(GG)": return "Guardians' Garrison landmark, mid Mountaintops."
        case "MotG/(GLR)": return "Grand Lift of Rold landmark, SW Mountaintops."
        case "MotG/(HR)": return "Heretical Rise landmark, NE Mountaintops."
        case "MotG/(LCE)": return "Lord Contender's Evergaol, E Mountaintops."
        case "MotG/(ME)": return "Minor Erdtree landmark, N Mountaintops."
        case "MotG/(SL)": return "Shack of the Lofty landmark, W Mountaintops."
        case "MotG/(SR)": return "Stargazers' Ruins landmark, W Mountaintops."
        case "MotG/(ZR)": return "Zamor Ruins landmark, SW Mountaintops."
        case "MotG/ASVR": return "Ancient Snow Valley Ruins grace, W Mountaintops."
        case "MotG/CSMG": return "Castle Sol Main Gate grace, NW Mountaintops."
        case "MotG/FCM": return "First Church of Marika grace, E Mountaintops."
        case "MotG/FR": return "Grace S of Freezing Lake, near Borealis, NE Mountaintops."
        case "MotG/GG": return "Guardians' Garrison grace, mid Mountaintops."
        case "MotG/HR": return "Heretical Rise area, NE Mountaintops."
        case "MotG/LCE": return "Lord Contender's Evergaol grace, NE Mountaintops."
        case "MotG/ME": return "Minor Erdtree, mid Mountaintops."
        case "MotG/SL": return "Shack of the Lofty grace, NW Mountaintops."
        case "MotG/SR": return "Stargazers' Ruins grace, W Mountaintops."
        case "MotG/SVRO": return "Snow Valley Ruins Overlook grace, NW Mountaintops."
        case "MotG/WR": return "Whiteridge Road grace, E Mountaintops."
        case "MotG/ZR": return "Zamor Ruins grace, SW Mountaintops."

        # Mountaintops of the Giants Dungeons
        # Giants' Mountaintop Catacombs
        case "MotG/(GMC)": return "Giants' Mountaintop Catacombs, SW Mountaintops."

        # Spiritcaller Cave
        case "MotG/(SC)": return "Spiritcaller Cave, NE Mountaintops."

        # Flame Peak
        case "FP/(CR)": return "Church of Repose landmark, SW Flame Peak."
        case "FP/CR": return "Church of Repose grace, W Flame Peak."
        case "FP/FF": return "Foot of the Forge grace, Fire Giant, NE Flame Peak."
        case "FP/GCHG": return "Giant-Conquering Hero's Grave grace, W Flame Peak."
        case "FP/GG": return "Giants' Gravepost grace, N Flame Peak."

        # Flame Peak Dungeon
        # Giant-Conquering Hero's Grave
        case "FP/(GCHG)": return "Giant-Conquering Hero's Grave."

        # Farum Azula
        case "FA/CBG": return "Crumbling Beast Grave grace."
        case "FA/CBGD": return "Crumbling Beast Grave Depths grace."
        case "FA/DT": return "Dragon Temple grace."
        case "FA/DTT": return "Dragon Temple Transept grace."
        case "FA/MotG": return "Farum Azula arrival point, from the Mountaintops warp."
        case "FA/TFB": return "Tempest-Facing Balcony grace."

        # Farum Azula Main
        case "FA/BGB": return "Beside the Great Bridge grace."
        case "FA/DTA": return "Dragon Temple Altar grace."
        case "FA/DTL": return "Dragon Temple Lift grace."
        case "FA/DTR": return "Dragon Temple Rooftop grace."

        # Consecrated Snowfield
        case "CS/(AD)": return "Apostate Derelict landmark, NW Snowfield."
        case "CS/(AR)": return "Albinauric Rise landmark, E Snowfield."
        case "CS/(ME)": return "Minor Erdtree landmark, NE Snowfield."
        case "CS/(OLT)": return "Ordina, Liturgical Town landmark, N Snowfield."
        case "CS/(YAR)": return "Yelough Anix Ruins landmark, SW Snowfield."
        case "CS/AD": return "Apostate Derelict grace, NW Snowfield."
        case "CS/AR": return "Albinauric Rise area, E Snowfield."
        case "CS/CF": return "Cave of the Forlorn entrance, E Snowfield."
        case "CS/CS": return "Consecrated Snowfield grace, S Snowfield."
        case "CS/CSC": return "Consecrated Snowfield Catacombs entrance, SE Snowfield."
        case "CS/HPH": return "Hidden Path to the Haligtree exit, SE Snowfield."
        case "CS/ICS": return "Inner Consecrated Snowfield grace, S Snowfield."
        case "CS/ME": return "Minor Erdtree, NE Snowfield."
        case "CS/OLT": return "Ordina, Liturgical Town grace, N Snowfield."
        case "CS/YAR": return "Yelough Anix Ruins grace, W Snowfield."
        case "CS/YAT": return "Yelough Anix Tunnel entrance, SW Snowfield."

        # Consecrated Snowfield Dungeons
        # Consecrated Snowfield Catacombs
        case "CS/(CSC)": return "Consecrated Snowfield Catacombs, SE Snowfield."

        # Cave of the Forlorn
        case "CS/(CF)": return "Cave of the Forlorn, NE Snowfield."

        # Yelough Anix Tunnel
        case "CS/(YAT)": return "Yelough Anix Tunnel, W Snowfield."

        # Mohgwyn Palace
        case "MP/(MDM)": return "Mohgwyn Dynasty Mausoleum, SW Mohgwyn."
        case "MP/MDE": return "Dynasty Mausoleum Entrance grace, N Mohgwyn."
        case "MP/PALR": return "Palace Approach Ledge-Road grace, SE Mohgwyn."
        case "MP/PALR|(MDM)": return "Blood lake below Palace Approach Ledge-Road, or by the Mohgwyn Dynasty Mausoleum elevator."

        # Miquella's Haligtree
        case "MH/HC": return "Haligtree Canopy grace."
        case "MH/HT": return "Haligtree Town grace."
        case "MH/HTP": return "Haligtree Town Plaza grace."

        # Elphael, Brace of the Haligtree
        case "EBH/DC": return "Drainage Channel grace."
        case "EBH/EIW": return "Elphael Inner Wall grace."
        case "EBH/HP": return "Haligtree Promenade grace."
        case "EBH/HR": return "Haligtree Roots grace, Malenia."
        case "EBH/PR": return "Prayer Room grace."

        # Leyndell, Ashen Capital
        case "LAC/FL": return "Ashen Capital, reached by backtracking from Forbidden Lands."
        case "LAC/LCA": return "Leyndell, Capital of Ash grace."
        case "LAC/QB": return "Queen's Bedchamber grace, Ashen Capital."
        case "LAC/RC": return "Royal Colosseum area, Goldmask spot, Ashen Capital."

        # Erdtree
        case "ET": return "Erdtree, Elden Beast arena."

        # ---- DLC ----
        # Roundtable Hold DLC Only
        case "RH/DLC": return "Roundtable Hold, shop stock only available with DLC."

        # Gravesite Plain
        case "GP/(AAV)": return "Abandoned Ailing Village landmark, N Gravesite Plain."
        case "GP/(AS)": return "Artist's Shack landmark, SW Gravesite Plain."
        case "GP/(CB)": return "Church of Benediction landmark, S Gravesite Plain."
        case "GP/(CC)": return "Church of Consolation landmark, SE Gravesite Plain."
        case "GP/(EG)": return "Ellac Greatbridge landmark, N Gravesite Plain."
        case "GP/(EH)": return "Elder's Hovel landmark, E Gravesite Plain."
        case "GP/(PT)": return "Prospect Town landmark, SW Gravesite Plain."
        case "GP/(RDTR)": return "Run-Down Traveler's Rest landmark, under Ellac Greatbridge."
        case "GP/(SP)": return "Suppressing Pillar landmark, SE Gravesite Plain."
        case "GP/(SR)": return "Scorched Ruins landmark, S Gravesite Plain."
        case "GP/(WNM)": return "Western Nameless Mausoleum, SW Gravesite Plain."
        case "GP/AS": return "Artist's Shack grace, SW Gravesite Plain."
        case "GP/BG": return "Belurat Gaol area, NW Gravesite Plain, SW of the dragon lake."
        case "GP/CB": return "Church of Benediction grace, S tip of Cliffroad Terminus."
        case "GP/CC": return "Road from Scorched Ruins to Church of Consolation, SE Gravesite Plain."
        case "GP/CF": return "Castle Front grace, NE Gravesite Plain."
        case "GP/CRT": return "Cliffroad Terminus grace, SW Gravesite Plain."
        case "GP/GN": return "Greatbridge, North grace, NW Gravesite Plain."
        case "GP/GP": return "Gravesite Plain grace, S Gravesite Plain."
        case "GP/MGC": return "Main Gate Cross grace, W Gravesite Plain."
        case "GP/PPC": return "Pillar Path Cross grace, NE Gravesite Plain."
        case "GP/PPW": return "Pillar Path Waypoint grace, E Gravesite Plain."
        case "GP/PT": return "Prospect Town area, SW Gravesite Plain."
        case "GP/SP": return "Suppressing Pillar grace, SE Gravesite Plain."
        case "GP/SR": return "Scorched Ruins grace, SE Gravesite Plain."
        case "GP/TPC": return "Three-Path Cross grace, mid Gravesite Plain."

        # Gravesite Plain Dungeons
        # Fog Rift Catacombs
        case "GP/(FRC)": return "Fog Rift Catacombs, N Gravesite Plain."

        # Belurat Gaol
        case "GP/(BG)": return "Belurat Gaol, W Gravesite Plain."

        # Dragon's Pit
        case "GP/(DP)": return "Dragon's Pit, SE Gravesite Plain."

        # Ruined Forge Lava Intake
        case "GP/(RFLI)": return "Ruined Forge Lava Intake, SE Gravesite Plain."

        # Belurat
        case "BTS/BTS": return "Belurat, Tower Settlement grace."
        case "BTS/SF": return "Stagefront grace, before Divine Beast Dancing Lion."
        case "BTS/SPA": return "Small Private Altar grace."
        case "BTS/TDB": return "Theatre of the Divine Beast grace."

        # Castle Ensis
        case "CE/CEC": return "Castle Ensis Checkpoint grace."
        case "CE/CF": return "Castle Front grace, W Castle Ensis."
        case "CE/CLC": return "Castle Lord's Chamber grace, Rellana."

        # Fog Rift Fort
        case "CE/(FRF)": return "Fog Rift Fort, SE Scadu Altus."

        # Jagged Peak
        # Jagged Peak Foot
        case "JP/DPT": return "Dragon's Pit Terminus grace."
        case "JP/FJP": return "Foot of the Jagged Peak grace."
        case "JP/GADC": return "Grand Altar of Dragon Communion grace."

        case "JP/JPM": return "Jagged Peak Mountainside grace."
        case "JP/JPS": return "Jagged Peak Summit grace, Bayle the Dread."

        # Charo's Hidden Grave
        case "CHG/CHG": return "Charo's Hidden Grave grace."
        case "CHG/LG": return "Lamenter's Gaol grace, outside the gaol."

        # Charo's Hidden Grave Dungeon
        # Lamenter's Gaol (Upper)
        case "CHG/(LG)": return "Lamenter's Gaol."

        # Scadu Altus
        case "SA/(BV)": return "Bonny Village landmark, E Scadu Altus."
        case "SA/(CC)": return "Church of the Crusade landmark, NW Scadu Altus."
        case "SA/(FR)": return "Fort of Reprimand landmark, S Scadu Altus."
        case "SA/(MR)": return "Moorth Ruins landmark, mid Scadu Altus."
        case "SA/(RR)": return "Rabbath's Rise landmark, NE Scadu Altus."
        case "SA/(WH)": return "Whipping Hut landmark, E of Bonny Village."
        case "SA/BFR": return "Behind the Fort of Reprimand grace, S Scadu Altus."
        case "SA/BLV": return "Bridge Leading to the Village grace, NE Scadu Altus."
        case "SA/BV": return "Bonny Village grace, mid Scadu Altus."
        case "SA/CC": return "Church of the Crusade grace, NW Scadu Altus."
        case "SA/CDH": return "Church District Highroad grace, NE Scadu Altus."
        case "SA/CMM": return "Cathedral of Manus Metyr grace, E Scadu Altus."
        case "SA/FR": return "Fort of Reprimand grace, S Scadu Altus."
        case "SA/HC": return "Highroad Cross grace, NW Scadu Altus."
        case "SA/MHS": return "Moorth Highway, South grace, SW Scadu Altus."
        case "SA/MR": return "Moorth Ruins grace, mid Scadu Altus."
        case "SA/RFSP": return "Ruined Forge of Starfall Past entrance, SW Scadu Altus."
        case "SA/SAW": return "Scadu Altus, West grace, above lower Castle Ensis."
        case "SA/SC": return "Scaduview Cross grace, SE Scadu Altus."

        # Scadu Altus Dungeons
        # Bonny Gaol
        case "SA/(BG)": return "Bonny Gaol."

        # Ruined Forge of Starfall Past
        case "SA/(RFSP)": return "Ruined Forge of Starfall Past."

        # Rauh Ruins Limited
        case "SA/ARR": return "Rauh Ruins Limited, use infused stonesword key."

        # Cathedral of Manus Metyr
        # Finger Ruins of Miyr
        case "FRM": return "Finger Ruins of Miyr."
        case "SA/(CMM)": return "Cathedral of Manus Metyr."

        # Rauh Base
        case "RB/(NNM)": return "Northern Nameless Mausoleum, SE Rauh Base."
        case "RB/(TTR)": return "Temple Town Ruins landmark, S Rauh Base."
        case "RB/ARB": return "Ancient Ruins Base grace, NE Rauh Base."
        case "RB/NNM": return "Northern Nameless Mausoleum grace, Rauh Base."
        case "RB/RN": return "Ravine North grace, NW Rauh Base."
        case "RB/SRC": return "Scorpion River Catacombs entrance, NW Rauh Base."
        case "RB/TRF": return "Taylew's Ruined Forge entrance, NE Rauh Base."
        case "RB/TTR": return "Temple Town Ruins grace, mid Rauh Base."

        # Rauh Base Dungeons
        # Scorpion River Catacombs
        case "RB/(SRC)": return "Scorpion River Catacombs."

        # Taylew's Ruined Forge
        case "RB/(TRF)": return "Taylew's Ruined Forge."

        # Ellac River
        case "ER/ERC": return "Ellac River Cave grace, Ellac River North."
        case "ER/ERD": return "Ellac River Downstream grace."
        case "ER/RC": return "Rivermouth Cave entrance, Ellac River."

        # Ellac River Dungeon
        # Rivermouth Cave
        case "ER/(RC)": return "Rivermouth Cave."

        # Cerulean Coast
        case "CC/CC": return "Cerulean Coast grace."
        case "CC/CCC": return "Cerulean Coast Cross grace."
        case "CC/CCW": return "Cerulean Coast West grace."

        # Finger Ruins of Rhia
        case "CC/FRR": return "Finger Ruins of Rhia approach, E beach."
        case "FRR": return "Finger Ruins of Rhia."
        case "FRR/(FWH)": return "Finger-Weaver's Hovel landmark, SE Finger Ruins of Rhia."

        # Stone Coffin Fissure
        case "SCF/FC": return "Fissure Cross grace."
        case "SCF/FD": return "Fissure Depths grace, Putrescent Knight."
        case "SCF/FW": return "Fissure Waypoint grace."
        case "SCF/GDP": return "Garden of Deep Purple grace, St. Trina."
        case "SCF/SCF": return "Stone Coffin Fissure grace."

        # Shadow Keep
        case "SK/MGP": return "Main Gate Plaza grace."
        case "SK/SKMG": return "Shadow Keep Main Gate grace, Golden Hippopotamus."

        # Shadow Keep Storehouse
        case "Cross": return "Any Miquella's Cross, after defeating Messmer."
        case "SK/DCE": return "Dark Chamber Entrance grace, Messmer."
        case "SK/SFiF": return "Storehouse, Fifth Floor grace."
        case "SK/SFoF": return "Storehouse, Fourth Floor grace."
        case "SK/SSF": return "Storehouse, Seventh Floor grace."

        # Shadow Keep Storehouse Back
        case "SK/SBS": return "Storehouse, Back Section grace."
        case "SK/SL": return "Storehouse, Loft grace."
        case "ScV/SKBG": return "Shadow Keep, Back Gate grace, Commander Gaius."

        # Shadow Keep, West Rampart
        case "SK/SFF": return "Storehouse, First Floor grace."
        case "SK/WR": return "West Rampart grace."

        # Shadow Keep, Church District
        case "SK/CDE": return "Church District Entrance grace."

        # Shadow Keep, Church District Lower
        case "SK/SC": return "Sunken Chapel grace."
        case "SK/TWS": return "Tree-Worship Sanctum grace."

        # Scaduview
        case "ScV/(AS)": return "Albinauric Shack, W Scaduview."
        case "ScV/(SC)": return "Scadutree Chalice, N Scaduview."

        # Scadutree Base
        case "SB/TWS": return "Scadutree Base, Scadutree Avatar arena."

        # Ancient Ruins of Rauh
        case "ARR/ARGS": return "Ancient Ruins, Grand Stairway grace."
        case "ARR/CBME": return "Church of the Bud, Main Entrance grace, Romina."
        case "ARR/CMBE": return "Below the Grand Stairway elevator, toward Church of the Bud."
        case "ARR/RARE": return "Rauh Ancient Ruins, East grace."
        case "ARR/RARW": return "Rauh Ancient Ruins, West grace."
        case "ARR/VMT": return "Viaduct Minor Tower grace."

        # Hinterland
        case "HL/(SV)": return "Shaman Village landmark, Hinterland."
        case "HL/FH": return "Fingerstone Hill grace, Hinterland."
        case "HL/HB": return "Hinterland Bridge grace."
        case "HL/HL": return "Hinterland grace."

        # Finger Ruins of Dheo
        case "FRD": return "Finger Ruins of Dheo."

        # Recluses' River
        case "RR/(ENM)": return "Eastern Nameless Mausoleum, SE Scadu Altus."
        case "RR/(RU)": return "Ruins of Unte landmark, NW Recluses' River."
        case "RR/(VF)": return "Village of Flies landmark, S Recluses' River."
        case "RR/CWH": return "Castle Watering Hole grace, NW Scadu Altus."
        case "RR/RRD": return "Recluses' River Downstream grace."
        case "RR/RRU": return "Recluses' River Upstream grace."
        case "RR/RU": return "Ruins of Unte grace, N Recluses' River."

        # Recluses' River Dungeon
        # Darklight Catacombs
        case "RR/(DC)": return "Darklight Catacombs, W Scadu Altus."

        # Abyssal Woods
        case "AW/(AC)": return "Abandoned Church landmark, SE Abyssal Woods."
        case "AW/AC": return "Abandoned Church grace, SE Abyssal Woods."
        case "AW/AW": return "Abyssal Woods grace."
        case "AW/DF": return "Divided Falls grace, NW Abyssal Woods."
        case "AW/MM": return "Midra's Manse grace, outside the manse."
        case "AW/WT": return "Woodland Trail grace, mid Abyssal Woods."

        # Midra's Manse
        case "MM/MH": return "Manse Hall grace."
        case "MM/ML": return "Midra's Library grace."
        case "MM/SFC": return "Second Floor Chamber grace, Midra."

        # Enir-Ilim
        case "BTS|EI/SR": return "End of the long drop from Spiral Rise down to Belurat."
        case "EI/CCA": return "Cleansing Chamber Anteroom grace."
        case "EI/DGFS": return "Divine Gate Front Staircase grace, Promised Consort Radahn."
        case "EI/FR": return "First Rise grace."
        case "EI/GD": return "Gate of Divinity grace."
        case "EI/OW": return "Outer Wall grace."
        case "EI/SR": return "Spiral Rise grace."
        case _: return ""

# make multiple regions be under one label
def find_label(region: str) -> str:
    if region in ("Coastal Cave", "Church of Dragon Communion", "Groveside Cave", "Stormfoot Catacombs", "Limgrave Tunnels"
                  , "Murkwater Cave", "Murkwater Catacombs", "Highroad Cave", "Deathtouched Catacombs", "Fringefolk Hero's Grave"):
        return "Limgrave Dungeons"

    if region in ("Stormveil Start", "Stormveil Castle", "Stormveil Throne", "Divine Tower of Limgrave"):
        return "Stormveil Castle"

    if region in ("Impaler's Catacombs", "Tombsward Catacombs", "Tombsward Cave", "Morne Tunnel", "Earthbore Cave"):
        return "Weeping Peninsula Dungeons"

    if region in ("Road's End Catacombs", "Black Knife Catacombs", "Cliffbottom Catacombs", "Stillwater Cave"
                  , "Lakeside Crystal Cave", "Academy Crystal Cave", "Raya Lucaria Crystal Tunnel"):
        return "Liurnia of The Lakes Dungeons"

    if region in ("Carian Study Hall", "Carian Study Hall (Inverted)"):
        return "Carian Study Hall"

    if region in ("The Four Belfries (Chapel of Anticipation)", "The Four Belfries (Nokron)", "The Four Belfries (Farum Azula)"):
        return "The Four Belfries"

    if region in ("Raya Lucaria Academy", "Raya Lucaria Academy Main", "Raya Lucaria Academy Chest", "Raya Lucaria Academy Library"):
        return "Raya Lucaria Academy"

    if region in ("Caelid Catacombs", "Gaol Cave", "Sellia Crystal Tunnel", "Abandoned Cave", "Minor Erdtree Catacombs", "Gael Tunnel"):
        return "Caelid Dungeons"

    if region in ("Redmane Castle Post Radahn", "Wailing Dunes", "War-Dead Catacombs"):
        return "Radahn Festival"

    if region in ("Dragonbarrow Cave", "Sellia Hideaway", "Divine Tower of Caelid"):
        return "Dragonbarrow Dungeons"

    if region in ("Nokron, Eternal City", "Nokron, Eternal City Start"):
        return "Nokron, Eternal City"

    if region in ("Deeproot Depths Upper", "Deeproot Depths", "Deeproot Depths Boss"):
        return "Deeproot Depths"

    if region in ("Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto", "Sage's Cave", "Old Altus Tunnel", "Altus Tunnel", "Wyndham Catacombs"):
        return "Altus Plateau Dungeons"

    if region in ("Gelmir Hero's Grave", "Seethewater Cave", "Volcano Cave"):
        return "Mt. Gelmir Dungeons"

    if region in ("Volcano Manor Dungeon", "Volcano Manor Entrance", "Volcano Manor Drawing Room", "Volcano Manor", "Volcano Manor Upper"):
        return "Volcano Manor"

    if region in ("Auriza Hero's Grave", "Auriza Side Tomb", "Sealed Tunnel"):
        return "Capital Outskirts Dungeons"

    if region in ("Leyndell, Royal Capital", "Leyndell, Royal Capital Unmissable", "Leyndell, Royal Capital Throne", "Divine Bridge"):
        return "Leyndell, Royal Capital"

    if region in ("Subterranean Shunning-Grounds", "Leyndell Catacombs"):
        return "Subterranean Shunning-Grounds"

    if region in ("Divine Tower of East Altus", "Forbidden Lands"):
        return "Forbidden Lands"    

    if region in ("Giants' Mountaintop Catacombs", "Spiritcaller Cave"):
        return "Mountaintops of the Giants Dungeons"    

    if region in ("Giant-Conquering Hero's Grave"):
        return "Flame Peak Dungeon"    

    if region in ("Farum Azula", "Farum Azula Main"):
        return "Farum Azula"        

    if region in ("Consecrated Snowfield Catacombs", "Cave of the Forlorn", "Yelough Anix Tunnel"):
        return "Consecrated Snowfield Dungeons"        

    if region in ("Leyndell, Ashen Capital", "Leyndell, Ashen Capital Throne"):
        return "Leyndell, Ashen Capital"


    # DLC

    if region in ("Fog Rift Catacombs", "Belurat Gaol", "Dragon's Pit", "Ruined Forge Lava Intake"):
        return "Gravesite Plain Dungeons"

    if region in ("Belurat", "Belurat Swamp"):
        return "Belurat"    

    if region in ("Jagged Peak", "Jagged Peak Foot"):
        return "Jagged Peak"    

    if region in ("Lamenter's Gaol (Entrance)", "Lamenter's Gaol (Upper)", "Lamenter's Gaol (Lower)"):
        return "Charo's Hidden Grave Dungeon"    

    if region in ("Bonny Gaol", "Ruined Forge of Starfall Past", "Rauh Ruins Limited"):
        return "Scadu Altus Dungeons"    

    if region in ("Cathedral of Manus Metyr", "Finger Ruins of Miyr"):
        return "Cathedral of Manus Metyr"    

    if region in ("Scorpion River Catacombs", "Taylew's Ruined Forge"):
        return "Rauh Base Dungeons"    

    if region in ("Cerulean Coast", "Finger Ruins of Rhia"):
        return "Cerulean Coast"   

    if region in ("Rivermouth Cave"):
        return "Ellac River Dungeon"    

    if region in ("Shadow Keep", "Shadow Keep Storehouse", "Shadow Keep Storehouse Back", "Shadow Keep, West Rampart", "Shadow Keep, Church District", "Shadow Keep, Church District Lower"):
        return "Shadow Keep"    

    if region in ("Hinterland", "Finger Ruins of Dheo"):
        return "Hinterland" 

    if region in ("Darklight Catacombs"):
        return "Recluses' River Dungeon"    

    # if nothing return region
    return region

if __name__ == '__main__':
    all_initials = []
    for region in location_tables:
        region_initals_to_description.setdefault(region, {})
        for location in location_tables[region]:
            initial = location.name[:location.name.find(":")]
            if initial not in all_initials and initial not in region_initals_to_description[region]:
                region_initals_to_description[region][initial] = find_description(initial)
                all_initials.append(initial) # removes dupe initials

    header = "<tr><th>Code</th><th>Description</th></tr>\n"
    table = "## Base Game\n<table>\n" + header
    last_region = ""
    for (region, inital_dict) in sorted(
        region_initals_to_description.items(),
        key = lambda pair: location_tables[pair[0]][0].region_value
    ):
        if region == "Roundtable Hold DLC Only":
            table += f"</table><br><div>\n\n## DLC\n\n</div><table>\n" + header
        if last_region != find_label(region):
            last_region = find_label(region)
            table += f"<tr><td colspan=\"2\"><h3>\n\n### {html.escape(last_region)}\n\n</td></tr>\n"
        for (initial, description) in sorted(
            inital_dict.items(),
            key = lambda pair: pair[0]
        ):
            table += f"<tr><td><strong>{html.escape(initial)}</strong></td><td>{html.escape(description)}</td></tr>\n"
    table += "</table>\n"
    # print(table)

    with open(
        os.path.join(os.path.dirname(__file__), 'en_region_guide.md'),
        'r+',
        encoding='utf-8'
    ) as f:
        original = f.read()
        start_flag = "<!-- begin region table -->\n"
        start = original.index(start_flag) + len(start_flag)
        end = original.index("<!-- end region table -->")

        f.seek(0)
        f.write(original[:start] + table + original[end:])
        f.truncate()

    print("Updated docs/en_region_guide.md!")

