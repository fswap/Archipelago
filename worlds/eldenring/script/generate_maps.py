from argparse import ArgumentParser
from dataclasses import asdict, dataclass, replace
import json
import os
from typing import Dict, Set, List, Iterable, Optional, Union, Tuple
from PIL import Image, ImageFile
import math
from zipfile import ZipFile, ZIP_DEFLATED

from worlds.eldenring.locations import ERLocationData, location_tables
from worlds.eldenring.region_names import region_order_dlc


@dataclass
class MapGroup:
    name: str
    """The name of the map."""

    regions: List[str] = None
    """Region names to use."""

    override_locations: Optional[List[str]] = None
    """Location names which should be placed in this map and not others.
    These do not need to be present in the region list."""

    underground: bool = False
    """Whether the map is base game underground. Can be inferred but simple
    enough to put here."""

    combine_dungeon: bool = False
    """Whether to put minidungeons in the same map layer as the main map."""

    alt_image_location: Optional[Tuple[str, str, str, str]] = None

    zoom: float = 1.0
    """Scaling factor to use on the map image"""

    node_size: int = 15
    """How big to make the nodes on the map"""

    node_border: int = 4
    """How big to make the border of the nodes on the map"""

    border: int = 100

    def locations(self) -> Iterable[str]:
        return self.override_locations or ()


