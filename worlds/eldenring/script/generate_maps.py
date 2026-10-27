from argparse import ArgumentParser
from collections import Counter
from dataclasses import asdict, dataclass, replace
import glob
import hashlib
import json
import os
from typing import Dict, Set, List, Iterable, Optional, Union, Tuple
import math
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageFile

from worlds.eldenring.locations import ERLocationData, location_tables
from worlds.eldenring.region_names import region_order_dlc
from worlds.eldenring.tracker import MapBounds, tracker_zip_has_json


@dataclass
class MapGroup:
    name: str
    """The name of the map."""

    regions: Dict[str, Union[int, List[int]]] = None
    """Region names with locations to add, and play regions for auto-tabbing."""

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

    icon_size: int = 80

    border: int = 100

    def locations(self) -> Iterable[str]:
        return self.override_locations or ()

    def region_names(self) -> Iterable[str]:
        return (region for region in self.regions.keys() if region)


map_groups: List[MapGroup] = [
    MapGroup("Limgrave", {
        "Limgrave": 6100,
        "Stormhill": 6101,
        "Coastal Cave": 3115,
        "Church of Dragon Communion": 6100090,
        "Groveside Cave": 3103,
        "Stormfoot Catacombs": 3002,
        "Limgrave Tunnels": 3201,
        "Murkwater Cave": 3100,
        "Murkwater Catacombs": 3004,
        "Highroad Cave": 3117,
        "Deathtouched Catacombs": 3011,
        "Fringefolk Hero's Grave": 1800,
        "Divine Tower of Limgrave": 3410, # accessed from Stormveil
    }, [
        "LG/(BS): Stonesword Key - behind wooden platform",
        "LG/(BS): Smithing Stone [1] x3 - corpse hanging off edge",
    ], icon_size=120),

    # The canonical location is in the middle of the ocean (in-game map overrides this).
    # TODO: It has the same orientation as Fortified Manor in Leyndell so this is a great
    # candidate for a custom image based on that.
    MapGroup("Roundtable Hold", {
        "Roundtable Hold": 1110,
    }, alt_image_location=(
        "Roundtable Hold",
        "RH: Sewer-Gaol Key - talk to Dung Eater while having a Seedbed Curse",
        "Leyndell, Royal Capital Unmissable",
        "LRC|LAC/FMFF: Seedbed Curse - second floor in Dung Eaters room, gets moved outside in LAC"
    ), node_size=3, node_border=1, icon_size=30),

    MapGroup("Stormveil Castle", {
        "Stormveil Start": 1000,
        "Stormveil Castle": 1000,
        "Stormveil Throne": 1000,
        "The Four Belfries (Chapel of Anticipation)": 1001,
    }, node_size=3, node_border=1, icon_size=60),

    MapGroup("Weeping Peninsula", {
        "Weeping Peninsula": 6102,
        "Impaler's Catacombs": 3001,
        "Tombsward Catacombs": 3000,
        "Tombsward Cave": 3102,
        "Morne Tunnel": 3200,
        "Earthbore Cave": 3101,
    }, [
        "LG/(BS): Stonesword Key - behind wooden platform",
        "LG/(BS): Smithing Stone [1] x3 - corpse hanging off edge",
    ]),

    MapGroup("Siofra", {
        "Siofra River": [1207, 1202, 1208],
        "Nokron, Eternal City Start": [1207, 1202],
        "Nokron, Eternal City": [1202, 1209],
        "The Four Belfries (Nokron)": 1202, # Fake
    }, underground=True, node_size=5, node_border=2),

    MapGroup("Liurnia of The Lakes", {
        "Liurnia of The Lakes": 6200,
        "Bellum Highway": 6201,
        "Road's End Catacombs": 3003,
        "Black Knife Catacombs": 3005,
        "Cliffbottom Catacombs": 3006,
        "Stillwater Cave": 3104,
        "Lakeside Crystal Cave": 3105,
        "Academy Crystal Cave": 3106,
        "Raya Lucaria Crystal Tunnel": 3202,
        "Caria Manor": 6200, # only after Loretta
        "Carian Study Hall": 3411,
        "Carian Study Hall (Inverted)": 3411,
    }, icon_size=160),

    MapGroup("Raya Lucaria Academy", {
        "Raya Lucaria Academy": 1400,
        "Raya Lucaria Academy Main": 1400,
        "Raya Lucaria Academy Chest": 1400,
        "Raya Lucaria Academy Library": 1400,
    }, node_size=5, node_border=2, icon_size=60),

    # Could also include locations outside the precipice in Liurnia for better bounding boxes.
    MapGroup("Ruin-Strewn Precipice", {
        "Ruin-Strewn Precipice": 3920,
    }, node_size=5, node_border=2, icon_size=30),

    MapGroup("Caelid", {
        "Caelid": [6400, 6401],
        "Caelid Catacombs": 3015,
        "Gaol Cave": 3121,
        "Sellia Crystal Tunnel": 3208,
        "Abandoned Cave": 3120,
        "Minor Erdtree Catacombs": 3014,
        "Gael Tunnel": 3207,
        "Great-Jar": 6400,
        "Redmane Castle Post Radahn": 6400,
        "Wailing Dunes": 6400,
        "War-Dead Catacombs": 3016,
        "Dragonbarrow": 6402,
        "Dragonbarrow Cave": 3110,
        "Sellia Hideaway": 3111,
        "Divine Tower of Caelid": 3413,
    }, icon_size=160),

    MapGroup("Deeproot Depths", {
        "Deeproot Depths Upper": 1203,
        "Deeproot Depths": 1203,
        "Deeproot Depths Boss": 1203,
    }, underground=True, node_size=5, node_border=2),

    MapGroup("Ainsel River", {
        "Ainsel River": 1201,
        "Ainsel River Main": 1201,
    }, underground=True, node_size=5, node_border=2),

    MapGroup("Lake of Rot", {
        "Lake of Rot": [1201015, 1201016, 1201017],
    }, underground=True, node_size=5, node_border=2),

    MapGroup("Ainsel River Boss", {
        None: 1204
    }, {
        "LR: Remembrance of the Naturalborn - mainboss drop"
    }, underground=True, border=220, node_size=10, node_border=3, icon_size=60),

    MapGroup("Moonlight Altar", {
        "Moonlight Altar": 6202,
    }, node_size=5, node_border=2),

    MapGroup("Altus Plateau", {
        "Altus Plateau": 6300,
        "Sainted Hero's Grave": 3008,
        "Unsightly Catacombs": 3012,
        "Perfumer's Grotto": 3118,
        "Sage's Cave": 3119,
        "Old Altus Tunnel": 3204,
        "Altus Tunnel": 3205,
        "Wyndham Catacombs": 3007,
    }, [
        "AP/SR: Ash of War: Barrage - scarab to N",
        "AP/SR: Arrow x10 - to NE under slanted rock",
    ], icon_size=120),

    MapGroup("Mt. Gelmir", {
        "Mt. Gelmir": 6302,
        "Gelmir Hero's Grave": 3009,
        "Seethewater Cave": 3107,
        "Volcano Cave": 3109,
    }, [
        "AP/SR: Ash of War: Barrage - scarab to N",
        "AP/SR: Arrow x10 - to NE under slanted rock",
    ], node_size=5, node_border=2),

    MapGroup("Volcano Manor", {
        "Volcano Manor Dungeon": 1600,
        "Volcano Manor Entrance": 1600,
        "Volcano Manor Drawing Room": 1600,
        "Volcano Manor": 1600,
        "Volcano Manor Upper": 1600,
    }, node_size=5, node_border=2, icon_size=30),

    MapGroup("Capital Outskirts", {
        "Capital Outskirts": 6301,
        "Auriza Hero's Grave": 3010,
        "Auriza Side Tomb": 3013,
        "Sealed Tunnel": 3412,
    }, node_size=10, node_border=3),

    MapGroup("Leyndell, Royal Capital", {
        "Leyndell, Royal Capital": 1100,
        "Leyndell, Royal Capital Unmissable": 1100,
        "Leyndell, Royal Capital Throne": 1100,
        "Divine Bridge": 1100,
    }, [
        "DTEA: Flamedrake Talisman +1 - E of leyndell elevator by pillar",
    ], node_size=3, node_border=1, icon_size=60, border=50),

    MapGroup("Subterranean Shunning-Grounds", {
        "Subterranean Shunning-Grounds": 3500,
        "Leyndell Catacombs": 3500,
        "Frenzied Flame Proscription": 3500,
    }, combine_dungeon=True, node_size=3, node_border=1, icon_size=60, border=50),

    MapGroup("Post-Leyndell", {
        "Divine Tower of East Altus": 3414,
        "Forbidden Lands": 6500,
    }, [
        "DTEA: Flamedrake Talisman +1 - E of leyndell elevator by pillar",
    ], node_size=10, node_border=3, border=150),

    MapGroup("Mountaintops of the Giants", {
        "Mountaintops of the Giants": 6501,
        "Giants' Mountaintop Catacombs": 3018,
        "Spiritcaller Cave": 3122,
        "Flame Peak": 6502,
        "Giant-Conquering Hero's Grave": 3017,
    }, icon_size=120),

    MapGroup("Farum Azula", {
        "Farum Azula": 1300,
        "Farum Azula Main": 1300,
        "The Four Belfries (Farum Azula)": 1300,
    }, node_size=5, node_border=2),

    MapGroup("Consecrated Snowfield", {
        "Consecrated Snowfield": 6503,
        "Hidden Path to the Haligtree": 3020,
        "Consecrated Snowfield Catacombs": 3019,
        "Cave of the Forlorn": 3112,
        "Yelough Anix Tunnel": 3211,
    }, icon_size=120),

    MapGroup("Mohgwyn Palace", {
        "Mohgwyn Palace": 1205,
    }, underground=True, node_size=3, node_border=1, icon_size=30),

    MapGroup("Miquella's Haligtree", {
        "Miquella's Haligtree": 1500,
        "Elphael, Brace of the Haligtree": 1500,
    }, node_size=5, node_border=2),

    MapGroup("Leyndell, Ashen Capital", {
        "Leyndell, Ashen Capital": 1105,
        "Leyndell, Ashen Capital Throne": 1105,
        "Erdtree": 1900,
        "Leyndell, Royal Capital Unmissable": 1105, # also in Royal Capital
        "Divine Bridge": 1105, # also in Royal Capital
    }, node_size=5, node_border=2, icon_size=60, border=50),

    MapGroup("Gravesite Plain", {
        "Gravesite Plain": [6800, 6810],
        "Fog Rift Catacombs": 4000,
        "Belurat Gaol": 4100,
        "Dragon's Pit": 4301,
        "Ruined Forge Lava Intake": 4200,
        # Gravesite Plain bounding box includes Ellac River, so may as well
        "Ellac River": 6810,
        "Rivermouth Cave": 4300,
    }, [
        "ER/ERD: Mushroom-Seller's Bell Bearing [2] - hanging pot to SE hanging on rock infront of waterfall",
    ], icon_size=120),

    MapGroup("Belurat", {
        "Belurat": 2000,
        "Belurat Swamp": 2000,
    }, [
        # "BTS|EI/SR: Euporia - outside to SE downstairs, drop down from gazebo, after jump to window, continue down and down",
    ], node_size=5, node_border=2, icon_size=60),

    MapGroup("Cerulean and Charo", {
        "Cerulean Coast": 6830,
        "Finger Ruins of Rhia": 6830,
        "Charo's Hidden Grave": 6840,
        "Lamenter's Gaol (Entrance)": 4102,
        "Lamenter's Gaol (Upper)": 4102,
        "Lamenter's Gaol (Lower)": 4102,
        "Stone Coffin Fissure": 2200,
    }, [
        "ER/ERD: Mushroom-Seller's Bell Bearing [2] - hanging pot to SE hanging on rock infront of waterfall",
        # In Cerulean Coast playregion
        "ER/ERD: Viridian Hidden Tear - furnace golem to SE",
        "ER/ERD: Forager Brood Cookbook [3] - given by friendly Kindred of Rot to SE, NE corner of cliffs",
        "ER/ERD: Yellow Fulgurbloom x3 - given by friendly Kindred of Rot to SE, NE corner of cliffs",
        "ER/ERD: Lightning Perfume Bottle - to SE in lake",
        "ER/ERD: Furnace Visage - furnace golem to SE",
    ], icon_size=120),

    # Jagged Peak is a big area but low check density
    MapGroup("Jagged Peak", {
        "Jagged Peak Foot": 6841,
        "Jagged Peak": 6850,
    }),

    MapGroup("Castle Ensis", {
        "Castle Ensis": 6820,
    }, [
        "SA/HC: Shadow Realm Rune [2] - to SW in a spire below warp",
        "SA/HC: Starlight Shards - to SW down in upper area of CE, jump over to SW by statue",
        "SA/HC: Carian Sorcery Sword - in chest to SW down in upper area of CE, back left corner",
        "SA/SAW: Grave Glovewort [8] - to S by grave down below, cross river and head down",
    ], node_size=4, node_border=2, icon_size=30),

    MapGroup("Scadu Altus", {
        "Scadu Altus": 6900,
        "Fog Rift Fort": 6900,
        "Bonny Gaol": 4101,
        "Ruined Forge of Starfall Past": 4202,
        "Cathedral of Manus Metyr": 6902,
        "Finger Ruins of Miyr": 2500,
        # Recluses' River could alternately be separate and siloed
        "Recluses' River": 6903,
        "Darklight Catacombs": 4002,
    }, [
        "SA/HC: Shadow Realm Rune [2] - to SW in a spire below warp", # Ensis boundary
        "SA/(RR): Spellmachinist's Bell Bearing - very top of rise, drop down from HL/SV", # Rabbath dropdown
        "RR/(DC): Barbed Staff-Spear - boss drop", # Abyssal Woods boundary
    ]),

    MapGroup("Shadow Keep", {
        "Shadow Keep": 2100,
        "Shadow Keep Storehouse": 2101,
        "Shadow Keep Storehouse Back": 2101,
        "Shadow Keep, Church District": 2100,
        "Shadow Keep, Church District Lower": 2100,
    }, node_size=3, node_border=2, icon_size=30), # from 5

    MapGroup("Shadow Keep, West Rampart", {
        "Shadow Keep, West Rampart": 2102,
    }, node_size=5, node_border=2, icon_size=30),

    # Huge area but very low check density
    MapGroup("Scaduview", {
        "Scaduview": [2101010, 2101013, 6920],
        "Scadutree Base": [2100010, 2100015],
        "Hinterland": 6930,
        "Finger Ruins of Dheo": 6930,
    }, [
        "SK/TWS: Iris of Grace - to S by statue",
        "SK/TWS: Marika's Rune - by grace",
        "ScV/SKBG: Remembrance of the Wild Boar Rider - mainboss drop",
        "SA/(RR): Spellmachinist's Bell Bearing - very top of rise, drop down from HL/SV",
    ]),

    MapGroup("Rauh Ruins and Base", {
        "Ancient Ruins of Rauh": [6940, 6941],
        "Rauh Ruins Limited": 6940,
        "Rauh Base": 6901,
        "Scorpion River Catacombs": 4001,
        "Taylew's Ruined Forge": 4203,
    }),

    MapGroup("Abyssal Woods", {
        "Abyssal Woods": 6860,
        "Midra's Manse": 6860,
    }, [
        "RR/(DC): Barbed Staff-Spear - boss drop",
    ], combine_dungeon=True),

    MapGroup("Enir-Ilim", {
        "Enir-Ilim": [2001, 2000011, 2000012],
    }, node_size=5, node_border=2, icon_size=60),
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
    """Display name."""

    image_name: str
    """Image filename (may be shared between maps)."""

    base_name: str
    """Name of the base layer image."""

    min_x: int
    max_x: int
    min_y: int
    max_y: int

    offset: Tuple[int, int]
    """Offsets based on alt map coordinates."""

    play_regions: List[int]
    """Play regions which indicate presence in this map."""

    minidungeon: bool = False
    """Whether this is a minidungeon layer."""

    def contains(self, coord: ImageCoord) -> bool:
        return (self.min_x <= coord.x < self.max_x
                and self.min_y <= coord.y < self.max_y
                and self.base_name == coord.image)


class Node:
    # Name is the key in the holding dict
    sections: list[str] # List of location names (usually only one)
    map_locations: list[ImageCoord] # What map to put the node on : Where to put it

    def __init__(self):
        self.sections = []
        self.map_locations = []


def file_md5(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "md5").hexdigest()


def main(map_dir: str, tracker_dir: str, write_zip: bool):
    with open(os.path.join(map_dir, "coords.json")) as f:
        coords_data = json.load(f)
        key_locations: Dict[str, ImageCoord] = {key: ImageCoord(**coord) for (key, coord) in coords_data.items()}

    output_dir = os.path.join(map_dir, "output")
    output_zip = os.path.join(map_dir, "output.zip")

    if write_zip and os.path.exists(output_zip):
        os.remove(output_zip)

    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    icon = "player.png"
    shutil.copy(os.path.join(map_dir, icon), os.path.join(output_dir, icon))

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
    region_counts = Counter(region for group in map_groups for region in group.region_names())
    silo_locations: Set[str] = set(loc for group in map_groups for loc in group.locations())
    silo_location_regions: Dict[str, str] = {
        loc.name: region
        for (region, locs) in location_tables.items()
        for loc in locs
        if loc.name in silo_locations
    }
    base_image_names = ["base", "underground", "dlc"]  # Index in list is used by client
    base_images: Dict[str,ImageFile.ImageFile] = {}
    for group in base_image_names:
        base_images[group] = Image.open(os.path.join(map_dir, f"{group}.png"))

    output_locations: dict[str, Node] = {}
    output_maps: List[MapImage] = []

    for group in map_groups:
        regions = frozenset(group.region_names())
        extra_regions = frozenset(silo_location_regions[loc] for loc in group.locations())

        def location_included(location: ERLocationData) -> bool:
            if location.region_name not in regions or location.name in silo_locations:
                return location.name in group.locations()
            return True
        def is_dungeon_region(region: str) -> bool:
            return region in dungeon_regions and not group.combine_dungeon
        def get_play_regions(is_dungeon: bool) -> List[int]:
            return list(sorted(set(
                area
                for (region, areas)
                in group.regions.items()
                if is_dungeon_region(region) == is_dungeon
                for area in ((areas,) if isinstance(areas, int) else areas)
            )))

        offset: Optional[Tuple[int, int]] = None
        if group.alt_image_location is not None:
            (target_region, target_name, source_region, source_name) = group.alt_image_location
            target = get_location_coord(get_location(target_region, target_name))
            source = get_location_coord(get_location(source_region, source_name))
            offset = (source.x - target.x, source.y - target.y)

        base_name = ("underground" if group.underground
                      else ("dlc" if any(region in dlc_regions for region in regions) else "base"))
        group_coords: List[ImageCoord] = []
        has_minidungeon = False
        for region in regions.union(extra_regions):
            if is_dungeon_region(region):
                has_minidungeon = True
            for location in location_tables[region]:
                if not location_included(location):
                    continue
                coord = get_location_coord(location, offset)
                if coord.image != base_name:
                    raise RuntimeError(f"{location.name} {location.key} in {region} is in {coord.image}, expected {base_name}")
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
            base_name=base_name,
            min_x=min(coord.x for coord in group_coords) - group.border,
            max_x=max(coord.x for coord in group_coords) + group.border,
            min_y=min(coord.y for coord in group_coords) - group.border,
            max_y=max(coord.y for coord in group_coords) + group.border,
            offset=offset or (0, 0),
            play_regions=get_play_regions(False),
        )
        if write_zip:
            res = base_images[full_image.base_name].crop((full_image.min_x, full_image.min_y, full_image.max_x, full_image.max_y))
            res = res.resize([int(group.zoom * (full_image.max_x-full_image.min_x)), int(group.zoom * (full_image.max_y - full_image.min_y))])
            res.save(os.path.join(output_dir, image_name))
        images = [full_image]
        if has_minidungeon:
            images.append(replace(full_image,
                                  map_name=f"{group.name} Dungeons",
                                  play_regions=get_play_regions(True),
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
                    if is_dungeon_region(region) != image.minidungeon:
                        continue
                    if image.contains(coord):
                        shared = location.name in silo_locations or region_counts[region] > 1
                        # Avoid grouping locations which are shared across maps
                        location_key = location.name + (f" - {image.map_name}" if shared else "")
                        map_coord = ImageCoord(image.map_name, int((coord.x - image.min_x) * group.zoom), int((coord.y - image.min_y) * group.zoom))
                        local_nodes.sort(key=map_coord.dist_node)
                        # about 2 * sqrt 2 so anything that has any overlap should be merged 
                        if len(local_nodes) > 0 and map_coord.dist_node(local_nodes[0]) < (group.node_size * 3):
                            local_nodes[0].sections.append(location.name)
                        elif location_key not in output_locations:
                            node = Node()
                            node.sections.append(location.name)
                            node.map_locations.append(map_coord)
                            output_locations[location_key] = node
                            local_nodes.append(node)
                        else:
                            output_locations[location_key].map_locations.append(map_coord)
                        count += 1

        print(f"{group.name}: {count} locations")

        # Now to generate the output files

    maps_json = [{
        "img": image.image_name,
        "name": image.map_name,
        "location_size": image.group.node_size,
        "location_icon_size": image.group.icon_size,
        "location_border_thickness": image.group.node_border,
    } for image in output_maps]
    output_bounds = [MapBounds(
        name=image.map_name,
        regions=image.play_regions,
        layer=base_image_names.index(image.base_name),
        layer_height=base_images[image.base_name].height,
        min_x=image.min_x - image.offset[0],
        max_x=image.max_x - image.offset[0],
        min_y=image.min_y - image.offset[1],
        max_y=image.max_y - image.offset[1],
    ) for (index, image) in enumerate(output_maps)]
    # I tried to do this in a cursed comprehension but python wouldn't let me
    locations_json = []
    for node_name, node in output_locations.items():
        node_json = {"name": node_name, "sections": [], "map_locations": []} # Pre-make both of these as we're going to need them
        for section in node.sections:
            node_json["sections"].append({"name": section})
        for m_loc in node.map_locations:
            node_json["map_locations"].append({"map": m_loc.image, "x": m_loc.x, "y": m_loc.y})
        locations_json.append(node_json)

    data_dir = output_dir if tracker_zip_has_json else tracker_dir
    with open(os.path.join(data_dir, "maps.json"), "w") as f:
        json.dump(maps_json, f, indent=2)
    with open(os.path.join(data_dir, "locations.json"), "w") as f:
        json.dump(locations_json, f, indent=2)
    with open(os.path.join(tracker_dir, "bounds.json"), "w") as f:
        json.dump([asdict(bounds) for bounds in output_bounds], f, indent=2)

    # Deflate saves like 1 MB file size
    if write_zip:
        with ZipFile(output_zip, "w", ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(output_dir):
                relroot = os.path.relpath(root, output_dir)
                for file in files:
                    relpath = os.path.join(relroot, file)
                    diskpath = os.path.join(output_dir, relpath)
                    zip.write(diskpath, relpath)
            # Try to make zip deterministic for hash
            # This doesn't actually work, though
            for info in zip.infolist():
                info.date_time = (2022, 2, 25, 0, 0, 0)

        if not tracker_zip_has_json:
            hash = file_md5(output_zip)
            hash_name = f"ERMaps_{hash[0:8]}.zip"
            print(f"MD5 hash: {hash} -> {hash_name}")
            os.rename(output_zip, os.path.join(map_dir, hash_name))


if __name__ == "__main__":
    # With venv: python -m worlds.eldenring.script.generate_maps --map-dir <dir>
    parser = ArgumentParser(prog="generate_maps")
    parser.add_argument("--map-dir", required=True,
                        help="Path to directory with image files and coords.json")
    parser.add_argument("--write-zip", action="store_true",
                        help="Output zip file, whose MD5 hash must be added to zip_md5s")
    args = parser.parse_args()

    tracker_dir = "worlds/eldenring/tracker/"
    if not os.path.exists(tracker_dir):
        raise RuntimeError(f"Directory does not exist: {tracker_dir}")

    main(args.map_dir, tracker_dir, args.write_zip)
