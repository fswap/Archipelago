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
        # limgrave
        case "BS": return "Bridge of Sacrifice landmark, connection point between S Limgrave and Weeping Peninsula."
        case "LG/(AS)": return "Artists Shack landmark, Mid Limgrave."
        case "LG/(CE)": return "Church of Elleh landmark, W Limgrave."
        case "LG/(DBR)": return "Dragon-Burnt Ruins landmark, S Limgrave."
        case "LG/(FH)": return "Fort Haight landmark, E Limgrave."
        case "LG/(FHE)": return "Forlorn Hound Evergaol, S Limgrave."
        case "": return ""
        case "": return ""
        case "": return ""
        case "": return ""
        case "": return ""
        case "": return ""
        case "": return ""
        
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
        
        # weeping
        case "WP/BS": return "Bridge of Sacrifice grace."
        
        # roundtable doesn't need one, self explainatory
        
        # stormveil
        case "SV/GG": return "Godrick the Grafted grace in Godrick's arena."
        
        
        # liurnia
        
        # study hall
        case "LL/(CSH)N": return "Carian Study Hall normal."
        case "LL/(CSH)I": return "Carian Study Hall inverted."
        case "LL/(DV)": return "Divine Tower of Liurnia"
        case "LL/LTB": return "Liurnia Tower Bridge grace, after CSH."
        
        
        
        # DLC
        
        # gravesite plains
        case "": return ""
        
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
    
    
    
    
    
    if region in ("Fog Rift Catacombs", "Belurat Gaol", "Dragon's Pit", "Ruined Forge Lava Intake"):
            return "Gravesite Plain Dungeons"
    
    
    # if nothing return region
    return region

if __name__ == '__main__':
    for region in location_tables:
        region_initals_to_description.setdefault(region, {})
        for location in location_tables[region]:
            initial = location.name[:location.name.find(":")]
            if initial not in region_initals_to_description[region]:
                region_initals_to_description[region][initial] = find_description(initial)
                
    table = "## Base Game\n<table>\n"
    last_region = ""
    for (region, inital_dict) in sorted(
        region_initals_to_description.items(),
        key = lambda pair: location_tables[pair[0]][0].region_value
    ):
        if region == "Roundtable Hold DLC Only":
            table += f"</table><br><div>\n\n## DLC\n\n</div><table>\n"
        if last_region != find_label(region):
            last_region = find_label(region)
            table += f"<tr><td><h3>{html.escape(last_region)}</td></tr>\n"
        for (initial, description) in sorted(
            inital_dict.items(),
            key = lambda pair: pair[0]
        ):
            table += f"<tr><td><strong>{html.escape(initial)}: </strong>{html.escape(description)}</td></tr>\n"
    table += "</table>\n"
    # print(table)

    with open(
        os.path.join(os.path.dirname(__file__), 'en_Elden Ring.md'),
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

    print("Updated docs/en_Elden Ring.md!")
    
    