map_groups: List[MapGroup] = [
    MapGroup("Limgrave", [
        "Limgrave",
        "Stormhill",
        "Coastal Cave",
        "Church of Dragon Communion",
        "Groveside Cave",
        "Stormfoot Catacombs",
        "Limgrave Tunnels",
        "Murkwater Cave",
        "Murkwater Catacombs",
        "Highroad Cave",
        "Deathtouched Catacombs",
        "Fringefolk Hero's Grave",
        "Divine Tower of Limgrave", # accessed from Stormveil
    ], [
        "LG/(BS): Stonesword Key - behind wooden platform",
        "LG/(BS): Smithing Stone [1] x3 - corpse hanging off edge",
    ]),

    # The canonical location is in the middle of the ocean (in-game map overrides this).
    # TODO: It has the same orientation as Fortified Manor in Leyndell so this is a great
    # candidate for a custom image based on that.
    MapGroup("Roundtable Hold", [
        "Roundtable Hold"
    ], alt_image_location=(
        "Roundtable Hold",
        "RH: Sewer-Gaol Key - talk to Dung Eater while having a Seedbed Curse",
        "Leyndell, Royal Capital Unmissable",
        "LRC|LAC/FMFF: Seedbed Curse - second floor in Dung Eaters room, gets moved outside in LAC"
    ), node_size=3, node_border=1),

    MapGroup("Stormveil Castle", [
        "Stormveil Start",
        "Stormveil Castle",
        "Stormveil Throne",
        "The Four Belfries (Chapel of Anticipation)",
    ], node_size=3, node_border=1),

    MapGroup("Weeping Peninsula", [
        "Weeping Peninsula",
        "Impaler's Catacombs",
        "Tombsward Catacombs",
        "Tombsward Cave",
        "Morne Tunnel",
        "Earthbore Cave",
    ], [
        "LG/(BS): Stonesword Key - behind wooden platform",
        "LG/(BS): Smithing Stone [1] x3 - corpse hanging off edge",
    ]),

    MapGroup("Liurnia of The Lakes", [
        "Liurnia of The Lakes",
        "Bellum Highway",
        "Road's End Catacombs",
        "Black Knife Catacombs",
        "Cliffbottom Catacombs",
        "Stillwater Cave",
        "Lakeside Crystal Cave",
        "Academy Crystal Cave",
        "Raya Lucaria Crystal Tunnel",
        "Caria Manor", # only includes after Loretta so can't be split out currently
        "Carian Study Hall",
        "Carian Study Hall (Inverted)",
    ]),

    MapGroup("Raya Lucaria Academy", [
        "Raya Lucaria Academy",
        "Raya Lucaria Academy Main",
        "Raya Lucaria Academy Chest",
        "Raya Lucaria Academy Library",
    ], node_size=5, node_border=2),

    MapGroup("Moonlight Altar", [
        "Moonlight Altar",
    ], node_size=5, node_border=2),

    # Could also include locations outside the precipice in Liurnia for better bounding boxes.
    MapGroup("Ruin-Strewn Precipice", [
        "Ruin-Strewn Precipice",
    ], node_size=5, node_border=2),

    MapGroup("Caelid", [
        "Caelid",
        "Caelid Catacombs",
        "Gaol Cave",
        "Sellia Crystal Tunnel",
        "Abandoned Cave",
        "Minor Erdtree Catacombs",
        "Gael Tunnel",
        "Great-Jar",
        "Redmane Castle Post Radahn",
        "Wailing Dunes",
        "War-Dead Catacombs",
        "Dragonbarrow",
        "Dragonbarrow Cave",
        "Sellia Hideaway",
        "Divine Tower of Caelid",
    ]),

    MapGroup("Siofra", [
        "Siofra River",
        "Nokron, Eternal City Start",
        "Nokron, Eternal City",
        "The Four Belfries (Nokron)",
    ], underground=True, node_size=5, node_border=2),

    MapGroup("Mohgwyn Palace", [
        "Mohgwyn Palace"
    ], underground=True, node_size=3, node_border=1),

    MapGroup("Deeproot Depths", [
        "Deeproot Depths Upper",
        "Deeproot Depths",
        "Deeproot Depths Boss",
    ], underground=True, node_size=5, node_border=2),

    MapGroup("Ainsel River", [
        "Ainsel River",
        "Ainsel River Main",
    ], underground=True, node_size=5, node_border=2),

    MapGroup("Lake of Rot", [
        "Lake of Rot",
    ], underground=True, node_size=5, node_border=2),

    MapGroup("Ainsel River Boss", [], [
        "LR: Remembrance of the Naturalborn - mainboss drop"
    ], underground=True, border=220), # , node_size=5, node_border=2),

    MapGroup("Altus Plateau", [
        "Altus Plateau",
        "Sainted Hero's Grave",
        "Unsightly Catacombs",
        "Perfumer's Grotto",
        "Sage's Cave",
        "Old Altus Tunnel",
        "Altus Tunnel",
        "Wyndham Catacombs",
    ], [
        "AP/SR: Ash of War: Barrage - scarab to N",
        "AP/SR: Arrow x10 - to NE under slanted rock",
    ]),

    MapGroup("Capital Outskirts", [
        "Capital Outskirts",
        "Auriza Hero's Grave",
        "Auriza Side Tomb",
        "Sealed Tunnel",
    ]),

    MapGroup("Mt. Gelmir", [
        "Mt. Gelmir",
        "Gelmir Hero's Grave",
        "Seethewater Cave",
        "Volcano Cave",
    ], [
        "AP/SR: Ash of War: Barrage - scarab to N",
        "AP/SR: Arrow x10 - to NE under slanted rock",
    ], node_size=5, node_border=2),

    MapGroup("Volcano Manor", [
        "Volcano Manor Dungeon",
        "Volcano Manor Entrance",
        "Volcano Manor Drawing Room",
        "Volcano Manor",
        "Volcano Manor Upper",
    ], node_size=5, node_border=2),

    MapGroup("Leyndell, Royal Capital", [
        "Leyndell, Royal Capital",
        "Leyndell, Royal Capital Unmissable",
        "Leyndell, Royal Capital Throne",
        "Divine Bridge",
    ], node_size=3, node_border=1),

    MapGroup("Leyndell, Ashen Capital", [
        "Leyndell, Ashen Capital",
        "Leyndell, Ashen Capital Throne",
        "Erdtree",
        "Leyndell, Royal Capital Unmissable", # also in Royal Capital
        "Divine Bridge", # also in Royal Capital
    ], node_size=3, node_border=1),

    MapGroup("Subterranean Shunning-Grounds", [
        "Subterranean Shunning-Grounds",
        "Leyndell Catacombs",
        "Frenzied Flame Proscription",
    ], combine_dungeon=True, node_size=3, node_border=1),

    MapGroup("Post-Leyndell", [
        "Divine Tower of East Altus",
        "Forbidden Lands",
    ]),

    MapGroup("Mountaintops of the Giants", [
        "Mountaintops of the Giants",
        "Giants' Mountaintop Catacombs",
        "Spiritcaller Cave",
        "Flame Peak",
        "Giant-Conquering Hero's Grave",
    ]),

    MapGroup("Farum Azula", [
        "Farum Azula",
        "Farum Azula Main",
        "The Four Belfries (Farum Azula)",
    ], node_size=5, node_border=2),

    MapGroup("Consecrated Snowfield", [
        "Consecrated Snowfield",
        "Hidden Path to the Haligtree",
        "Consecrated Snowfield Catacombs",
        "Cave of the Forlorn",
        "Yelough Anix Tunnel",
    ]),

    MapGroup("Miquella's Haligtree", [
        "Miquella's Haligtree",
        "Elphael, Brace of the Haligtree",
    ], node_size=5, node_border=2),

    MapGroup("Gravesite Plain", [
        "Gravesite Plain",
        "Fog Rift Catacombs",
        "Belurat Gaol",
        "Dragon's Pit",
        "Ruined Forge Lava Intake",
        # Gravesite Plain bounding box includes Ellac River, so may as well
        "Ellac River",
        "Rivermouth Cave",
    ]),

    MapGroup("Belurat", [
        "Belurat",
        "Belurat Swamp",
    ], [
        # "BTS|EI/SR: Euporia - outside to SE downstairs, drop down from gazebo, after jump to window, continue down and down",
    ], node_size=5, node_border=2),

    MapGroup("Enir-Ilim", [
        "Enir-Ilim",
    ], node_size=5, node_border=2),

    # Jagged Peak is a big area but low check density
    MapGroup("Jagged Peak", [
        "Jagged Peak Foot",
        "Jagged Peak",
    ]),

    MapGroup("Cerulean and Charo", [
        "Cerulean Coast",
        "Finger Ruins of Rhia",
        "Charo's Hidden Grave",
        "Lamenter's Gaol (Entrance)",
        "Lamenter's Gaol (Upper)", #main
        "Lamenter's Gaol (Lower)", #boss
        "Stone Coffin Fissure",
    ]),

    MapGroup("Castle Ensis", [
        "Castle Ensis",
    ], [
        "SA/HC: Shadow Realm Rune [2] - to SW in a spire below warp",
        "SA/HC: Starlight Shards - to SW down in upper area of CE, jump over to SW by statue",
        "SA/HC: Carian Sorcery Sword - in chest to SW down in upper area of CE, back left corner",
        "SA/SAW: Grave Glovewort [8] - to S by grave down below, cross river and head down",
    ], node_size=4, node_border=2),

    MapGroup("Scadu Altus", [
        "Scadu Altus",
        "Fog Rift Fort",
        "Bonny Gaol",
        "Ruined Forge of Starfall Past",
        "Cathedral of Manus Metyr",
        "Finger Ruins of Miyr",
        # Recluses' River could alternately be separate and siloed
        "Recluses' River",
        "Darklight Catacombs",
    ], [
        "SA/HC: Shadow Realm Rune [2] - to SW in a spire below warp",
        "SA/(RR): Spellmachinist's Bell Bearing - very top of rise, drop down from HL/SV",
    ]),

    MapGroup("Rauh Ruins and Base", [
        "Ancient Ruins of Rauh",
        "Rauh Ruins Limited",
        "Rauh Base",
        "Scorpion River Catacombs",
        "Taylew's Ruined Forge",
    ]),

    MapGroup("Shadow Keep", [
        "Shadow Keep",
        "Shadow Keep Storehouse",
        "Shadow Keep Storehouse Back",
        "Shadow Keep, Church District",
        "Shadow Keep, Church District Lower",
    ], node_size=3, node_border=2), # from 5

    MapGroup("Shadow Keep, West Rampart", [
        "Shadow Keep, West Rampart",
    ], node_size=5, node_border=2),

    # Huge area but very low check density
    MapGroup("Scaduview", [
        "Scaduview",
        "Scadutree Base",
        "Hinterland",
        "Finger Ruins of Dheo",
    ], [
        "SK/TWS: Iris of Grace - to S by statue",
        "SK/TWS: Marika's Rune - by grace",
        "ScV/SKBG: Remembrance of the Wild Boar Rider - mainboss drop",
        "SA/(RR): Spellmachinist's Bell Bearing - very top of rise, drop down from HL/SV",
    ]),

    MapGroup("Abyssal Woods", [
        "Abyssal Woods",
        "Midra's Manse",
    ]),
]

