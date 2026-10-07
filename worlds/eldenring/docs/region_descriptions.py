# python -m worlds.eldenring.docs.region_descriptions

from typing import Dict
import os
import html

from worlds.eldenring.locations import location_tables

# region to inital to description
region_initals_to_description: Dict[str, Dict[str, str]] = {}

def find_description(initial: str) -> str:
    match initial:
        # limgrave
        case "BS": return "Bridge of Sacifice, connection point between South Limgrave and Weeping Peninsula"
        case "LG/(AS)": return "Artists Shack landmark."
        case "": return ""
        case "": return ""
        case "": return ""
        
        case "SV/GG": return "Godrick the Grafted grace in Godrick's arena."
        
        case "": return ""
    
    return ""

if __name__ == '__main__':
    for region in location_tables:
        region_initals_to_description.setdefault(region, {})
        for location in location_tables[region]:
            initial = location.name[:location.name.find(":")]
            if initial not in region_initals_to_description[region]:
                region_initals_to_description[region][initial] = find_description(initial)
                
    table = "## Base Game\n<table>\n"
    for (region, inital_dict) in sorted(
        region_initals_to_description.items(),
        key = lambda pair: location_tables[pair[0]][0].region_value
    ):
        if region == "Roundtable Hold DLC Only":
            table += f"</table><br><div>\n\n## DLC\n\n</div><table>\n"
        table += f"<tr><td><h3>{html.escape(region)}</td></tr>\n"
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
    
    