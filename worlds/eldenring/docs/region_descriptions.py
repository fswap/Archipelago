# python -m worlds.eldenring.docs.region_descriptions

from typing import Dict
import os
import html

from worlds.eldenring.locations import location_tables
from worlds.eldenring.region_names import region_order, region_order_dlc

# region to inital to description
region_initals_to_description: Dict[str, Dict[str, str]] = {}

# add descriptions to initials
def find_description(initial: str) -> str:
    match initial:
        # limgrave
        case "LG/(BS)": return "Bridge of Sacrifice landmark, connection point between S Limgrave and Weeping Peninsula."
        case "LG/(AS)": return "Artist's Shack landmark, Mid Limgrave."
        case "LG/(CE)": return "Church of Elleh landmark, W Limgrave."
        case "LG/(DBR)": return "Dragon-Burnt Ruins landmark, S Limgrave."
        case "LG/(FH)": return "Fort Haight landmark, E Limgrave."
        case "LG/(FHE)": return "Forlorn Hound Evergaol, S Limgrave."
        case "LG/(GR)": return "Gatefront Ruins landmark, Mid Limgrave."
        case "LG/(MR)": return "Mistwood Ruins landmark, E Limgrave."
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
        case "LG/(SGr)": return "Stranded Graveyard landmark, SW Limgrave."
        case "LG/SR": return "Seaside Ruins grace, SW Limgrave."
        case "LG/SRW": return "Siofra River Well landmark, E Limgrave."        
        case "LG/SWV": return "Summonwater Village landmark, NE Limgrave."
        case "LG/SWVO": return "Summonwater Village Outskirts grace, NE Limgrave."
        case "LG/TCM": return "Third Church of Marika landmark, E Limgrave."
        case "LG/TFS": return "The First Step grace, SW Limgrave."
        case "LG/WR": return "Waypoint Ruins landmark, Mid Limgrave."
        
        # stormhill
        case "LG/(SE)": return "Stormhill Evergaol, S Stormhill."
        case "LG/(SGa)": return "Stormgate landmark, S Stormhill."
        case "LG/(SS)": return "Stormhill Shack landmark, W Stormhill."
        case "LG/(WS)": return "Warmaster's Shack landmark, mid Stormhill."
        case "LG/DC": return "Deathtouched Catacombs landmark, NE Stormhill."
        case "LG/LC": return "Limgrave Colosseum landmark, N Stormhill."
        case "LG/SB": return "Saintsbridge grace, E Stormhill."
        case "LG/SS": return "Stormhill Shack grace, W Stormhill."
        case "LG/SV": return "Stormveil landmark, area S of Margit arena or right of Stormveil on the bridge to Liurnia."
        case "LG/WS": return "Warmaster's Shack grace, mid Stormhill."
        case "SV/CT": return "Castleward Tunnel grace, Stormveil enterance."
                        
        # limgrave dungeons
        case "LG/(CC)": return "Coastal Cave, SW Limgrave."
        case "LG/(CDC)": return "Church of Dragon Communion, through Coastal Cave SW Limgrave."
        case "LG/(GC)": return "Groveside Cave, W Limgrave."
        case "LG/(SC)": return "Stormfoot Catacombs, W Limgrave."
        case "LG/(LT)": return "Limgrave Tunnels, W Limgrave."
        case "LG/(MCV)": return "Murkwater Cave, Mid Limgrave."
        case "LG/(MCC)": return "Murkwater Catacombs, Mid Limgrave."
        case "LG/(HC)": return "Highroad Cave, N Limgrave."
        case "LG/(DC)": return "Deathtouched Catacombs, E Stormhill."
        case "LG/(FHG)": return "Fringefolk Hero's Grave, W Limgrave."
        
        case "RH": return "Roundtable Hold."
        
        # stormveil
        case "SV/GC": return "Gateside Chamber grace."
        case "SV/LC": return "Liftside Chamber grace."
        case "SV/LTB": return "Limgrave Tower Bridge grace."
        case "SV/RT": return "Rampart Tower grace."
        case "SV/SMG": return "Stormveil Main Gate grace."
        case "SV/SeC": return "Secluded Cell grace."
        case "SV/StC": return "Stormveil Cliffside grace."
        case "SV/GG": return "Godrick the Grafted grace, in Godrick's arena."
        case "SV/LL": return "Liurnia side of Stormveil, after Godrick's arena."
        case "SV/(DTL)": return "Divine Tower of Limgrave landmark."
        
        
        # weeping
        case "WP/(AV)": return "Ailing Village landmark, mid Weeping."
        case "WP/(CBC)": return "Callu Baptismal Church, mid Weeping."
        case "WP/(CM)": return "Castle Morne landmark, S Weeping."
        case "WP/(CP)": return "Church of Pilgrimage landmark, N Weeping."
        case "WP/(DHFR)": return "Demi-Human Forest Ruins landmark, N Weeping."
        case "WP/(FCM)": return "Fourth Church of Marika landmark, NW Weeping."
        case "WP/(FLT)": return "Forest Lookout Tower landmark, NE Weeping."
        case "WP/(IMS)": return "Isolated Merchant's Shack landmark, W Weeping."
        case "WP/(OR)": return "Oridys's Rise landmark, E Weeping."
        case "WP/(TwR)": return "Tombsward Ruins landmark, NW Weeping."
        case "WP/(WE)": return "Weeping Evergaol, NW Weeping."
        case "WP/(WR)": return "Witchbane Ruins landmark, NW Weeping."
        case "WP/AV": return "Ailing Village landmark, mid Weeping."
        case "WP/BCPG": return "Beside the Crater-Pocked Glade grace, NE Weeping."
        case "WP/BS": return "Bridge of Sacrifice grace, N Weeping."
        case "WP/CM": return "Castle Morne landmark, S Weeping."
        case "WP/CMR": return "Castle Morne Rampart grace, E Weeping."
        case "WP/CP": return "Church of Pilgrimage grace, N Weeping."
        case "WP/DHFR": return "Demi-Human Forest Ruins landmark, N Weeping."
        case "WP/EC": return "Earthbore Cave landmark, N Weeping."
        case "WP/FLT": return "Forest Lookout Tower landmark, NE Weeping."
        case "WP/ME": return "Minor Erdtree, mid Weeping."
        case "WP/MT": return "Morne Tunnel landmark, mid Weeping."
        case "WP/OR": return "Oridys's Rise landmark, E Weeping."
        case "WP/SLT": return "South of the Lookout Tower grace, NE Weeping."
        case "WP/ToR": return "Tower of Return landmark, SW Weeping."
        case "WP/TwR": return "Tombsward Ruins landmark, NW Weeping."
        case "WP/WR": return "Witchbane Ruins landmark, NW Weeping."
        
        # weeping dungeons
        case "WP/(IC)": return "Impaler's Catacombs, NE Weeping."
        case "WP/(TCC)": return "Tombsward Catacombs, mid Weeping."
        case "WP/(TCV)": return "Tombsward Cave, W Weeping."
        case "WP/(MT)": return "Morne Tunnel, mid Weeping."
        case "WP/(EC)": return "Earthbore Cave, N Weeping."
        
        # siofra
        case "SR/(HG)": return "Hallowhorn Grounds landmark, SE Siofra."
        case "SR/BW": return "Below The Well grace, N Siofra."
        case "SR/SRB": return "Siofra River Bank grace, S Siofra."
        case "SR/SRWD": return "Siofra River Well Depths grace, SW Siofra."
        case "SR/WW": return "Worshippers' Woods grace, mid Siofra."
        
        case "": return "."
        case "": return "."

        # liurnia
        
        # study hall
        case "LL/(CSH)N": return "Carian Study Hall normal."
        case "LL/(CSH)I": return "Carian Study Hall inverted."
        case "LL/(DV)": return "Divine Tower of Liurnia."
        case "LL/LTB": return "Liurnia Tower Bridge grace, after CSH."
        
        case "LL/(TFB/CA)": return "The Four Belfries (Chapel of Anticipation)"
        case "LL/(TFB/NEC)": return "The Four Belfries (Nokron)"
        case "LL/(TFB/FA)": return "The Four Belfries (Farum Azula)"
        
        
        
        case "CL/(WD)": return "Wailing Dunes."
        case "CL/(WDC)": return "War-Dead Catacombs, N of Wailing Dunes."
        
        case "DB/(DC)": return "Dragonbarrow Cave."
        case "DB/(SH)": return "Sellia Hideaway."
        case "DB/(DT)": return "Divine Tower of Caelid."
        
        
        
        
        
        
        case "FP/(GCHG)": return "Giant-Conquering Hero's Grave."
        
        # DLC
        
        # gravesite plains
        case "GP/(AAV)": return "Abandoned Ailing Village."
        case "GP/(AS)": return "Artist Shack."
        case "GP/(CB)": return "Church of Benediction."
        case "GP/(CC)": return "Church of Consolation."
        case "GP/(EG)": return "Ellac Greatbridge."
        case "GP/(EH)": return "Elder's Hovel."
        case "GP/(PT)": return "Prospect Town."
        case "GP/(RDTR)": return "Run-Down Traveler's Rest."
        case "GP/(SP)": return "Suppressing Pillar."
        case "GP/(SR)": return "Scorched Ruins."
        case "GP/(WNM)": return "Western Nameless Mausoleum."
        case "GP/AS": return "Northwest of Artist Shack on Cliffside."
        case "GP/BG": return "Belurat Gaol."
        case "GP/CB": return "Church of Benediction."
        case "GP/CC": return "Church of Consolation."
        case "GP/CF": return "Castle Front Grace."
        case "GP/CRT": return "Cliffroad Terminus Grace."
        case "GP/GN": return "Greatbridge North Grace."
        case "GP/GP": return "Gravesite Plain Grace."
        case "GP/MGC": return "Main Gate Cross Grace."
        case "GP/PPC": return "Pillar Path Cross Grace."
        case "GP/PPW": return "Pillar Path Waypoint Grace."
        case "GP/PT": return "Prospect Town."
        case "GP/SP": return "Suppressing Pillar."
        case "GP/SR": return "Scorched Ruins."
        case "GP/TPC": return "Three-Path Cross Grace."
        case "CHG/(LG)": return "Lamenter's Gaol."
    
        #Gravesite Plain dungeons
        case "GP/(FRC)": return "Fog Rift Catacombs."
        case "GP/(BG)": return "Belurat Gaol."
        case "GP/(DP)": return "Dragon's Pit."
        case "GP/(RFLI)": return "Ruined Forge Lava Intake."

        #Belurat
        case "BTS/BTS": return "Belurat, Tower Settlement Grace."
        case "BTS/SF": return "Stagefront Grace."
        case "BTS/SPA": return "Small Private Altar Grace."
        case "BTS/TDB": return "Theater of the Divine Beast Grace."

        #Castle Ensis
        case "CE/CEC": return "Castle Ensis Checkpoint Grace."
        case "CE/CF": return "Castle Front."
        case "CE/CLC": return "Castle-Lord's Chamber Grace."

        #Fog Rift Fort
        case "CE/(FRF)": return "Fog Rift Fort to northeast of Castle Ensis"

        #Jagged Peak
        case "JP/DPT": return "Dragon's Pit Terminus Grace."
        case "JP/FJP": return "Foot of the Jagged Peak Grace."
        case "JP/GADC": return "Grand Altar of Dragon Communion Grace."
        case "JP/JPM": return "Jagged Peak Mountainside Grace."
        case "JP/JPS": return "Jagged Peak Summit Grace."

        #Charo's Hidden Grave
        case "CHG/CHG": return "Charo's Hidden Grave Grace."
        case "CHG/LG": return "Lamentor's Gaol Grace."

        #Scadu Altus
        case "SA/(BV)": return "Bonny Village."
        case "SA/(CC)": return "Church of the Crusade."
        case "SA/(FR)": return "Fort of Reprimand."
        case "SA/(MR)": return "Moorth Ruins."
        case "SA/(RR)": return "Rabbath's Rise."
        case "SA/(WH)": return "Whipping Hut."
        case "SA/BFR": return "Behind the Fort of Reprimand Grace."
        case "SA/BLV": return "Bridge Leeading to Village Grace."
        case "SA/BV": return "Bonny Village Grace."
        case "SA/CC": return "Church of the Crusade."
        case "SA/CDH": return "Church District Highroad Grace."
        case "SA/CMM": return "Cathedral of Manus Metyr."
        case "SA/FR": return "Fort of Reprimand."
        case "SA/HC": return "Highroad Cross Grace."
        case "SA/MHS": return "Moorth Highway, South Grace."
        case "SA/MR": return "Moorth Ruins Grace."
        case "SA/RFSP": return "Ruined Forge of Starfall Past Grace."
        case "SA/SAW": return "Scadu Altus West Grace."
        case "SA/SC": return "Scaduview Cross Grace, Up the Sealed Spiritspring."
            
        #Scadu Altus Dungeons
        case "SA/(BG)": return "Bonny Gaol."
        case "SA/(RFSP)": return "Ruined Forge of Starfall Past."
        case "SA/ARR": return "Rauh Ruins Limited, use infused stonesword key."

        #Cathedral of Manus Metyr
        case "FRM": return "Finger Ruins of Miyr."
        case "SA/(CMM)": return "Cathedral of Manus Metyr."

        #Shadow Keep
        case "SK/MGP": return "Main Gate Plaza Grace."
        case "SK/SKMG": return "Shadow Keep Main Gate Grace."
        case "Cross": return "Message From Leda - by any cross after SK Main Boss."
        case "SK/DCE": return "Dark Chamber Entrance."
        case "SK/SFiF": return "Storehouse, First Floor Grace."
        case "SK/SFoF": return "Storehouse, Fourth Floor Grace."
        case "SK/SSF": return "Storehouse, Seventh Floor Grace."
        case "SK/SBS": return "Storehouse, Back Section Grace."
        case "SK/SL": return "Storehouse, Loft Grace."
        case "ScV/SKBG": return "Shadow Keep, Back Gate Grace."
        case "SK/SFF": return "Storehouse, First Floor Grace."
        case "SK/WR": return "West Rampart Grace."
        case "SK/CDE": return "Church District Entrance."
        case "SK/SC": return "Sunken Chapel Grace."
        case "SK/TWS": return "Tree-Worship Passage Grace."
    
        #Rauh Base Dungeons
        case "RB/(SRC)": return "Scorpion River Catacombs."
        case "RB/(TRF)": return "Taylew's Ruined Forge."

        #Rauh Base
        case "RB/(NNM)": return "Northern Nameless Ruins."
        case "RB/(TTR)": return "Temple Town Ruins."
        case "RB/ARB": return "Ancient Ruine Base."
        case "RB/NNM": return "Northern Nameless Mausoleum."
        case "RB/RN": return "Ravine North Grace."
        case "RB/SRC": return "Scorpion River Catacombs."
        case "RB/TRF": return "Taylew's Ruined Forge Grace."
        case "RB/TTR": return "Temple Town Ruins."
            
        #Cerulean Coast
        case "CC/CC": return "Cerulean Coast Grace."
        case "CC/CCC": return "Cerulean Coast Cross Grace."
        case "CC/CCW": return "Cerulean Coast West Grace."
        case "CC/FRR": return "Finger Ruine of Rhia Grace."
        case "FRR": return "Finger Ruins of Rhia."
        case "FRR/(FWH)": return "Finger-Weaver's Hovel landmark, SE Finger Ruins of Rhia."

        #Stone Coffin Fissure
        case "SCF/FC": return "Fissure Cross Grace."
        case "SCF/FD": return "Fissure Depths Grace."
        case "SCF/FW": return "Fissure Waypoint Grace."
        case "SCF/GDP": return "Garden of Deep Purple Grace."
        case "SCF/SCF": return "Stone Coffin Fissure Grace."

            
        #Ellac River
        case "ER/ERC": return "Ellac River Cave."
        case "ER/ERD": return "Ellac River Downstream."
        case "ER/RC": return "Rivermouth Cave."
            
        #Ellac River Dungeon
        case "ER/(RC)": return "Rivermouth Cave."

        #Scaduview
        case "ScV/(AS)": return "Albinauric's Shack."
        case "ScV/(SC)": return "Scadutree Chalice."

        #Scadutree Base
        case "SB/TWS": return "Tree-Worship Sanctum Grace."

        #Ancient Ruins of Rauh
        case "ARR/ARGS": return "Ancient Ruins, Grand Stairway Grace."
        case "ARR/CBME": return "Church of the Bud, Main Entrance."
        case "ARR/RARE": return "Rauh Ancient Ruins, East Grace."
        case "ARR/RARW": return "Rauh Ancient Ruins, West Grace."
        case "ARR/VMT": return "Viaduct Minor Tower Grace."
            
        #Hinterland
        case "HL/(SV)": return "Shaman Village."
        case "HL/FH": return "Fingerstone Hill Grace."
        case "HL/HB": return "Hinterland Bridge Grace."
        case "HL/HL": return "Hinterland Grace."
        case "FRD": return "Finger Ruins of Dheo."

        #Recluses' River
        case "RR/(ENM)": return "Eastern Nameless Mausoleum."
        case "RR/(RU)": return "Ruins of Unte."
        case "RR/(VF)": return "Village of the Flies."
        case "RR/CWH": return "Castle Watering Hole Grace."
        case "RR/RRD": return "Recluses' River Downstream Grace."
        case "RR/RRU": return "Recluses' River Upstream Grace."
        case "RR/RU": return "Ruins of Unte."

        #Recluses' River Dungeon
        case "RR/(DC)": return "Darklight Catacombs."

        #Abyssal Woods
        case "AW/(AC)": return "Abandoned Church."
        case "AW/AC": return "Abandoned Churct."
        case "AW/AW": return "Abyssal Wood Grace."
        case "AW/DF": return "Divided Falls Grace."
        case "AW/MM": return "Midra's Manse Grace."
        case "AW/WT": return "Woodland Trail Grace."

        #Midra's Manse
        case "MM/MH": return "Manse hall Grace."
        case "MM/ML": return "Midra's Library Grace."
        case "MM/SFC": return "Second Floor Chamber Grace."

        #Enir-Ilim
        case "BTS|EI/SR": return "Spiral Rise."
        case "EI/CCA": return "Cleansing Chamber Anteroom Grace."
        case "EI/DGFS": return "Divine Gate Front Staircase Grace."
        case "EI/FR": return "First Rise Grace."
        case "EI/GD": return "Gate of Divinty Grace."
        case "EI/OW": return "Enir-Ilim: Outer Wall"
        case "EI/SR": return "Spiral Rise."






    case "": return ""
    return ""

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
                
    table = "## Base Game\n<table border=2px soild white style=\"width:100%\">\n"
    last_region = ""
    for (region, inital_dict) in sorted(
        region_initals_to_description.items(),
        key = lambda pair: location_tables[pair[0]][0].region_value
    ):
        if region == "Roundtable Hold DLC Only":
            table += f"</table><br><div>\n\n## DLC\n\n</div><table border=2px soild white style=\"width:100%\">\n"
        if last_region != find_label(region):
            last_region = find_label(region)
            table += f"<th colspan=\"2\" style=\"text-align: center\">\n\n### {html.escape(last_region)}\n\n</th>\n"
        for (initial, description) in sorted(
            inital_dict.items(),
            key = lambda pair: pair[0]
        ):
            table += f"<tr style=\"height:45px\"><td style=\"text-align: center\"><strong>{html.escape(initial)}</strong></td><td> {html.escape(description)}</td></tr>\n"
    table += "</table>\n"
    
    table += "\n\n## List of All Regions\n"
    table += "<table>\n<tr><th>All Base Game Regions</th></tr>\n"
    for region in region_order:
        table += f"<tr><td>{region}</td></tr>\n"
    table += "<tr><th>All DLC Regions</th></tr>\n"
    table += "<tr><td>Roundtable Hold DLC Only</td></tr>\n"
    for region in region_order_dlc:
        table += f"<tr><td>{region}</td></tr>\n"
    table += "</table>\n"

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
    
    