others = [
    MapGroup("Shadow Keep", [
        "Shadow Keep",
    ], node_size=5, node_border=2),

    # Good luck
    MapGroup("Shadow Keep Storehouse", [
        "Shadow Keep Storehouse",
        "Shadow Keep Storehouse Back",
    ], node_size=5, node_border=2),

    MapGroup("Shadow Keep, Church District", [
        "Shadow Keep, Church District",
        "Shadow Keep, Church District Lower",
    ], node_size=5, node_border=2),
]


@dataclass
class ImageCoord:
    image: str
    x: int
    y: int

    def dist(self, other: "ImageCoord") -> float:
        return math.dist((self.x, self.y),(other.x, other.y))

    def dist_node(self, other: "Node") -> float:
        coords = [c for c in other.map_locations if c.image == self.image]
        if len(coords) < 1:
            return 9999999999.0 # Big number, not relevent how big
        coords.sort(key=self.dist)
        return coords[0].dist(self)


@dataclass
class MapImage:
    group: MapGroup
    map_name: str
    image_name: str
    base_image: str
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    minidungeon: bool = False

    def contains(self, coord: ImageCoord) -> bool:
        return (self.min_x <= coord.x < self.max_x
                and self.min_y <= coord.y < self.max_y
                and self.base_image == coord.image)

class Node:
    # Name is the key in the holding dict
    sections: list[str] # List of location names (usually only one)
    map_locations: list[ImageCoord] # What map to put the node on : Where to put it

    def __init__(self, sections: Union[str,list[str]], map_locations: Union[ImageCoord,List[ImageCoord]]):
        if isinstance(sections, str):
            sections = [sections]
        if isinstance(map_locations, ImageCoord):
            map_locations = [map_locations]
        self.sections = sections
        self.map_locations = map_locations

def main(map_dir: str):
    with open(os.path.join(map_dir, "coords.json")) as f:
        coords_data = json.load(f)
        key_locations: Dict[str, ImageCoord] = {key: ImageCoord(**coord) for (key, coord) in coords_data.items()}

    output_dir = os.path.join(map_dir,"output")
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    output_zip = os.path.join(map_dir, "output.zip")
    if os.path.exists(output_zip):
        os.remove(output_zip)

    def get_location_coord(location: ERLocationData, offset: Optional[Tuple[int, int]]=None) -> ImageCoord:
        if not location.key:
            raise KeyError(location.name)
        coord = key_locations[location.key]
        if offset is not None:
            coord = replace(coord, x=coord.x + offset[0], y=coord.y + offset[1])
        return coord
    def get_location(region: str, name: str) -> ERLocationData:
        return next(loc for loc in location_tables[region] if loc.name == name)

    dungeon_regions: Set[str] = set(region for (region, locs) in location_tables.items() if any(loc.dungeon for loc in locs))
    dlc_regions: Set[str] = set(region_order_dlc)
    silo_locations: Set[str] = set(loc for group in map_groups for loc in group.locations())
    silo_location_regions: Dict[str, str] = {
        loc.name: region
        for (region, locs) in location_tables.items()
        for loc in locs
        if loc.name in silo_locations
    }
    base_images: Dict[str,ImageFile.ImageFile] = {}
    for group in ("underground", "dlc", "base"):
        base_images[group] = Image.open(os.path.join(map_dir,f"{group}.png"))

    output_locations: dict[str, Node] = {}
    output_maps: List[MapImage] = []

    for group in map_groups:
        regions = frozenset(group.regions)
        extra_regions = frozenset(silo_location_regions[loc] for loc in group.locations())
        def location_included(location: ERLocationData) -> bool:
            if location.region_name not in regions or location.name in silo_locations:
                return location.name in group.locations()
            return True

        offset: Optional[Tuple[int, int]] = None
        if group.alt_image_location is not None:
            (target_region, target_name, source_region, source_name) = group.alt_image_location
            target = get_location_coord(get_location(target_region, target_name))
            source = get_location_coord(get_location(source_region, source_name))
            offset = (source.x - target.x, source.y - target.y)

        base_image = ("underground" if group.underground
                      else ("dlc" if any(region in dlc_regions for region in regions) else "base"))
        group_coords: List[ImageCoord] = []
        has_minidungeon = False
        for region in regions.union(extra_regions):
            if region in dungeon_regions and not group.combine_dungeon:
                has_minidungeon = True
            for location in location_tables[region]:
                if not location_included(location):
                    continue
                coord = get_location_coord(location, offset)
                if coord.image != base_image:
                    raise RuntimeError(f"{location.name} {location.key} in {region} is in {coord.image}, expected {base_image}")
                group_coords.append(coord)
        if not len(group_coords):
            raise RuntimeError(f"No coordinates found in {group.name}")

        # For now each MapGroup corresponds to one image and minidungeons are implemented as a separate layer on that image.
        # Minidungeon custom maps would best be implemented by an image per minidungeon.
        # Splits based on x/y coordinates could be handled with separate MapGroups.
        image_name = f"{group.name}.png"
        full_image = MapImage(
            group=group,
            map_name=group.name,
            image_name=image_name,
            base_image=base_image,
            min_x=min(coord.x for coord in group_coords) - group.border,
            max_x=max(coord.x for coord in group_coords) + group.border,
            min_y=min(coord.y for coord in group_coords) - group.border,
            max_y=max(coord.y for coord in group_coords) + group.border,
        )
        res = base_images[full_image.base_image].crop((full_image.min_x, full_image.min_y, full_image.max_x, full_image.max_y))
        res = res.resize([int(group.zoom * (full_image.max_x-full_image.min_x)), int(group.zoom * (full_image.max_y - full_image.min_y))])
        res.save(os.path.join(output_dir, image_name))
        images = [full_image]
        if has_minidungeon:
            images.append(replace(full_image,
                                  map_name=f"{group.name} Dungeons",
                                  minidungeon=True))
        output_maps.extend(images)

        # Quadratic or cubic or something nbd
        count = 0
        local_nodes: list[Node] = []
        for region, locations in location_tables.items():
            if region not in regions and region not in extra_regions:
                continue
            for location in locations:
                if not location_included(location):
                    continue
                coord = get_location_coord(location, offset)
                for image in images:
                    if (region in dungeon_regions and not group.combine_dungeon) != image.minidungeon:
                        continue
                    if image.contains(coord):
                        map_coord = ImageCoord(image.map_name, int((coord.x - image.min_x) * group.zoom), int((coord.y - image.min_y) * group.zoom))
                        local_nodes.sort(key=map_coord.dist_node)
                        if len(local_nodes) > 0 and map_coord.dist_node(local_nodes[0]) < (group.node_size * 3): # about 2 * sqrt 2 so anything that has any overlap should be merged 
                            local_nodes[0].sections.append(location.name)
                        elif location.name not in output_locations:
                            temp_node = Node(location.name, map_coord)
                            output_locations[location.name] = temp_node
                            local_nodes.append(temp_node)
                        else:
                            output_locations[location.name].map_locations.append(map_coord)
                        count += 1

        print(f"{group.name}: {count} locations")

        # Now to generate the output files

    maps_json = [{
        "img": image.image_name,
        "name": image.map_name,
        "location_size": image.group.node_size,
        "location_border_thickness": image.group.node_border,
    } for image in output_maps]
    # I tried to do this in a cursed comprehension but python wouldn't let me
    locations_json = []
    for node_name, node in output_locations.items():
        temp_node = {"name":node_name, "sections":[], "map_locations":[]} # Pre-make both of these as we're going to need them
        for section in node.sections:
            temp_node["sections"].append({"name":section})
        for m_loc in node.map_locations:
            temp_node["map_locations"].append({"map":m_loc.image, "x":m_loc.x, "y":m_loc.y})
        locations_json.append(temp_node)
    with open(os.path.join(output_dir, "maps.json"), "w") as f:
        json.dump(maps_json, f, indent=2)
    with open(os.path.join(output_dir, "locations.json"), "w") as f:
        json.dump(locations_json, f, indent=2)

    # Deflate can do e.g. 108 MB -> 107 MB
    with ZipFile(output_zip, 'w', ZIP_DEFLATED) as zip:
        for path in os.listdir(output_dir):
            # zip.write(path, os.path.basename(path))
            zip.write(os.path.join(output_dir, path), path)


if __name__ == "__main__":
    # With venv: python -m worlds.eldenring.script.generate_maps --map-dir <dir>
    parser = ArgumentParser(prog="generate_maps")
    parser.add_argument("--map-dir", required=True,
                        help="Path to directory with image files and coords.json")
    args = parser.parse_args()

    main(args.map_dir)
