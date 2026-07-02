from dataclasses import dataclass
from typing import ClassVar, cast

from BaseClasses import ItemClassification, Location, Region

from .Items import SekiroItemCategory, item_dictionary

@dataclass
class SekiroLocationData:
    __location_id: ClassVar[int] = 1
    """The next location ID to use when creating location data."""

    name: str
    """The name of this location according to Archipelago.

    This needs to be unique within this world."""

    default_item_name: str | None
    """The name of the item that appears by default in this location.

    If this is None, that indicates that this location is an "event" that's
    automatically considered accessed as soon as it's available. Events are used
    to indicate major game transitions that aren't otherwise gated by items so
    that progression balancing and item smoothing is more accurate for Sekiro.
    """

    ap_code: int | None = None
    """Archipelago's internal ID for this location (also known as its "address")."""

    region_value: int = 0
    """The relative value of items in this location's region.

    This is used to sort locations when placing items like the base game.
    """

    static: str | None = None
    """The key in the static randomizer's Slots table that corresponds to this location.

    By default, the static randomizer chooses its location based on the region and the item name.
    If the item name is unique across the whole game, it can also look it up based on that alone. If
    there are multiple instances of the same item type in the same region, it will assume its order
    (in annotations.txt) matches Archipelago's order.

    In cases where this heuristic doesn't work, such as when Archipelago's region categorization or
    item name disagrees with the static randomizer's, this field is used to provide an explicit
    association instead.
    """

    missable: bool = False
    """Whether this item is possible to permanently lose access to.

    Missable locations are always marked as excluded, so they will never contain
    progression or useful items.
    """

    npc: bool = False
    """Whether this item is contingent on following an NPC's quest."""

    prominent: bool = False
    """Whether this is one of few particularly prominent places for items to appear.

    This is a small number of locations (boss drops and progression locations)
    intended to be set as priority locations for players who don't want a lot of
    mandatory checks.

    For bosses with multiple drops, only one should be marked prominent.
    """

    progression: bool = False
    """Whether this location normally contains an item that blocks forward progress."""

    boss: bool = False
    """Whether this location is a reward for defeating a full boss."""

    miniboss: bool = False
    """Whether this location is a reward for defeating a miniboss.
    
    Minibosses are enemies with unique health bars that do not drop memories.
    """

    prosthetic: bool = False
    """Whether this location normally contains a prosthetic tool item."""

    drop: bool = False
    """Whether this is an item dropped by a (non-boss) enemy.

    This is automatically set to True if miniboss or carp is True.
    """

    shop: bool = False
    """Whether this location can appear in an NPC's shop."""

    conditional: bool = False
    """Whether this location is conditional on a progression item.

    This is used to track locations that won't become available until an unknown amount of time into
    the run, and as such shouldn't have "similar to the base game" items placed in them.
    """

    hidden: bool = False
    """Whether this location is particularly tricky to find.

    This is for players without an encyclopedic knowledge of Sekiro who don't want to get stuck looking
    for some out of the way hidden item.
    """

    headless: bool = False
    """Whether this location is dropped by a headless miniboss."""

    carp: bool = False
    """Whether this location is dropped by a Treasure Carp."""

    offering_box: bool = False
    """Whether this is an item that moves to the Offering Box after becoming unavailable.

    This is used to track items that could contain some important item that cannot be missed.
    Once the opportunity to acquire the item has passed, it will be placed in the Offering Box.    
    """

    diving: bool = False
    """Whether this location is only accessible via Mibu Breathing Technique
    
    This is used to track locations that are conditional on this progression item specifically,
    and warrant their own rule due to the amount of them.
    """

    @property
    def is_event(self) -> bool:
        """Whether this location represents an event rather than a specific item pickup."""
        return self.default_item_name is None

    def __post_init__(self):
        if not self.is_event:
            self.ap_code = self.ap_code or SekiroLocationData.__location_id
            SekiroLocationData.__location_id += 1
        if self.miniboss or self.carp: self.drop = True

    def location_groups(self) -> list[str]:
        """The names of location groups this location should appear in.

        This is computed from the properties assigned to this location."""
        names = []
        if self.prominent: names.append("Prominent")
        if self.progression: names.append("Progression")
        if self.boss: names.append("Boss Rewards")
        if self.miniboss: names.append("Miniboss Rewards")
        if self.headless: names.append("Headless")
        if self.drop: names.append("Drops")
        if self.npc: names.append("Friendly")
        if self.prosthetic: names.append("Prosthetics")
        if self.hidden: names.append("Hidden")
        if self.offering_box: names.append("Offering Box")

        default_item = item_dictionary[cast(str, self.default_item_name)]
        names.append({
                         SekiroItemCategory.ESOTERIC_TEXTS: "Esoteric Texts",
                         SekiroItemCategory.SKILLS: "Skills",
                         SekiroItemCategory.MISC: "Miscellaneous",
                         SekiroItemCategory.PRAYER_BEADS: "Prayer Beads",
                         SekiroItemCategory.UNIQUE: "Unique",
                         SekiroItemCategory.MEMORIES: "Memories",
                         SekiroItemCategory.CURRENCY: "Currency",
                         SekiroItemCategory.UPGRADE: "Upgrade",
                         SekiroItemCategory.GOURD_SEEDS: "Gourd Seeds",
                     }[default_item.category])
        if default_item.classification == ItemClassification.progression:
            names.append("Progression")

        return names


class SekiroLocation(Location):
    game: str = "Sekiro: Shadows Die Twice"
    data: SekiroLocationData

    def __init__(
            self,
            player: int,
            data: SekiroLocationData,
            parent: Region | None = None,
            event: bool = False):
        super().__init__(player, data.name, None if event else data.ap_code, parent)
        self.data = data


# Naming conventions:
#
# https://gist.github.com/nex3/5bfbc00cc272c80cdb94d292f2aa87ee
location_tables: dict[str, list[SekiroLocationData]] = {
    "Tutorial": [
        # This is all flagged missable due to only being accessible again upon reaching Ashina Reservoir
        SekiroLocationData("T: Pellet - miniboss drop", "Pellet", static="01,0:51112920::", miniboss=True,
                           missable=True),
        SekiroLocationData("T: Ornamental Letter - starting well", "Ornamental Letter", missable=True),
        SekiroLocationData("T: Pellet - moon-view tower, upper floor", "Pellet", static="01,0:51120040::",
                           missable=True),
        SekiroLocationData("T: Pellet - ledge under bridge", "Pellet", static="01,0:51120140::", missable=True),
        SekiroLocationData("T: Fistful of Ash - ledge after miniboss", "Fistful of Ash x2", missable=True),
    ],
    "Dilapidated Temple": [
        SekiroLocationData("DT: Gourd Seed - Fujioka the Info Broker", "Gourd Seed", shop=True, conditional=True),
        SekiroLocationData("DT: Sabimaru Memo - Fujioka the Info Broker", "Sabimaru Memo", shop=True, conditional=True),
        SekiroLocationData("DT: Three-story Pagoda Memo - Fujioka the Info Broker", "Three-story Pagoda Memo",
                           shop=True, conditional=True),
        SekiroLocationData("DT: Valley Apparitions Memo - Fujioka after boss killed in Guardian Ape's Burrow",
                           "Valley Apparitions Memo", shop=True, conditional=True),
        SekiroLocationData("DT: Shinobi Prosthetic - complete Tutorial", "Shinobi Prosthetic", progression=True),
        # Technically missable due to it being a pickup, not an auto drop. If you reload, it despawns.
        SekiroLocationData("DT: Hidden Tooth - complete Hanbei's quest", "Hidden Tooth", npc=True, conditional=True,
                           missable=True),
        SekiroLocationData("DT: Pellet - next to idol", "Pellet x2"),
        SekiroLocationData("DT: Light Coin Purse - behind DT", "Light Coin Purse"),
        SekiroLocationData("DT: Shinobi Esoteric Text - talk to Sculptor with 1 skill point", "Shinobi Esoteric Text",
                           npc=True, conditional=True),
        SekiroLocationData("DT: Prosthetic Esoteric Text - talk to Sculptor with 3 prosthetic tools",
                           "Prosthetic Esoteric Text", npc=True, conditional=True),
        # Missable as some people may be too good to ever trigger this. Also second invasion removes it.
        SekiroLocationData("DT: Ashina Sake - Emma after healing Sculptor's dragonrot", "Ashina Sake", missable=True,
                           npc=True, conditional=True),
    ],
    "Ashina Outskirts": [
        SekiroLocationData("AO: Robert's Firecrackers - Crow's Bed & Battlefield Memorial Mob",
                           "Robert's Firecrackers", prosthetic=True, shop=True),
        SekiroLocationData("AO: Gourd Seed - Battlefield Memorial Mob", "Gourd Seed", static="00,0:-1:1100100:",
                           shop=True),
        SekiroLocationData("AO: Phantom Kunai - Anayama the Peddler", "Phantom Kunai", shop=True, offering_box=True),
        SekiroLocationData("AO: Memory: Gyoubu Oniwa", "Memory: Gyoubu Oniwa", boss=True),
        # Technically missable due to it being a pickup if not collected until second invasion. Despawns on reload.
        # (not missable in Shura)
        SekiroLocationData("AO: Young Lord's Bell Charm - Inosuke's Mother", "Young Lord's Bell Charm", missable=True,
                           npc=True, progression=True),
        SekiroLocationData("AO: Flame Barrel Memo - Anayama", "Flame Barrel Memo", missable=True, npc=True),
        # Missable if the player does not have Flame Barrel on first encounter.
        SekiroLocationData("AO: Oil - Anayama with Flame Barrel", "Oil x2", missable=True, npc=True, conditional=True),
        SekiroLocationData("AO: Rat Description - agree to help Tengu", "Rat Description", npc=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Snap Seed - near palanquin in Underbridge Valley", "Snap Seed x5", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Pellet - left on lower path at area start", "Pellet", static="00,0:51100040::",
                           missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ungo's Sugar - broken wall above Ashina Outskirts idol", "Ungo's Sugar",
                           static="00,0:51100050::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ceramic Shard - under branch on lower path at area start", "Ceramic Shard",
                           static="00,0:51100060::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ungo's Sugar - gate house before tall grass", "Ungo's Sugar x2",
                           static="00,0:51100070::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ceramic Shard - right cliff from Outskirts idol, near broken wall", "Ceramic Shard x2",
                           static="00,0:51100080::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Fistful of Ash - cliff courtyard, broken hut", "Fistful of Ash x2",
                           static="00,0:51100090::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Pellet - left above wide gate house", "Pellet x3", static="00,0:51100100::",
                           missable=True),
        SekiroLocationData("AO: Ceramic Shard - destroyed house, second floor", "Ceramic Shard x3",
                           static="00,0:51100110::"),
        SekiroLocationData("AO: Mibu Balloon of Wealth - destroyed house, first floor", "Mibu Balloon of Wealth"),
        SekiroLocationData("AO: Gachiin's Sugar - below cave beneath wide gate house", "Gachiin's Sugar x3"),
        SekiroLocationData("AO: Light Coin Purse - room under Inosuke's Mother #1", "Light Coin Purse",
                           static="00,0:51100140::"),
        SekiroLocationData("AO: Light Coin Purse - room under Inosuke's Mother #2", "Light Coin Purse",
                           static="00,0:51100150::"),
        SekiroLocationData("AO: Light Coin Purse - room under Inosuke's Mother #3", "Light Coin Purse",
                           static="00,0:51100160::"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Fistful of Ash - right of gate leading to Gate Path idol", "Fistful of Ash",
                           static="00,0:51100170::", missable=True),
        SekiroLocationData("AO: Pellet - up stairs, before lookout building miniboss", "Pellet",
                           static="00,0:51100180::"),
        SekiroLocationData("AO: Mibu Balloon of Wealth - left of miniboss before lookout building",
                           "Mibu Balloon of Wealth"),
        SekiroLocationData("AO: Ceramic Shard - lookout building, left room", "Ceramic Shard x2",
                           static="00,0:51100210::"),
        SekiroLocationData("AO: Gachiin's Sugar - house with headless cave shortcut", "Gachiin's Sugar x2"),
        SekiroLocationData("AO: Antidote Powder - lookout building, right room", "Antidote Powder"),
        SekiroLocationData("AO: Divine Grass - lookout building, right room", "Divine Grass"),
        SekiroLocationData("AO: Pellet - just before Underbridge Valley idol", "Pellet x2", static="00,0:51100250::"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ungo's Sugar - fortress, behind house", "Ungo's Sugar", static="00,0:51100260::",
                           missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Heavy Coin Purse - fortress, courtyard house bottom floor", "Heavy Coin Purse",
                           missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Fistful of Ash - fortress, near dead horse", "Fistful of Ash x2",
                           static="00,0:51100280::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Pellet - fortress, near doors opened from other side", "Pellet x2",
                           static="00,0:51100290::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ako's Sugar - fortress, along left outer wall from idol", "Ako's Sugar", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Fistful of Ash - boss arena", "Fistful of Ash x2", static="00,0:51100320::",
                           missable=True),
        SekiroLocationData("AO: Nightjar Monocular - lookout building, grapple entrance", "Nightjar Monocular"),
        SekiroLocationData("AO: Scrap Iron - courtyard after lookout building", "Scrap Iron"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Bundled Jizo Statue - cave beneath wide gate house", "Bundled Jizo Statue",
                           hidden=True, missable=True),
        SekiroLocationData("AO: Light Coin Purse - destroyed house, roof", "Light Coin Purse",
                           static="00,0:51100360::"),
        SekiroLocationData("AO: Pellet - behind cliffside gate", "Pellet x2", static="00,0:51100370::"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ako's Sugar - right cliff from Outskirts idol, wall cave", "Ako's Sugar", hidden=True,
                           missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Pellet - left of gate to Gate Path idol", "Pellet", static="00,0:51100390::",
                           missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ceramic Shard - left of Gate Path idol", "Ceramic Shard x2", static="00,0:51100400::",
                           missable=True),
        SekiroLocationData("AO: Scrap Iron - secluded platforms, after snake skin", "Scrap Iron"),
        SekiroLocationData("AO: Mibu Possession Balloon - secluded platforms, before snake skin #1",
                           "Mibu Possession Balloon"),
        SekiroLocationData("AO: Mibu Possession Balloon - secluded platforms, before snake skin #2",
                           "Mibu Possession Balloon"),
        SekiroLocationData("AO: Gachiin's Sugar - after shimmy on way to headless cave", "Gachiin's Sugar x2"),
        SekiroLocationData("AO: Divine Confetti - slope before headless warning sign", "Divine Confetti"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Gachiin's Sugar - fortress, left of idol", "Gachiin's Sugar", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Ceramic Shard - fortress, courtyard outside house", "Ceramic Shard",
                           static="00,0:51100480::", missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Mibu Balloon of Wealth - fortress, courtyard house bottom floor",
                           "Mibu Balloon of Wealth x3", missable=True),
        SekiroLocationData("AO: Ceramic Shard - before stairs next to Tengu Tower", "Ceramic Shard",
                           static="00,0:51100500::"),
        SekiroLocationData("AO: Light Coin Purse - Tengu Tower, second floor", "Light Coin Purse",
                           static="00,0:51100510::"),
        SekiroLocationData("AO: Pellet - Tengu Tower, bottom floor", "Pellet x2", static="00,0:51100520::"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Herb Catalogue Scrap - fortress, near idol, enemy drop", "Herb Catalogue Scrap",
                           drop=True, missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AO: Black Gunpowder - right cobblestone platform, enemy drop", "Black Gunpowder",
                           drop=True, missable=True),
        SekiroLocationData("AO: Ako's Spiritfall - headless cave, miniboss drop", "Ako's Spiritfall",
                           miniboss=True, headless=True),
        SekiroLocationData("AO: Shuriken Wheel - wide gate house, second floor", "Shuriken Wheel", prosthetic=True,
                           offering_box=True),
        SekiroLocationData("AO: Shinobi Medicine Rank 1 - before lookout building, miniboss drop",
                           "Shinobi Medicine Rank 1", miniboss=True),
        SekiroLocationData("AO: Gourd Seed - cliff courtyard, miniboss drop", "Gourd Seed",
                           static="00,0:6723:9025,1100500:", miniboss=True, offering_box=True),
        SekiroLocationData("AO: Gourd Seed - lookout building, left room", "Gourd Seed", static="00,0:6725::"),
        SekiroLocationData("AO: Mechanical Barrel - boss arena, boss drop", "Mechanical Barrel", prominent=True,
                           boss=True),
        SekiroLocationData("AO: Prayer Bead - cliff courtyard, miniboss drop", "Prayer Bead",
                           static="00,0:6760:9027,1100500:", miniboss=True, offering_box=True),
        SekiroLocationData("AO: Prayer Bead - before lookout building, miniboss drop", "Prayer Bead",
                           static="00,0:6761::", miniboss=True),
        SekiroLocationData("AO: Prayer Bead - courtyard after lookout building, miniboss drop", "Prayer Bead",
                           static="00,0:6762:9028,1100500:", miniboss=True, offering_box=True),
        SekiroLocationData("AO: Prayer Bead - Tengu Tower, top floor chest", "Prayer Bead", static="00,0:6788::"),
        # Missable in Shura if the player refuses the quest. Otherwise, can be picked up after reaching AC/C
        SekiroLocationData("AO: Ashina Esoteric Text - Tengu after killing rats", "Ashina Esoteric Text", missable=True,
                           npc=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Pellet - tree near Tengu rat quest enemy", "Pellet x2", static="02,0:51110090::",
                           missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Fistful of Ash - castle gate courtyard, corner house at tree", "Fistful of Ash x2",
                           static="02,0:51110100::", missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Ako's Sugar - castle gate courtyard, cliffside, behind wall", "Ako's Sugar x2",
                           static="02,0:51110260::", hidden=True, missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Light Coin Purse - building in castle gate courtyard, top floor", "Light Coin Purse",
                           static="02,0:51110270::", missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Ceramic Shard - base of stairs after Ashina Castle Gate idol", "Ceramic Shard",
                           static="02,0:51110290::", missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Scrap Iron - castle gate courtyard, hidden behind corner house", "Scrap Iron",
                           missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Scrap Iron - stone near Ashina Castle entrance walls", "Scrap Iron", missable=True),
        # Generally missable after the first invasion (unless skip, but we do not assume that)
        SekiroLocationData("AO: Gachiin's Sugar - tree near Ashina Castle entrance walls", "Gachiin's Sugar x2",
                           missable=True),
        # Missable due to first invasion removing this enemy.
        SekiroLocationData("AO: Black Gunpowder - Tengu rat quest, enemy drop", "Black Gunpowder", drop=True,
                           missable=True),
        SekiroLocationData("AO: Shinobi Medicine Rank 2 - Ashina Castle entrance, miniboss drop",
                           "Shinobi Medicine Rank 2", miniboss=True),
        SekiroLocationData("AO: Prayer Bead - Ashina Castle entrance, miniboss drop", "Prayer Bead",
                           static="02,0:6765::", miniboss=True),
    ],
    "Hirata Estate (Young Lord's Bell Charm)": [
        SekiroLocationData("HE1: Floating Passage Text - Pot Noble Harunaga", "Floating Passage Text", shop=True,
                           conditional=True),
        SekiroLocationData("HE1: Divine Grass - Pot Noble Harunaga", "Divine Grass", shop=True),
        SekiroLocationData("HE1: Withered Red Gourd - Pot Noble Harunaga", "Withered Red Gourd", shop=True),
        SekiroLocationData("HE1: Mask Fragment: Right - Pot Noble Harunaga", "Mask Fragment: Right", shop=True,
                           conditional=True),
        SekiroLocationData("HE1: Memory: Lady Butterfly", "Memory: Lady Butterfly", boss=True, conditional=True),
        # Removed as soon as one enters Hirata 2
        SekiroLocationData("HE1: Hidden Temple Key - Owl", "Hidden Temple Key", npc=True, progression=True,
                           missable=True),
        # Removed as soon as one enters Hirata 2
        SekiroLocationData("HE1: Snap Seed - Audience Chamber, Inosuke", "Snap Seed", conditional=True, missable=True),
        # Removed as soon as one enters Hirata 2
        SekiroLocationData("HE1: Antidote Powder - Estate Path shortcut, second right courtyard, NPC",
                           "Antidote Powder x2", npc=True, missable=True),
        # Missable for now as location may not work if the item is already given to the Great Carp. Remove in Shura!
        SekiroLocationData("HE1: Truly Precious Bait - Pot Noble Harunaga after trading 6 scales",
                           "Truly Precious Bait (Harunaga)", static="03,0:50006360::", npc=True, missable=True,
                           conditional=True),
        # Missable if Pot Noble Harunaga's bait is not fed to Great Carp. Remove in Shura!
        SekiroLocationData("HE1: Lapis Lazuli - Pot Noble Harunaga after Truly Precious Bait", "Lapis Lazuli",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("HE1: Pellet - behind start", "Pellet x2"),
        SekiroLocationData("HE1: Dousing Powder - before first bridge", "Dousing Powder x2"),
        SekiroLocationData("HE1: Mibu Possession Balloon - boat near Pot Noble Harunaga", "Mibu Possession Balloon"),
        SekiroLocationData("HE1: Light Coin Purse - by Pot Noble Harunaga", "Light Coin Purse"),
        SekiroLocationData("HE1: Ungo's Sugar - left of Estate Path, over wall", "Ungo's Sugar x3"),
        SekiroLocationData("HE1: Ako's Sugar - Estate Path, first compound, along right wall", "Ako's Sugar"),
        SekiroLocationData("HE1: Pellet - Estate Path, first compound, largest house", "Pellet x2"),
        SekiroLocationData("HE1: Ceramic Shard - bonfire houses, base of tree", "Ceramic Shard x3"),
        SekiroLocationData("HE1: Fistful of Ash - Estate Path, before shortcut door", "Fistful of Ash x3",
                           static="03,0:51000110::"),
        SekiroLocationData("HE1: Fistful of Ash - tree near bonfire", "Fistful of Ash", static="03,0:51000120::"),
        SekiroLocationData("HE1: Pellet - Estate Path shortcut, first left compound, well", "Pellet"),
        SekiroLocationData("HE1: Light Coin Purse - Estate Path shortcut, first right courtyard, house",
                           "Light Coin Purse"),
        SekiroLocationData("HE1: Ungo's Sugar - Estate Path shortcut, first left courtyard, house", "Ungo's Sugar x3"),
        SekiroLocationData("HE1: Oil - before Bamboo Thicket Slope bridge", "Oil"),
        SekiroLocationData("HE1: Mibu Possession Balloon - side path before cave, crouch opening",
                           "Mibu Possession Balloon", conditional=True, hidden=True),
        SekiroLocationData("HE1: Dousing Powder - Bamboo Thicket Slope, grapple from first ledge",
                           "Dousing Powder x2", conditional=True),
        SekiroLocationData("HE1: Dousing Powder - Main Hall, large building before marsh", "Dousing Powder",
                           conditional=True),
        SekiroLocationData("HE1: Divine Confetti - Main Hall, large building before marsh", "Divine Confetti x2",
                           conditional=True),
        SekiroLocationData("HE1: Light Coin Purse - Main Hall, left building after marsh", "Light Coin Purse",
                           conditional=True),
        SekiroLocationData("HE1: Dousing Powder - Audience Chamber, left room", "Dousing Powder x2", conditional=True),
        SekiroLocationData("HE1: Pellet - Audience Chamber, left room", "Pellet x2", conditional=True),
        SekiroLocationData("HE1: Light Coin Purse - Estate Path shortcut, first left courtyard, roof",
                           "Light Coin Purse"),
        SekiroLocationData("HE1: Pellet - bonfire", "Pellet x2"),
        SekiroLocationData("HE1: Fistful of Ash - before first bridge, dying Nightjar", "Fistful of Ash x2",
                           static="03,0:51000260::"),
        SekiroLocationData("HE1: Ceramic Shard - Main Hall, island in the marsh", "Ceramic Shard", conditional=True),
        SekiroLocationData("HE1: Treasure Carp Scale - behind rock before first bridge", "Treasure Carp Scale"),
        SekiroLocationData("HE1: Ceramic Shard - Estate Path, beside idol", "Ceramic Shard x2"),
        SekiroLocationData("HE1: Mibu Balloon of Wealth - bonfire", "Mibu Balloon of Wealth"),
        SekiroLocationData("HE1: Dousing Powder - bonfire", "Dousing Powder"),
        SekiroLocationData("HE1: Gokan's Sugar - Estate Path shortcut, gate", "Gokan's Sugar"),
        SekiroLocationData("HE1: Mibu Balloon of Soul - side path before cave", "Mibu Balloon of Soul",
                           conditional=True),
        SekiroLocationData("HE1: Bundled Jizo Statue - bamboo path behind Anayama", "Bundled Jizo Statue"),
        SekiroLocationData("HE1: Pellet - right of gate to Bamboo Thicket Slope idol", "Pellet x2"),
        SekiroLocationData("HE1: Mibu Possession Balloon - left of gate to Bamboo Thicket Slope idol",
                           "Mibu Possession Balloon"),
        SekiroLocationData("HE1: Fistful of Ash - after Bamboo Thicket Slope bridge", "Fistful of Ash",
                           static="03,0:51000380::"),
        SekiroLocationData("HE1: Contact Medicine - by tunnel to three-story pagoda", "Contact Medicine",
                           conditional=True),
        SekiroLocationData("HE1: Pellet - side path before cave", "Pellet x2", conditional=True),
        SekiroLocationData("HE1: Oil - Main Hall, between well and idol", "Oil x2", conditional=True),
        SekiroLocationData("HE1: Oil - Audience Chamber, left hallway before shinobi door", "Oil", conditional=True),
        SekiroLocationData("HE1: Divine Confetti - Audience Chamber, shinobi door", "Divine Confetti x2",
                           conditional=True),
        SekiroLocationData("HE1: Light Coin Purse - Audience Chamber, shinobi door", "Light Coin Purse",
                           conditional=True),
        SekiroLocationData("HE1: Mibu Balloon of Wealth - Audience Chamber, shinobi door",
                           "Mibu Balloon of Wealth", conditional=True),
        SekiroLocationData("HE1: Mibu Balloon of Soul - Audience Chamber, room left of idol", "Mibu Balloon of Soul",
                           conditional=True),
        # Does not drop from Juzou in Hirata 2, therefore missable if skipped here
        SekiroLocationData("HE1: Unrefined Sake - Main Hall, miniboss drop", "Unrefined Sake", miniboss=True,
                           missable=True, conditional=True),
        SekiroLocationData("HE1: Bulging Coin Purse - side path before cave, enemy drop", "Bulging Coin Purse",
                           drop=True, conditional=True),
        SekiroLocationData("HE1: Scrap Iron - three-story pagoda, enemy drop", "Scrap Iron", drop=True,
                           conditional=True),
        SekiroLocationData("HE1: Treasure Carp Scale - near first bridge, Carp drop", "Treasure Carp Scale", carp=True),
        SekiroLocationData("HE1: Treasure Carp Scale - near Pot Noble Harunaga, Carp drop", "Treasure Carp Scale",
                           carp=True),
        SekiroLocationData("HE1: Treasure Carp Scale - under Bamboo Thicket Slope bridge, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("HE1: Treasure Carp Scale - underwater, under Bamboo Thicket Slope bridge, Carp drop",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        SekiroLocationData("HE1: Treasure Carp Scale - underwater, Dragonspring Lake, Carp drop #1",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        SekiroLocationData("HE1: Treasure Carp Scale - underwater, Dragonspring Lake, Carp drop #2",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        SekiroLocationData("HE1: Flame Barrel - bonfire", "Flame Barrel", prosthetic=True),
        SekiroLocationData("HE1: Shinobi Axe of the Monkey - Estate Path shortcut, first right courtyard, shrine",
                           "Shinobi Axe of the Monkey", prosthetic=True),
        SekiroLocationData("HE1: Mist Raven's Feathers - three-story pagoda", "Mist Raven's Feathers", progression=True,
                           prosthetic=True, conditional=True),
        SekiroLocationData("HE1: Sakura Droplet - boss drop", "Sakura Droplet", prominent=True,
                           boss=True, conditional=True),
        SekiroLocationData("HE1: Prayer Bead - before Bamboo Thicket Slope, miniboss drop", "Prayer Bead",
                           static="03,0:6763::", miniboss=True),
        SekiroLocationData("HE1: Prayer Bead - Main Hall, miniboss drop", "Prayer Bead",
                           static="03,0:6764::", miniboss=True, conditional=True),
        SekiroLocationData("HE1: Prayer Bead - Audience Chamber, shinobi door chest", "Prayer Bead",
                           static="03,0:6789::", conditional=True),
    ],
    "Ashina Castle": [
        SekiroLocationData("AC: Anti-air Deathblow Text - Blackhat Badger", "Anti-air Deathblow Text", shop=True,
                           offering_box=True),
        SekiroLocationData("AC: Memory: Genichiro", "Memory: Genichiro", prominent=True, boss=True),
        SekiroLocationData("AC: Fragrant Flower Note - Kuro", "Fragrant Flower Note", npc=True),
        SekiroLocationData("AC: Immortal Severance Text - Kuro", "Immortal Severance Text", npc=True),
        # Missable if one does not have Rice for Kuro / does not give it to Kuro
        SekiroLocationData("AC: Sweet Rice Ball - Kuro for Rice for Kuro", "Sweet Rice Ball x2", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("AC: Page's Diary - Kuro", "Page's Diary", npc=True),
        # Missable if not triggered before Fountainhead Incense is placed
        SekiroLocationData("AC: Okami's Ancient Text - Kuro with Lotus of the Palace", "Okami's Ancient Text",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("AC: Immortal Severance Scrap - Emma", "Immortal Severance Scrap", npc=True,
                           conditional=True),
        # Missable if you already have Mortal Blade when speaking to Isshin
        SekiroLocationData("AC: Unrefined Sake - Isshin", "Unrefined Sake", missable=True, npc=True),
        # These are missable after progressing Divine Child questline to eating both Viscera (not missable in Shura)
        SekiroLocationData("AC: Ungo's Sugar - any Old Praying Woman, pop 1 balloon", "Ungo's Sugar", missable=True,
                           npc=True, hidden=True),
        SekiroLocationData("AC: Ako's Sugar - any Old Praying Woman, pop 2 balloons", "Ako's Sugar", missable=True,
                           npc=True, hidden=True),
        SekiroLocationData("AC: Divine Confetti - any Old Praying Woman, pop 3 balloons", "Divine Confetti",
                           missable=True, npc=True, hidden=True),
        # Only given if Fujioka's pursuers are defeated prior to beating AC boss.
        SekiroLocationData("AC: Nightjar Beacon Memo - Fujioka", "Nightjar Beacon Memo", missable=True, npc=True),
        SekiroLocationData("AC: Eel Liver - shrine across from serpent shrine", "Eel Liver x3"),
        SekiroLocationData("AC: Light Coin Purse - upper tower, shinobi door", "Light Coin Purse"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AC: Light Coin Purse - house before bridge to AD", "Light Coin Purse", missable=True),
        SekiroLocationData("AC: Eel Liver - Ashina Dojo", "Eel Liver x3"),
        SekiroLocationData("AC: Mibu Possession Balloon - underwater, lake, near bridge",
                           "Mibu Possession Balloon x2", conditional=True, diving=True),
        SekiroLocationData("AC: Pellet - bird's nest before grappling to castle roof", "Pellet"),
        SekiroLocationData("AC: Fistful of Ash - courtyard right of Ashina Castle idol", "Fistful of Ash x3"),
        SekiroLocationData("AC: Gachiin's Sugar - old grave, courtyard near Blackhat Badger", "Gachiin's Sugar"),
        SekiroLocationData("AC: Pellet - upper tower, room near map room", "Pellet x2"),
        SekiroLocationData("AC: Ako's Sugar - upper tower, map room", "Ako's Sugar"),
        SekiroLocationData("AC: Gokan's Sugar - upper tower, Ashina Dojo idol room", "Gokan's Sugar"),
        SekiroLocationData("AC: Scrap Iron - lake, far ledge", "Scrap Iron x2"),
        SekiroLocationData("AC: Mibu Balloon of Spirit - serpent shrine", "Mibu Balloon of Spirit"),
        SekiroLocationData("AC: Gachiin's Sugar - old grave, bird's nest close to idol", "Gachiin's Sugar"),
        SekiroLocationData("AC: Mibu Possession Balloon - courtyard near AR entrance", "Mibu Possession Balloon"),
        SekiroLocationData("AC: Scrap Magnetite - Kuro's room, behind statue", "Scrap Magnetite"),
        SekiroLocationData("AC: Eel Liver - Isshin's dojo", "Eel Liver x2"),
        SekiroLocationData("AC: Ceramic Shard - area right of main stairway, near Fujioka's pursuers", "Ceramic Shard"),
        SekiroLocationData("AC: Mibu Balloon of Wealth - main stairway, alcove near top", "Mibu Balloon of Wealth"),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AC: Black Gunpowder - outside building at AD entrance", "Black Gunpowder", missable=True),
        SekiroLocationData("AC: Gokan's Sugar - basement, chest room", "Gokan's Sugar"),
        SekiroLocationData("AC: Scrap Iron - courtyard near AR entrance", "Scrap Iron"),
        SekiroLocationData("AC: Gachiin's Sugar - upper tower, rafters", "Gachiin's Sugar x2"),
        SekiroLocationData("AC: Pellet - Isshin's dojo, stairs", "Pellet x2"),
        SekiroLocationData("AC: Gachiin's Sugar - bird's nest on roof near Isshin's watchtower", "Gachiin's Sugar"),
        SekiroLocationData("AC: Scrap Iron - upper tower, map room", "Scrap Iron"),
        SekiroLocationData("AC: Light Coin Purse - upper tower exterior, birds's nest", "Light Coin Purse"),
        SekiroLocationData("AC: Ungo's Sugar - Blackhat Badger building, roof, bird's nest", "Ungo's Sugar"),
        SekiroLocationData("AC: Scrap Magnetite - Ashina Dojo, side room", "Scrap Magnetite"),
        SekiroLocationData("AC: Ceramic Shard - old grave, courtyard near Blackhat Badger", "Ceramic Shard"),
        SekiroLocationData("AC: Pellet - before AR gate", "Pellet"),
        SekiroLocationData("AC: Ceramic Shard - bird's nest on rooftop path", "Ceramic Shard x2"),
        SekiroLocationData("AC: Heavy Coin Purse - upper tower, shinobi door", "Heavy Coin Purse", hidden=True),
        SekiroLocationData("AC: Scrap Iron - ledge right of Ashina Castle idol", "Scrap Iron"),
        SekiroLocationData("AC: Treasure Carp Scale - underwater, by Ashina Castle idol", "Treasure Carp Scale",
                           conditional=True, diving=True),
        SekiroLocationData("AC: Mibu Possession Balloon - lake, bridge", "Mibu Possession Balloon x2"),
        SekiroLocationData("AC: Heavy Coin Purse - underwater, near headless #1", "Heavy Coin Purse", conditional=True,
                           diving=True),
        SekiroLocationData("AC: Heavy Coin Purse - underwater, near headless #2", "Heavy Coin Purse", conditional=True,
                           diving=True),
        SekiroLocationData("AC: Yashariku's Sugar - underwater, near headless against castle wall",
                           "Yashariku's Sugar", conditional=True, diving=True),
        SekiroLocationData("AC: Mibu Possession Balloon - lake, under bridge", "Mibu Possession Balloon"),
        SekiroLocationData("AC: Dragon's Blood Droplet - old grave, near graves", "Dragon's Blood Droplet"),
        SekiroLocationData("AC: Light Coin Purse - old grave, courtyard near Blackhat Badger", "Light Coin Purse"),
        SekiroLocationData("AC: Ceramic Shard - bird's nest before Antechamber idol", "Ceramic Shard"),
        SekiroLocationData("AC: Mibu Balloon of Wealth - upper tower, stairs to Ashina Dojo idol",
                           "Mibu Balloon of Wealth"),
        SekiroLocationData("AC: Pellet - Ashina Dojo, side room", "Pellet"),
        SekiroLocationData("AC: Ungo's Sugar - reservoir tower", "Ungo's Sugar x2"),
        SekiroLocationData("AC: Ceramic Shard - upper tower, right of stairs to Ashina Dojo idol", "Ceramic Shard"),
        SekiroLocationData("AC: Divine Grass - main stairway, chest at top", "Divine Grass"),
        SekiroLocationData("AC: Black Gunpowder - old grave, destroyed bridge", "Black Gunpowder"),
        # Removed once the boss at the top of AC is defeated, if Tengu was met previously.
        SekiroLocationData("AC: Isshin's Letter - Isshin's watchtower", "Isshin's Letter", missable=True),
        SekiroLocationData("AC: Heavy Coin Purse - underwater, near headless #3", "Heavy Coin Purse", conditional=True,
                           diving=True),
        SekiroLocationData("AC: Fistful of Ash - old grave, courtyard near Blackhat Badger", "Fistful of Ash"),
        SekiroLocationData("AC: Gun Fort Shrine Key - Kuro's library", "Gun Fort Shrine Key", progression=True),
        SekiroLocationData("AC: Fistful of Ash - upper tower, by Antechamber idol", "Fistful of Ash"),
        SekiroLocationData("AC: Eel Liver - basement, chest room", "Eel Liver x2"),
        SekiroLocationData("AC: Heavy Coin Purse - courtyard before Old Grave idol, enemy drop", "Heavy Coin Purse",
                           static="02,0:51110971::", drop=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AC: Scrap Magnetite - outside building at AD entrance, enemy drop", "Scrap Magnetite",
                           drop=True, missable=True),
        SekiroLocationData("AC: Ungo's Spiritfall - underwater, headless drop", "Ungo's Spiritfall", miniboss=True,
                           conditional=True, headless=True, diving=True),
        SekiroLocationData("AC: Gatehouse Key - bridge to AD, enemy drop", "Gatehouse Key", drop=True),
        SekiroLocationData("AC: Sabimaru - basement, chest", "Sabimaru", prosthetic=True),
        SekiroLocationData("AC: Gourd Seed - upper tower, chest near Antechamber idol", "Gourd Seed"),
        SekiroLocationData("AC: Bloodsmoke Ninjutsu - boss arena, boss drop", "Bloodsmoke Ninjutsu", boss=True),
        SekiroLocationData("AC: Prayer Bead - main stairway, miniboss drop", "Prayer Bead",
                           static="02,0:6766:9021,1100500:", miniboss=True, offering_box=True),
        SekiroLocationData("AC: Prayer Bead - Ashina Dojo, miniboss drop", "Prayer Bead",
                           static="02,0:6767:9022,1100500:", miniboss=True, offering_box=True),
        SekiroLocationData("AC: Prayer Bead - upper tower, shinobi door, chest", "Prayer Bead",
                           static="02,0:6790::"),
        SekiroLocationData("AC: Iron Fortress - Blackhat Badger", "Iron Fortress", prosthetic=True, shop=True,
                           offering_box=True),
        SekiroLocationData("AC -> SV", None),
    ],
    "Ashina Reservoir": [
        # This applies to all missables in this region:
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AR: Scrap Magnetite - starting well, miniboss drop", "Scrap Magnetite x2", miniboss=True),
        SekiroLocationData("AR: Scrap Iron - tree beside moon-view tower", "Scrap Iron", missable=True),
        SekiroLocationData("AR: Scrap Iron - starting well, ledge above water", "Scrap Iron"),
        SekiroLocationData("AR: Pellet - broken cart in yard", "Pellet", missable=True),
        SekiroLocationData("AR: Ceramic Shard - gatehouse, below", "Ceramic Shard x2", hidden=True, missable=True),
        SekiroLocationData("AR: Fistful of Ash - stairs to gatehouse", "Fistful of Ash", missable=True),
        SekiroLocationData("AR: Scrap Iron - door left of Secret Passage", "Scrap Iron"),
        SekiroLocationData("AR: Heavy Coin Purse - gatehouse, next to chest", "Heavy Coin Purse",
                           static="01,0:51120110::", conditional=True, missable=True),
        SekiroLocationData("AR: Bundled Jizo Statue - moon-view tower, red balcony", "Bundled Jizo Statue",
                           missable=True),
        SekiroLocationData("AR: Mibu Balloon of Soul - underwater, starting well", "Mibu Balloon of Soul",
                           conditional=True, diving=True),
        SekiroLocationData("AR: Heavy Coin Purse - door left of Secret Passage", "Heavy Coin Purse",
                           static="01,0:51120160::"),
        SekiroLocationData("AR: Mibu Balloon of Spirit - moat", "Mibu Balloon of Spirit"),
        SekiroLocationData("AR: Gyoubu's Broken Horn - gatehouse, chest", "Gyoubu's Broken Horn", prosthetic=True,
                           conditional=True, offering_box=True),
        SekiroLocationData("AR: Prayer Bead - moon-view tower, miniboss drop", "Prayer Bead", miniboss=True,
                           offering_box=True),
        SekiroLocationData("AR: Prayer Bead - starting well, miniboss drop", "Prayer Bead", miniboss=True),
    ],
    "Abandoned Dungeon": [
        SekiroLocationData("AD: Prayer Bead - Dungeon Memorial Mob", "Prayer Bead", shop=True),
        SekiroLocationData("AD: Mask Fragment: Dragon - Dungeon Memorial Mob", "Mask Fragment: Dragon", shop=True),
        SekiroLocationData("AD: Heavy Coin Purse - wagon by Dungeon Memorial Mob", "Heavy Coin Purse",
                           static="02,0:51110110::"),

        # The following block is missable if Doujun's quest is not completed
        SekiroLocationData("AD: Red Lump - Underground Waterway island, red-eyed Kotaro, enemy drop", "Red Lump",
                           npc=True, drop=True, missable=True, conditional=True, diving=True),
        SekiroLocationData("AD: Red Lump - Underground Waterway island, red-eyed Jinzaemon, enemy drop", "Red Lump",
                           npc=True, drop=True, missable=True, conditional=True, diving=True),
        SekiroLocationData("AD: Surgeon's Bloody Letter - start Doujun's quest", "Surgeon's Bloody Letter",
                           missable=True, npc=True),
        SekiroLocationData("AD: Lump of Fat Wax - Doujun after sending subject", "Lump of Fat Wax x3", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("AD: Surgeon's Stained Letter - Doujun requests Red Carp Eyes", "Surgeon's Stained Letter",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("AD: Lump of Grave Wax - Doujun for Red Carp Eyes", "Lump of Grave Wax x2", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("AD: Academics' Red Lump - Underground Waterway island, red-eyed Doujun, enemy drop",
                           "Academics' Red Lump", drop=True, npc=True, missable=True, conditional=True, diving=True),

        SekiroLocationData("AD: Dosaku's Note - underwater, Doujun's cell", "Dosaku's Note", conditional=True,
                           diving=True),
        SekiroLocationData("AD: Rotting Prisoner's Note - cell, first on the left", "Rotting Prisoner's Note"),
        SekiroLocationData("AD: Pacifying Agent - Underground Waterway island", "Pacifying Agent x2"),
        SekiroLocationData("AD: Pacifying Agent - cell, first on the right", "Pacifying Agent x2"),
        SekiroLocationData("AD: Pacifying Agent - along right wall", "Pacifying Agent x3"),
        SekiroLocationData("AD: Oil - cricket pit #1", "Oil"),
        SekiroLocationData("AD: Mibu Balloon of Soul - Bottomless Hole, wooden planks above miniboss arena",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("AD: Oil - cricket pit #2", "Oil"),
        SekiroLocationData("AD: Mibu Balloon of Soul - Bottomless Hole, stalagmite in miniboss arena",
                           "Mibu Balloon of Soul x2"),
        SekiroLocationData("AD: Red Lump - corpse before Underground Waterway idol", "Red Lump"),
        SekiroLocationData("AD: Ako's Sugar - Underground Waterway island, boat", "Ako's Sugar x2"),
        SekiroLocationData("AD: Light Coin Purse - Underground Waterway island", "Light Coin Purse"),
        SekiroLocationData("AD: Bite Down - thin cave connecting AD to Bottomless Hole", "Bite Down"),
        SekiroLocationData("AD: Pacifying Agent - Bottomless Hole, small platform above miniboss arena",
                           "Pacifying Agent"),
        SekiroLocationData("AD: Bulging Coin Purse - Bottomless Hole, stalagmite near idol", "Bulging Coin Purse"),
        SekiroLocationData("AD: Light Coin Purse - underwater, Underground Waterway #1, 3-item group",
                           "Light Coin Purse", conditional=True, diving=True),
        SekiroLocationData("AD: Ceramic Shard - underwater, Underground Waterway", "Ceramic Shard", conditional=True,
                           diving=True),
        SekiroLocationData("AD: Mibu Balloon of Soul - Bottomless Hole drop, top platform after falling",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("AD: Fistful of Ash - Bottomless Hole, before drop to Ashina Depths idol",
                           "Fistful of Ash x2"),
        SekiroLocationData("AD: Mibu Balloon of Soul - underwater, grapple after path to Doujun's cell",
                           "Mibu Balloon of Soul x3", conditional=True, diving=True),
        SekiroLocationData("AD: Pacifying Agent - underwater, Doujun's cell", "Pacifying Agent x5", conditional=True,
                           diving=True),
        SekiroLocationData("AD: Black Gunpowder - Underground Waterway island", "Black Gunpowder"),
        SekiroLocationData("AD: Scrap Magnetite - Bottomless Hole, wall in miniboss arena", "Scrap Magnetite"),
        SekiroLocationData("AD: Scrap Iron - Underground Waterway, ramp after idol", "Scrap Iron"),
        SekiroLocationData("AD: Black Gunpowder - Bottomless Hole, alcove in miniboss arena", "Black Gunpowder"),
        SekiroLocationData("AD: Light Coin Purse - underwater, Underground Waterway #2, 3-item group",
                           "Light Coin Purse", conditional=True, diving=True),
        SekiroLocationData("AD: Light Coin Purse - underwater, Underground Waterway #3, 3-item group",
                           "Light Coin Purse", conditional=True, diving=True),
        SekiroLocationData("AD: Ceremonial Tanto - Bottomless Hole, miniboss drop", "Ceremonial Tanto", miniboss=True),
        SekiroLocationData("AD -> ST", None),
        SekiroLocationData("AD -> PP", None),
    ],
    "Senpou Temple, Mt. Kongo": [
        # Missable if Kotaro's quest is not done / he is sent to Anayama or Doujun.
        SekiroLocationData("ST: Taro Persimmon - Halls of Illusion, Kotaro quest", "Taro Persimmon", npc=True,
                           missable=True, conditional=True),
        SekiroLocationData("ST: Five-color Rice - Shugendo Memorial Mob", "Five-color Rice", shop=True),
        SekiroLocationData("ST: Memory: Screen Monkeys", "Memory: Screen Monkeys", boss=True),
        SekiroLocationData("ST: Mortal Blade - Divine Child", "Mortal Blade", npc=True, prominent=True,
                           progression=True),
        # Missable if Divine Child quest is not followed / Rice for Kuro is already obtained.
        SekiroLocationData("ST: Rice for Kuro - Divine Child for Persimmon", "Rice for Kuro", npc=True, missable=True,
                           conditional=True),
        # Missable if Divine Child quest is not followed
        SekiroLocationData("ST: Frozen Tears - Divine Child for both Serpent Viscera after first invasion",
                           "Frozen Tears", missable=True, npc=True, progression=True, conditional=True),
        SekiroLocationData("ST: Holy Chapter: Infested - underwater, carp pond", "Holy Chapter: Infested",
                           conditional=True, diving=True),
        # Missable if Divine Child quest is not followed
        SekiroLocationData("ST: Holy Chapter: Dragon's Return - cave, blue-robed corpse after Holy Chapter: Infested",
                           "Holy Chapter: Dragon's Return", missable=True, conditional=True),
        SekiroLocationData("ST: Monkey Booze - right room before Bell Demon's Temple idol", "Monkey Booze"),
        SekiroLocationData("ST: Red and White Pinwheel - hill with many pinwheels before bridge arena",
                           "Red and White Pinwheel"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - after Sunken Valley Cavern idol", "Mibu Balloon of Spirit x3",
                           conditional=True),
        SekiroLocationData("ST: Gachiin's Sugar - broken bridge", "Gachiin's Sugar"),
        SekiroLocationData("ST: Antidote Powder - cliffside right of cricket building #1, 3-item group",
                           "Antidote Powder x2"),
        SekiroLocationData("ST: Gokan's Sugar - below Temple Grounds idol", "Gokan's Sugar"),
        SekiroLocationData("ST: Ungo's Sugar - Main Hall, right wing", "Ungo's Sugar", static="07,0:52000100::"),
        SekiroLocationData("ST: Ceramic Shard - rooftop in front of Temple Grounds idol", "Ceramic Shard x2"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - temple grounds side path #1 ",
                           "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - temple grounds side path #2",
                           "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Lump of Fat Wax - atrium, inside main building", "Lump of Fat Wax"),
        SekiroLocationData("ST: Gokan's Sugar - cricket building, left of exit window", "Gokan's Sugar"),
        SekiroLocationData("ST: White Pinwheel - hidden cliff before Bell Demon's Temple idol", "White Pinwheel"),
        SekiroLocationData("ST: Scrap Iron - uphill from Kotaro", "Scrap Iron x2"),
        SekiroLocationData("ST: Ako's Sugar - cliff left of Main Hall", "Ako's Sugar", static="07,0:52000190::"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - area with kite mechanism", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Ungo's Sugar - under stairs before Main Hall", "Ungo's Sugar x3",
                           static="07,0:52000210::"),
        SekiroLocationData("ST: Gokan's Sugar - cliffside temple", "Gokan's Sugar"),
        SekiroLocationData("ST: Gachiin's Sugar - left of Senpou Temple, Mt. Kongo idol building", "Gachiin's Sugar"),
        SekiroLocationData("ST: Pellet - cave, under tree after exiting", "Pellet x2"),
        SekiroLocationData("ST: Pellet - temple grounds side path, top", "Pellet"),
        SekiroLocationData("ST: Pellet - left of broken bridge", "Pellet"),
        SekiroLocationData("ST: Heavy Coin Purse - along hidden path to Bell Demon's Temple idol", "Heavy Coin Purse",
                           static="07,0:52000280::"),
        SekiroLocationData("ST: Gachiin's Sugar - area with kite mechanism", "Gachiin's Sugar"),
        SekiroLocationData("ST: Ceramic Shard - nest before Shugendo Memorial Mob", "Ceramic Shard x3"),
        SekiroLocationData("ST: Black Gunpowder - cliffside temple #1", "Black Gunpowder x2"),
        SekiroLocationData("ST: Mibu Possession Balloon - left cliff before cricket building",
                           "Mibu Possession Balloon x2"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - temple grounds side path #3",
                           "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Fistful of Ash - ground before cricket building entrance", "Fistful of Ash"),
        SekiroLocationData("ST: Light Coin Purse - cliffside right of cricket building, 3-item group",
                           "Light Coin Purse", static="07,0:52000400::"),
        SekiroLocationData("ST: Ungo's Sugar - right balcony before broken bridge", "Ungo's Sugar",
                           static="07,0:52000410::"),
        SekiroLocationData("ST: Ceramic Shard - atrium, left side outside the wall", "Ceramic Shard x2"),
        SekiroLocationData("ST: Heavy Coin Purse - temple grounds side path, broken bridge", "Heavy Coin Purse",
                           static="07,0:52000430::"),
        SekiroLocationData("ST: Ako's Sugar - stairs before cricket building", "Ako's Sugar", static="07,0:52000440::"),
        SekiroLocationData("ST: Snap Seed - after kite jump", "Snap Seed x2", conditional=True),
        SekiroLocationData("ST: Ako's Sugar - cricket building, after grappling", "Ako's Sugar",
                           static="07,0:52000460::"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - cricket building, right of exit", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Black Gunpowder - room before Bell Demon's Temple idol", "Black Gunpowder"),
        SekiroLocationData("ST: Antidote Powder - left corner before broken bridge", "Antidote Powder"),
        SekiroLocationData("ST: Scrap Magnetite - before Sunken Valley Cavern idol", "Scrap Magnetite",
                           conditional=True),
        SekiroLocationData("ST: Scrap Magnetite - next to Temple Grounds idol", "Scrap Magnetite"),
        SekiroLocationData("ST: Black Gunpowder - Main Hall, right wing", "Black Gunpowder"),
        SekiroLocationData("ST: Black Gunpowder - cliffside temple #2", "Black Gunpowder"),
        SekiroLocationData("ST: Lump of Fat Wax - Main Hall, behind large statue", "Lump of Fat Wax"),
        SekiroLocationData("ST: Ceramic Shard - cricket building, left of exit window", "Ceramic Shard x4"),
        SekiroLocationData("ST: Pellet - Main Hall, left wing", "Pellet"),
        SekiroLocationData("ST: Heavy Coin Purse - right room before Bell Demon's Temple idol", "Heavy Coin Purse",
                           static="07,0:52000590::"),
        SekiroLocationData("ST: Pellet - behind Inner Sanctum building", "Pellet x2"),
        SekiroLocationData("ST: Fistful of Ash - balcony overlooking carp pond", "Fistful of Ash x3"),
        SekiroLocationData("ST: Mibu Possession Balloon - tree above temple grounds side path",
                           "Mibu Possession Balloon", hidden=True),
        SekiroLocationData("ST: Light Coin Purse - atrium, right side near exit", "Light Coin Purse",
                           static="07,0:52000650::"),
        SekiroLocationData("ST: Ungo's Sugar - sloped path, near enemies after bonfire", "Ungo's Sugar",
                           static="07,0:52000660::"),
        SekiroLocationData("ST: Fistful of Ash - sloped path, beside bonfire", "Fistful of Ash x5", hidden=True),
        SekiroLocationData("ST: Mibu Balloon of Spirit - sloped path. base", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Gokan's Sugar - sloped path, ledge above tall grass", "Gokan's Sugar"),
        SekiroLocationData("ST: Bundled Jizo Statue - Main Hall, amid statues left of idol", "Bundled Jizo Statue"),
        # Make sure to separate this from shop persimmons, so keep static
        SekiroLocationData("ST: Persimmon - temple grounds side path, persimmon tree", "Persimmon",
                           static="07,0:52000710::"),
        SekiroLocationData("ST: Dragon's Blood Droplet - Main Hall, held by statue", "Dragon's Blood Droplet",
                           static="07,0:52000720::"),
        SekiroLocationData("ST: Lump of Fat Wax - cricket building, behind shrine", "Lump of Fat Wax"),
        SekiroLocationData("ST: Pacifying Agent - near left wall before cricket building", "Pacifying Agent"),
        SekiroLocationData("ST: Pellet - left of path to cricket building", "Pellet"),
        SekiroLocationData("ST: Light Coin Purse - roof of mini gate at area start", "Light Coin Purse",
                           static="07,0:52000770::", hidden=True),
        SekiroLocationData("ST: Gachiin's Sugar - separate stone pillar in Shugendo", "Gachiin's Sugar"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - Shugendo, cave path", "Mibu Balloon of Spirit x2"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - cave, shallow section with puddle", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Antidote Powder - cliffside right of cricket building #2, 3-item group",
                           "Antidote Powder"),
        SekiroLocationData("ST: Heavy Coin Purse - elevated cliff right of cricket building entrance",
                           "Heavy Coin Purse", static="07,0:52000840::"),
        SekiroLocationData("ST: Light Coin Purse - nest on large tree after cricket building exit", "Light Coin Purse",
                           static="07,0:52000850::"),
        SekiroLocationData("ST: Heavy Coin Purse - broken bridge, enemy drop", "Heavy Coin Purse",
                           static="07,0:52000900::", drop=True),
        SekiroLocationData("ST: Bulging Coin Purse - kill 3 enemies outside Main Hall, enemy drop",
                           "Bulging Coin Purse", drop=True),
        SekiroLocationData("ST: Scrap Magnetite - sloped path, enemies after bonfire, enemy drop", "Scrap Magnetite",
                           drop=True),
        SekiroLocationData("ST: Yellow Gunpowder - cliffside temple, miniboss drop", "Yellow Gunpowder x2",
                           miniboss=True),
        SekiroLocationData("ST: Treasure Carp Scale - carp pond, Carp drop #1", "Treasure Carp Scale", carp=True),
        SekiroLocationData("ST: Treasure Carp Scale - carp pond, Carp drop #2", "Treasure Carp Scale", carp=True),
        SekiroLocationData("ST: Senpou Esoteric Text - cave, pagoda after exiting", "Senpou Esoteric Text"),
        SekiroLocationData("ST: Breath of Nature: Shadow - bridge arena, miniboss drop", "Breath of Nature: Shadow",
                           miniboss=True),
        SekiroLocationData("ST: Gourd Seed - cricket building, main room", "Gourd Seed"),
        SekiroLocationData("ST: Puppeteer Ninjutsu - Halls of Illusion, boss drop", "Puppeteer Ninjutsu",
                           prominent=True, progression=True, boss=True),
        SekiroLocationData("ST: Prayer Bead - bridge arena, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("ST: Prayer Bead - cliffside temple, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("ST: Prayer Bead - underwater, carp pond", "Prayer Bead", conditional=True, diving=True),
    ],
    "Sunken Valley": [
        SekiroLocationData("SV: Pellet - Gun Fort, under wooden battlement", "Pellet x2"),
        SekiroLocationData("SV: Divine Grass - pond cave, behind giant pillar", "Divine Grass", conditional=True,
                           hidden=True, diving=True),
        SekiroLocationData("SV: Antidote Powder - Gun Fort approach, right ledge near miniboss", "Antidote Powder"),
        SekiroLocationData("SV: Pacifying Agent - before pond cave, near pond", "Pacifying Agent"),
        SekiroLocationData("SV: Divine Confetti - Gun Fort chasm, dead-end tunnel", "Divine Confetti x3"),
        SekiroLocationData("SV: Black Gunpowder - Gun Fort, along path to cave entrance", "Black Gunpowder"),
        SekiroLocationData("SV: Antidote Powder - shimmy before Sunken Valley idol", "Antidote Powder"),
        SekiroLocationData("SV: Gokan's Sugar - Gun Fort, ledge left of cave entrance", "Gokan's Sugar", hidden=True),
        SekiroLocationData("SV: Ungo's Sugar - Gun Fort, stone pillar facing cave entrance", "Ungo's Sugar",
                           hidden=True),
        SekiroLocationData("SV: Scrap Magnetite - Gun Fort approach, slope left of miniboss", "Scrap Magnetite"),
        SekiroLocationData("SV: Scrap Magnetite - right of Sunken Valley idol", "Scrap Magnetite"),
        SekiroLocationData("SV: Mibu Balloon of Soul - Gun Fort chasm, wooden planks", "Mibu Balloon of Soul x3"),
        SekiroLocationData("SV: Scrap Magnetite - Gun Fort approach, rightmost ledge overlooking rope bridge",
                           "Scrap Magnetite"),
        SekiroLocationData("SV: Black Gunpowder - Gun Fort, right barricade", "Black Gunpowder x2"),
        SekiroLocationData("SV: Heavy Coin Purse - Gun Fort, under wooden battlement", "Heavy Coin Purse"),
        SekiroLocationData("SV: Scrap Magnetite - Gun Fort, ledge behind barricades", "Scrap Magnetite"),
        SekiroLocationData("SV: Snap Seed - Gun Fort, atop wooden battlement", "Snap Seed x3"),
        SekiroLocationData("SV: Fistful of Ash - right of Under-Shrine Valley idol", "Fistful of Ash x2"),
        SekiroLocationData("SV: Scrap Magnetite - Gun Fort shrine, right of statue", "Scrap Magnetite"),
        SekiroLocationData("SV: Ceramic Shard - right ledge before hidden encampment path", "Ceramic Shard"),
        SekiroLocationData("SV: Yellow Gunpowder - hidden encampment", "Yellow Gunpowder"),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort, under wooden battlement", "Yellow Gunpowder"),
        SekiroLocationData("SV: Fistful of Ash - Gun Fort approach, ground right of miniboss", "Fistful of Ash x2"),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort shrine, below in crawl space", "Yellow Gunpowder"),
        SekiroLocationData("SV: Pacifying Agent - before pond cave, behind frozen waterfall", "Pacifying Agent x3",
                           hidden=True),
        SekiroLocationData("SV: Contact Medicine - Gun Fort chasm, bottom ledge", "Contact Medicine"),
        SekiroLocationData("SV: Lump of Grave Wax - pond cave, behind miniboss", "Lump of Grave Wax", conditional=True,
                           diving=True),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort shrine, miniboss drop", "Yellow Gunpowder x2",
                           miniboss=True),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort, enemy drop", "Yellow Gunpowder x3", drop=True),
        SekiroLocationData("SV: Gokan's Spiritfall - pond cave, miniboss drop", "Gokan's Spiritfall", conditional=True,
                           miniboss=True, headless=True, diving=True),
        SekiroLocationData("SV: Large Fan - Gun Fort shrine, statue", "Large Fan", prosthetic=True),
        SekiroLocationData("SV: Gourd Seed - behind hidden encampment", "Gourd Seed"),
        SekiroLocationData("SV: Prayer Bead - Gun Fort approach, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("SV: Prayer Bead - Gun Fort shrine, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("SV: Prayer Bead - before pond cave, near stone pyramid", "Prayer Bead"),
        SekiroLocationData("SV: Prayer Bead - Gun Fort chasm, bottom ledge", "Prayer Bead"),
    ],
    "Sunken Valley Passage": [
        SekiroLocationData("SVP: Green Mossy Gourd - Toxic Memorial Mob", "Green Mossy Gourd", shop=True),
        SekiroLocationData("SVP: Memory: Guardian Ape", "Memory: Guardian Ape", prominent=True, boss=True),
        SekiroLocationData("SVP: Lotus of the Palace - cave behind Guardian Ape's Watering Hole idol",
                           "Lotus of the Palace", prominent=True, progression=True),
        SekiroLocationData("SVP: Snap Seed - first left bodhi statue, base", "Snap Seed x3"),
        SekiroLocationData("SVP: Mibu Balloon of Soul - ledge under Bodhisattva Valley idol", "Mibu Balloon of Soul"),
        SekiroLocationData("SVP: Scrap Magnetite - shrine cave, 3-item group", "Scrap Magnetite"),
        SekiroLocationData("SVP: Snap Seed - right ledge after Gun Fort shrine", "Snap Seed x2"),
        # Missable as if you warp away before picking up, you cannot go back.
        SekiroLocationData("SVP: Dragon's Blood Droplet - Sunken Valley Cavern, after killing serpent",
                           "Dragon's Blood Droplet", missable=True, conditional=True),
        SekiroLocationData("SVP: Ungo's Sugar - left side ledge opposite of 23-enemy cluster", "Ungo's Sugar"),
        SekiroLocationData("SVP: Pacifying Agent - ledge next to 23-enemy cluster", "Pacifying Agent"),
        SekiroLocationData("SVP: Mibu Balloon of Soul - alcove left of swamp island", "Mibu Balloon of Soul"),
        SekiroLocationData("SVP: Divine Confetti - underground shrine, ledge above", "Divine Confetti x3",
                           conditional=True),
        SekiroLocationData("SVP: Snap Seed - next to Toxic Memorial Mob", "Snap Seed"),
        SekiroLocationData("SVP: Light Coin Purse - swamp island, behind right mound", "Light Coin Purse"),
        SekiroLocationData("SVP: Ako's Sugar - third left bodhi statue, base", "Ako's Sugar x2"),
        SekiroLocationData("SVP: Adamantite Scrap - underwater, lake opposite from Riven Cave entrance",
                           "Adamantite Scrap", conditional=True, diving=True),
        SekiroLocationData("SVP: Scrap Magnetite - swamp island, dead tree", "Scrap Magnetite"),
        SekiroLocationData("SVP: Antidote Powder - shrine cave, shortly after entering", "Antidote Powder x2"),
        SekiroLocationData("SVP: Fistful of Ash - shrine cave, under low arch", "Fistful of Ash x2"),
        SekiroLocationData("SVP: Fulminated Mercury - swamp island, behind left mound", "Fulminated Mercury"),
        SekiroLocationData("SVP: Bulging Coin Purse - underwater, log in middle of lake", "Bulging Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Yellow Gunpowder - under Bodhisattva Valley idol in toxic water", "Yellow Gunpowder",
                           static="06,0:51700580::"),
        SekiroLocationData("SVP: Heavy Coin Purse - swamp below Bodhisattva Valley idol", "Heavy Coin Purse"),
        SekiroLocationData("SVP: Yashariku's Sugar - underwater, lake between rocks", "Yashariku's Sugar",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Pacifying Agent - in front of broken bodhi head", "Pacifying Agent"),
        SekiroLocationData("SVP: Contact Medicine - dropdown after broken bodhi head", "Contact Medicine x3"),
        SekiroLocationData("SVP: Scrap Magnetite - behind fallen bodhi statue's head", "Scrap Magnetite"),
        SekiroLocationData("SVP: Contact Medicine - last upright left bodhi statue, behind", "Contact Medicine x3"),
        SekiroLocationData("SVP: Monkey Booze - kill 23-enemy cluster between statues, enemy drop", "Monkey Booze",
                           drop=True),
        SekiroLocationData("SVP: Ungo's Sugar - island before Toxic Memorial Mob", "Ungo's Sugar"),
        SekiroLocationData("SVP: Scrap Magnetite - shrine cave, late along left wall and up", "Scrap Magnetite x2"),
        SekiroLocationData("SVP: Mibu Balloon of Soul - underground shrine, back porch", "Mibu Balloon of Soul",
                           conditional=True),
        SekiroLocationData("SVP: Pellet - shrine cave, 3-item group", "Pellet x2"),
        SekiroLocationData("SVP: Fistful of Ash - shrine cave, 3-item group", "Fistful of Ash"),
        SekiroLocationData("SVP: Dried Serpent Viscera - underground shrine, statue", "Dried Serpent Viscera",
                           progression=True, conditional=True),
        SekiroLocationData("SVP: Precious Bait - underwater, Guardian Ape's Watering Hole", "Precious Bait",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Adamantite Scrap - grapple spot above Riven Cave idol", "Adamantite Scrap"),
        SekiroLocationData("SVP: Scrap Iron - behind 23-enemy cluster", "Scrap Iron x3"),
        # Missable as if you warp away before picking up, you cannot go back.
        SekiroLocationData("SVP: Mibu Balloon of Soul - Sunken Valley Cavern, lake overlook after killing serpent",
                           "Mibu Balloon of Soul", missable=True, conditional=True),
        # Missable as if you warp away before picking up, you cannot go back.
        SekiroLocationData("SVP: Bundled Jizo Statue - Sunken Valley Cavern, after killing serpent",
                           "Bundled Jizo Statue", missable=True, conditional=True),
        SekiroLocationData("SVP: Treasure Carp Scale - underwater, lake at Riven Cave entrance",
                           "Treasure Carp Scale", conditional=True, diving=True),
        SekiroLocationData("SVP: Great White Whisker - Guardian Ape's Watering Hole, after killing Giant Carp",
                           "Great White Whisker", conditional=True),
        SekiroLocationData("SVP: Gachiin's Sugar - underwater, lake opposite from Riven Cave entrance",
                           "Gachiin's Sugar x3", conditional=True, diving=True),
        SekiroLocationData("SVP: Yellow Gunpowder - swamp island, enemy drop", "Yellow Gunpowder",
                           static="06,0:51700931::", drop=True),
        SekiroLocationData("SVP: Yellow Gunpowder - before Toxic Memorial Mob, enemy drop", "Yellow Gunpowder",
                           static="06,0:51700935::", drop=True),
        SekiroLocationData("SVP: Fresh Serpent Viscera - Sunken Valley Cavern, plunge kill serpent, enemy drop",
                           "Fresh Serpent Viscera", progression=True, drop=True, conditional=True),
        SekiroLocationData("SVP: Treasure Carp Scale - underwater, lake far from Riven Cave entrance, Carp drop",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        SekiroLocationData("SVP: Treasure Carp Scale - underwater, lake close to Riven Cave entrance, Carp drop",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        SekiroLocationData("SVP: Slender Finger - Guardian Ape's Watering Hole, boss drop", "Slender Finger",
                           boss=True, prosthetic=True),
    ],
    "Poison Pool": [
        SekiroLocationData("PP: Memory: Headless Ape", "Memory: Headless Ape", prominent=True, boss=True,
                           conditional=True),
        SekiroLocationData("PP: Pacifying Agent - next to Ashina Depths idol", "Pacifying Agent x2"),
        SekiroLocationData("PP: Oil - ledge above Poison Pool idol", "Oil x3"),
        SekiroLocationData("PP: Scrap Magnetite - outcropping, among enemies", "Scrap Magnetite"),
        SekiroLocationData("PP: Scrap Magnetite - central island", "Scrap Magnetite"),
        SekiroLocationData("PP: Scrap Magnetite - hand of giant statue against right wall", "Scrap Magnetite"),
        SekiroLocationData("PP: Yellow Gunpowder - before tallest statue top", "Yellow Gunpowder"),
        SekiroLocationData("PP: Yellow Gunpowder - behind stone head near left wall", "Yellow Gunpowder"),
        SekiroLocationData("PP: Mibu Possession Balloon - central island", "Mibu Possession Balloon x3"),
        SekiroLocationData("PP: Black Gunpowder - outcropping, among enemies", "Black Gunpowder x2"),
        SekiroLocationData("PP: Pellet - tiny island near Poison Pool idol", "Pellet x2"),
        SekiroLocationData("PP: Heavy Coin Purse - poison against left wall", "Heavy Coin Purse"),
        SekiroLocationData("PP: Monkey Booze - above Guardian Ape's Burrow", "Monkey Booze"),
        SekiroLocationData("PP: Malcontent's Ring - Guardian Ape's Burrow, miniboss drop", "Malcontent's Ring",
                           miniboss=True, conditional=True),
        SekiroLocationData("PP: Bestowal Ninjutsu - Guardian Ape's Burrow, boss drop", "Bestowal Ninjutsu", boss=True,
                           conditional=True),
        SekiroLocationData("PP: Prayer Bead - miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("PP: Prayer Bead - top of tallest statue", "Prayer Bead", hidden=True),
        SekiroLocationData("PP: Prayer Bead - Guardian Ape's Burrow, boss drop #1", "Prayer Bead", boss=True,
                           conditional=True),
        SekiroLocationData("PP: Prayer Bead - Guardian Ape's Burrow, boss drop #2", "Prayer Bead", boss=True,
                           conditional=True),
    ],
    "Hidden Forest": [
        SekiroLocationData("HF: Heavy Coin Purse - temple front, pit", "Heavy Coin Purse"),
        SekiroLocationData("HF: Ceramic Shard - above sinkhole, branch before bonfire", "Ceramic Shard x2"),
        SekiroLocationData("HF: Mibu Balloon of Wealth - sinkhole, 3-item group", "Mibu Balloon of Wealth x3"),
        SekiroLocationData("HF: Scrap Iron - sinkhole, 3-item group", "Scrap Iron x5"),
        SekiroLocationData("HF: Pellet - sinkhole, 3-item group", "Pellet"),
        SekiroLocationData("HF: Pellet - sinkhole, ledge above Bonfire", "Pellet"),
        SekiroLocationData("HF: Light Coin Purse - above sinkhole, right side cliff", "Light Coin Purse"),
        SekiroLocationData("HF: Oil - temple front, near stone lantern", "Oil"),
        SekiroLocationData("HF: Ceramic Shard - behind temple", "Ceramic Shard x2"),
        SekiroLocationData("HF: Contact Medicine - temple front, 3-item group", "Contact Medicine x2"),
        SekiroLocationData("HF: Bite Down - temple front, 3-item group", "Bite Down"),
        SekiroLocationData("HF: Light Coin Purse - temple front, 3-item group", "Light Coin Purse"),
        SekiroLocationData("HF: Yashariku's Sugar - inside temple", "Yashariku's Sugar"),
        SekiroLocationData("HF: Adamantite Scrap - ledge opposite of temple", "Adamantite Scrap"),
        SekiroLocationData("HF: Snap Seed - near shimmy in front of temple", "Snap Seed x3"),
        SekiroLocationData("HF: Fistful of Ash - cliffside, bonfire near miniboss", "Fistful of Ash"),
        SekiroLocationData("HF: Pellet - cliffside, ledge hang at end", "Pellet x3"),
        SekiroLocationData("HF: Yashariku's Sugar - sinkhole, up ledge behind miniboss", "Yashariku's Sugar x3"),
        SekiroLocationData("HF: Scrap Magnetite - sinkhole, beside miniboss", "Scrap Magnetite"),
        SekiroLocationData("HF: Scrap Magnetite - sinkhole, gravestone on hill", "Scrap Magnetite"),
        SekiroLocationData("HF: Yellow Gunpowder - right of temple front, against wall", "Yellow Gunpowder"),
        SekiroLocationData("HF: Lump of Fat Wax - sinkhole, beside miniboss", "Lump of Fat Wax"),
        SekiroLocationData("HF: Lump of Fat Wax - after cliffside path", "Lump of Fat Wax"),
        SekiroLocationData("HF: Mibu Balloon of Soul - above sinkhole, before second branch", "Mibu Balloon of Soul"),
        SekiroLocationData("HF: Bite Down - temple front, right side", "Bite Down"),
        SekiroLocationData("HF: Oil - left of temple", "Oil"),
        SekiroLocationData("HF: Lump of Grave Wax - temple, miniboss drop", "Lump of Grave Wax", miniboss=True),
        SekiroLocationData("HF: Gachiin's Spiritfall - sinkhole, miniboss drop", "Gachiin's Spiritfall", miniboss=True,
                           headless=True),
        SekiroLocationData("HF: Unrefined Sake - cliffside, miniboss drop", "Unrefined Sake", miniboss=True),
        SekiroLocationData("HF: Prayer Bead - cliffside, miniboss drop", "Prayer Bead", miniboss=True),
    ],
    "Mibu Village": [
        SekiroLocationData("MV: Mottled Purple Gourd - Exiled Memorial Mob", "Mottled Purple Gourd", shop=True),
        SekiroLocationData("MV: Dragonspring Sake - Exiled Memorial Mob", "Dragonspring Sake",
                           static="05,0:-1:1500000:", shop=True),
        SekiroLocationData("MV: Mibu Breathing Technique - Wedding Cave, boss drop", "Mibu Breathing Technique",
                           prominent=True, progression=True, boss=True),
        SekiroLocationData("MV: Memory: Corrupted Monk", "Memory: Corrupted Monk", boss=True),
        SekiroLocationData("MV: Dragonspring Sake - Head Priest for Water of the Palace", "Dragonspring Sake",
                           static="05,0:50006280::", npc=True, conditional=True),
        # Technically missable due to it being a pickup, not an auto drop. If you reload, it despawns.
        SekiroLocationData("MV: Treasure Carp Scale - Head Priest's house, enemy drop", "Treasure Carp Scale x5",
                           npc=True, drop=True, conditional=True, missable=True),
        # Missable if the player chooses to send Jinzaemon to Doujun or just ignores him
        SekiroLocationData("MV: Jinza's Jizo Statue - Jinzaemon reward after killing miniboss", "Jinza's Jizo Statue",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("MV: Ashina Sake - villager fields, shrine", "Ashina Sake"),
        SekiroLocationData("MV: Shelter Stone - Wedding Cave", "Shelter Stone", prominent=True, progression=True,
                           conditional=True),
        SekiroLocationData("MV: Mibu Balloon of Soul - main path, big tree bed right", "Mibu Balloon of Soul"),
        SekiroLocationData("MV: Treasure Carp Scale - near enemy downstream from Mibu Village idol",
                           "Treasure Carp Scale"),
        SekiroLocationData("MV: Mibu Balloon of Soul - near tree on bank before docks", "Mibu Balloon of Soul"),
        SekiroLocationData("MV: Pacifying Agent - main path, behind Shosuke's house", "Pacifying Agent"),
        SekiroLocationData("MV: Mibu Balloon of Wealth - boat by the docks", "Mibu Balloon of Wealth x2"),
        SekiroLocationData("MV: Fistful of Ash - second house with hole in roof", "Fistful of Ash x5"),
        SekiroLocationData("MV: Pellet - dried riverbank left of big tree", "Pellet x3", static="05,0:51500280::"),
        SekiroLocationData("MV: Contact Medicine - villager fields, middle", "Contact Medicine x2"),
        SekiroLocationData("MV: Yellow Gunpowder - building before Water Mill idol", "Yellow Gunpowder"),
        SekiroLocationData("MV: Mibu Balloon of Soul - main path, after big tree behind barricade",
                           "Mibu Balloon of Soul x2"),
        SekiroLocationData("MV: Light Coin Purse - underwater, pond village side #1", "Light Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("MV: Light Coin Purse - underwater, pond village side #2", "Light Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("MV: Precious Bait - underwater, river upstream from Head Priest's house", "Precious Bait",
                           conditional=True, diving=True),
        SekiroLocationData("MV: Pellet - top of plank before Water Mill idol", "Pellet x2", static="05,0:51500360::"),
        SekiroLocationData("MV: Contact Medicine - house before Inuhiko's house", "Contact Medicine"),
        SekiroLocationData("MV: Fistful of Ash - Inuhiko's house, front", "Fistful of Ash x3"),
        SekiroLocationData("MV: Light Coin Purse - right of Exiled Memorial Mob, up ledge past enemies",
                           "Light Coin Purse"),
        SekiroLocationData("MV: Pellet - before descending to MV", "Pellet x2", static="05,0:51500400::"),
        SekiroLocationData("MV: Divine Confetti - building before Water Mill idol", "Divine Confetti"),
        SekiroLocationData("MV: Adamantite Scrap - Inuhiko's house, bird's nest on roof", "Adamantite Scrap",
                           static="05,0:51500450::"),
        SekiroLocationData("MV: Red Lump - Head Priest's house, behind pots", "Red Lump x2"),
        SekiroLocationData("MV: Adamantite Scrap - villager fields, upper ledge on right", "Adamantite Scrap",
                           static="05,0:51500470::"),
        SekiroLocationData("MV: Black Gunpowder - main path, before big tree", "Black Gunpowder x2"),
        SekiroLocationData("MV: Lump of Fat Wax - behind house closest to Exiled Memorial Mob", "Lump of Fat Wax"),
        SekiroLocationData("MV: Adamantite Scrap - Head Priest's house, behind", "Adamantite Scrap",
                           static="05,0:51500530::"),
        SekiroLocationData("MV: Lump of Fat Wax - right before bridge to Head Priest's house", "Lump of Fat Wax"),
        SekiroLocationData("MV: Mibu Balloon of Soul - grapple from Inuhiko's house, up the path",
                           "Mibu Balloon of Soul x2", hidden=True),
        SekiroLocationData("MV: Divine Confetti - Head Priest's house, statue", "Divine Confetti x5"),
        SekiroLocationData("MV: Divine Grass - bottom waterfall chest", "Divine Grass"),
        SekiroLocationData("MV: Heavy Coin Purse - Head Priest's house, bird's nest on roof", "Heavy Coin Purse"),
        SekiroLocationData("MV: Light Coin Purse - hut across from Head Priest's house in bird's nest",
                           "Light Coin Purse"),
        SekiroLocationData("MV: Pellet - boat across pond", "Pellet", static="05,0:51500640::"),
        SekiroLocationData("MV: Scrap Magnetite - downstream from Mibu Village idol, enemy drop", "Scrap Magnetite",
                           drop=True),
        SekiroLocationData("MV: Treasure Carp Scale - underwater, near Water Mill idol, Carp drop",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        SekiroLocationData("MV: Breath of Life: Shadow - miniboss drop", "Breath of Life: Shadow", miniboss=True),
        SekiroLocationData("MV: Gourd Seed - main path, big tree bed center", "Gourd Seed"),
        SekiroLocationData("MV: Pine Resin Ember - Inuhiko's house, roof", "Pine Resin Ember"),
        SekiroLocationData("MV: Prayer Bead - miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("MV: Prayer Bead - Head Priest's house, second floor", "Prayer Bead"),
        SekiroLocationData("MV: Prayer Bead - underwater, pond chest", "Prayer Bead", conditional=True, diving=True),
        SekiroLocationData("MV: Red Carp Eyes - underwater, near the end of the pond, Carp drop", "Red Carp Eyes",
                           drop=True, conditional=True, diving=True),
    ],
    "Ashina Castle (Interior Ministry)": [
        # Remove the following two locations for Shura!
        SekiroLocationData("AC/I: Aromatic Branch - boss arena, boss drop", "Aromatic Branch", prominent=True,
                           progression=True, boss=True),
        SekiroLocationData("AC/I: Memory: Great Shinobi", "Memory: Great Shinobi", boss=True),
        # Fully commented locations should currently not be generated as they are unreachable in regular ending.
        # Keep for implementing Shura end, we currently inject these items so that they can be found.
        # SekiroLocationData("AC/I: Memory: Isshin Ashina", "Memory: Isshin Ashina", prominent=True, shura=True,
        # boss=True),
        # Missable if one does not have Rice for Kuro / does not give it to Kuro. Remove for Shura!
        SekiroLocationData("AC/I: Sweet Rice Ball - Kuro after incense and Rice for Kuro", "Sweet Rice Ball",
                           missable=True, npc=True, conditional=True),
        # Missable if not speaking to Kuro before second invasion. Remove for Shura!
        SekiroLocationData("AC/I: Divine Grass - Kuro after entering Fountainhead Palace", "Divine Grass",
                           missable=True, npc=True, conditional=True),
        # Missable by not doing the requirements before the second invasion. Remove for Shura!
        SekiroLocationData("AC/I: Father's Bell Charm - Emma after eavesdropping on her", "Father's Bell Charm",
                           progression=True, conditional=True, missable=True),
        # Missable by not doing the requirements before the second invasion, Remove for Shura!
        SekiroLocationData("AC/I: Tomoe's Note - Emma after eavesdropping on Kuro", "Tomoe's Note", npc=True,
                           missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AC/I: Pellet - end of bridge from AD", "Pellet x2", missable=True),
        SekiroLocationData("AC/I: Ceramic Shard - lake, bridge", "Ceramic Shard"),
        SekiroLocationData("AC/I: Adamantite Scrap - basement, passage to main stairway right", "Adamantite Scrap"),
        SekiroLocationData("AC/I: Pellet - upper tower, rafters", "Pellet x3"),
        SekiroLocationData("AC/I: Antidote Powder - secluded courtyard", "Antidote Powder"),
        SekiroLocationData("AC/I: Adamantite Scrap - upper tower, Ashina Dojo idol room", "Adamantite Scrap"),
        SekiroLocationData("AC/I: Adamantite Scrap - basement, central structure", "Adamantite Scrap"),
        SekiroLocationData("AC/I: Oil - basement, passage to main stairway left", "Oil x5"),
        SekiroLocationData("AC/I: Yashariku's Sugar - moat below Ashina Castle idol", "Yashariku's Sugar"),
        SekiroLocationData("AC/I: Pellet - Isshin's watchtower, balcony", "Pellet"),
        SekiroLocationData("AC/I: Black Scroll - Isshin's watchtower, chest", "Black Scroll"),
        SekiroLocationData("AC/I: Pellet - rooftop path, towards outskirts", "Pellet x2"),
        SekiroLocationData("AC/I: Scrap Magnetite - rooftop path, last roof", "Scrap Magnetite x2"),
        SekiroLocationData("AC/I: Yashariku's Sugar - gate from lake to serpent shrine",
                           "Yashariku's Sugar"),
        SekiroLocationData("AC/I: Dragon's Blood Droplet - serpent shrine, corpse", "Dragon's Blood Droplet"),
        SekiroLocationData("AC/I: Oil - main stairway", "Oil x2"),
        SekiroLocationData("AC/I: Oil - courtyard far right from Ashina Castle idol", "Oil x2"),
        SekiroLocationData("AC/I: Black Gunpowder - courtyard far right from Ashina Castle idol", "Black Gunpowder x3"),
        SekiroLocationData("AC/I: Lump of Fat Wax - Ashina Dojo, miniboss drop", "Lump of Fat Wax x2", miniboss=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AC/I: Yellow Gunpowder - serpent shrine, miniboss drop", "Yellow Gunpowder x2",
                           miniboss=True, missable=True),
        # Removed in the second invasion, therefore not missable in Shura
        SekiroLocationData("AC/I: Heavy Coin Purse - old grave, broken bridge, enemy drop", "Heavy Coin Purse",
                           drop=True, missable=True),
        SekiroLocationData("AC/I: Treasure Carp Scale - underwater, by Ashina Castle idol, Carp drop",
                           "Treasure Carp Scale", carp=True, conditional=True, diving=True),
        # SekiroLocationData("AC/I: One Mind - boss arena, boss drop", "One Mind", shura=True, boss=True),
        SekiroLocationData("AC/I: Shinobi Medicine Rank 3 - basement, miniboss drop", "Shinobi Medicine Rank 3",
                           miniboss=True),
        SekiroLocationData("AC/I: Prayer Bead - basement, miniboss drop", "Prayer Bead", static="02,0:6778::",
                           miniboss=True),
        SekiroLocationData("AC/I: Prayer Bead - Ashina Dojo, miniboss drop", "Prayer Bead", static="02,0:6779::",
                           miniboss=True),
        SekiroLocationData("AC/I: Prayer Bead - serpent shrine, miniboss drop", "Prayer Bead",
                           static="02,0:6780:9035,1100500:", miniboss=True, offering_box=True),
    ],
    "Hirata Estate (Father's Bell Charm)": [
        SekiroLocationData("HE2: Aromatic Flower - boss drop", "Aromatic Flower", prominent=True, boss=True),
        SekiroLocationData("HE2: Memory: Foster Father", "Memory: Foster Father", boss=True),
        SekiroLocationData("HE2: Fulminated Mercury - burning courtyard, after miniboss", "Fulminated Mercury"),
        SekiroLocationData("HE2: Adamantite Scrap - Main Hall, roof near three enemies", "Adamantite Scrap"),
        SekiroLocationData("HE2: Adamantite Scrap - Main Hall, tree at entrance to Audience Chamber",
                           "Adamantite Scrap"),
        SekiroLocationData("HE2: Fulminated Mercury - Audience Chamber, hallway to shinobi door", "Fulminated Mercury"),
        SekiroLocationData("HE2: Mibu Balloon of Wealth - Main Hall, open area before marsh",
                           "Mibu Balloon of Wealth x2"),
        SekiroLocationData("HE2: Fistful of Ash - Main Hall, corpse of Ashina Elite near miniboss", "Fistful of Ash"),
        SekiroLocationData("HE2: Light Coin Purse - Main Hall, left building after marsh", "Light Coin Purse"),
        SekiroLocationData("HE2: Ashina Sake - Main Hall, left building after marsh", "Ashina Sake"),
        SekiroLocationData("HE2: Pellet - Audience Chamber, room straight from entrance", "Pellet x3"),
        SekiroLocationData("HE2: Gokan's Sugar - Audience Chamber, left second room", "Gokan's Sugar x2"),
        SekiroLocationData("HE2: Adamantite Scrap - burning courtyard, miniboss drop", "Adamantite Scrap x2",
                           miniboss=True),
        SekiroLocationData("HE2: Prayer Bead - burning courtyard, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("HE2: Prayer Bead - Main Hall, miniboss drop", "Prayer Bead", miniboss=True),
    ],
    "Fountainhead Palace (before underwater progression)": [
        SekiroLocationData("FP1: Mask Fragment: Left - Pot Noble Koremori", "Mask Fragment: Left", shop=True),
        SekiroLocationData("FP1: Dragon's Blood Droplet - Pot Noble Koremori", "Dragon's Blood Droplet", shop=True),
        SekiroLocationData("FP1: Memory: True Monk", "Memory: True Monk", boss=True),
        # Missable as location may not work if the item is already given to the Great Carp
        SekiroLocationData("FP1: Truly Precious Bait - Pot Noble Koremori after 9 scales",
                           "Truly Precious Bait (Koremori)", npc=True, missable=True),
        SekiroLocationData("FP1: Mibu Balloon of Soul - first building after descent from Vermilion Bridge",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("FP1: Light Coin Purse - log left of first building", "Light Coin Purse"),
        SekiroLocationData("FP1: Mibu Balloon of Wealth - second building backside, room under overhang",
                           "Mibu Balloon of Wealth"),
        SekiroLocationData("FP1: Eel Liver - courtyard, behind bridge", "Eel Liver x2"),
        SekiroLocationData("FP1: Ungo's Sugar - courtyard, middle between trees", "Ungo's Sugar"),
        SekiroLocationData("FP1: Heavy Coin Purse - courtyard, middle between trees", "Heavy Coin Purse"),
        SekiroLocationData("FP1: Yashariku's Sugar - courtyard, tree left of door to idol", "Yashariku's Sugar x2"),
        SekiroLocationData("FP1: Treasure Carp Scale - Mibu Manor, dive in left corner before exit #1",
                           "Treasure Carp Scale", conditional=True, diving=True),
        SekiroLocationData("FP1: Bite Down - Mibu Manor, room with old woman", "Bite Down x2"),
        SekiroLocationData("FP1: Treasure Carp Scale - Mibu Manor, dive in left corner before exit #2",
                           "Treasure Carp Scale", conditional=True, diving=True),
        SekiroLocationData("FP1: Pellet - Mibu Manor, central open area under tree", "Pellet"),
        SekiroLocationData("FP1: Ako's Sugar - Mibu Manor, tree outside window at first enemy", "Ako's Sugar x3"),
        SekiroLocationData("FP1: Eel Liver - Mibu Manor, first house on left", "Eel Liver x3"),
        SekiroLocationData("FP1: Divine Confetti - Mibu Manor, far left corner", "Divine Confetti x2"),
        SekiroLocationData("FP1: Yellow Gunpowder - Mibu Manor, first left house dead end", "Yellow Gunpowder x4"),
        SekiroLocationData("FP1: Adamantite Scrap - Mibu Manor, room with chest", "Adamantite Scrap"),
        SekiroLocationData("FP1: Divine Grass - Mibu Manor, chest in room across water", "Divine Grass"),
        SekiroLocationData("FP1: Divine Confetti - behind pagoda at Flower Viewing Stage idol", "Divine Confetti x3"),
        SekiroLocationData("FP1: Adamantite Scrap - beside Mibu Manor, 3-item group", "Adamantite Scrap"),
        SekiroLocationData("FP1: Yashariku's Sugar - beside Mibu Manor, 3-item group", "Yashariku's Sugar x3"),
        SekiroLocationData("FP1: Bulging Coin Purse - beside Mibu Manor, 3-item group", "Bulging Coin Purse"),
        SekiroLocationData("FP1: Pellet - beside Mibu Manor, along wall", "Pellet x2"),
        SekiroLocationData("FP1: Mibu Balloon of Soul - past bridge, building across from bridge",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("FP1: Mibu Balloon of Soul - past bridge, underneath first platform",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("FP1: Ceramic Shard - past bridge, below platforms at water intersection",
                           "Ceramic Shard x3"),
        SekiroLocationData("FP1: Adamantite Scrap - roof of submerged building near Mibu Manor", "Adamantite Scrap"),
        SekiroLocationData("FP1: Light Coin Purse - past bridge, giant tree base, front", "Light Coin Purse"),
        SekiroLocationData("FP1: Heavy Coin Purse - past bridge, giant tree base, left", "Heavy Coin Purse"),
        SekiroLocationData("FP1: Bundled Jizo Statue - behind waterfall miniboss", "Bundled Jizo Statue"),
        SekiroLocationData("FP1: Eel Liver - past bridge, end of small stream left", "Eel Liver x2"),
        SekiroLocationData("FP1: Mibu Possession Balloon - by three enemies near waterfall miniboss #1",
                           "Mibu Possession Balloon"),
        SekiroLocationData("FP1: Mibu Possession Balloon - by three enemies near waterfall miniboss #2",
                           "Mibu Possession Balloon"),
        SekiroLocationData("FP1: Pellet - past bridge, left before stairs to Palace Grounds", "Pellet x2"),
        SekiroLocationData("FP1: Gokan's Sugar - past bridge, left-most high roof", "Gokan's Sugar x3"),
        SekiroLocationData("FP1: Divine Confetti - near Pot Noble Koremori", "Divine Confetti x2"),
        SekiroLocationData("FP1: Bulging Coin Purse - lower branch near Great Sakura miniboss", "Bulging Coin Purse"),
        SekiroLocationData("FP1: Treasure Carp Scale - Mibu Manor, dive in left corner before exit #3",
                           "Treasure Carp Scale", conditional=True, diving=True),
        SekiroLocationData("FP1: Adamantite Scrap - courtyard, inside left building", "Adamantite Scrap"),
        SekiroLocationData("FP1: Adamantite Scrap - inside building in middle of lake", "Adamantite Scrap"),
        SekiroLocationData("FP1: Pellet - Vermilion Bridge, behind collapsed strawman", "Pellet x2"),
        SekiroLocationData("FP1: Lump of Grave Wax - first bridge into water", "Lump of Grave Wax"),
        SekiroLocationData("FP1: Lump of Grave Wax - Mibu Manor, booth in house with rafters", "Lump of Grave Wax"),
        SekiroLocationData("FP1: Lump of Grave Wax - nearly submerged house roof in lake", "Lump of Grave Wax"),
        SekiroLocationData("FP1: Water of the Palace - Mibu Manor, dive in left corner before exit, chest",
                           "Water of the Palace", conditional=True, diving=True),
        SekiroLocationData("FP1: Ceramic Shard - bird's nest on wall before courtyard", "Ceramic Shard x3"),
        SekiroLocationData("FP1: Lapis Lazuli - past bridge, at waterfall, miniboss drop", "Lapis Lazuli",
                           miniboss=True),
        SekiroLocationData("FP1: Dragonspring Sake - before Great Sakura idol, enemy drop", "Dragonspring Sake",
                           drop=True),
        SekiroLocationData("FP1: A Beast's Karma - beside Mibu Manor, miniboss drop", "A Beast's Karma", miniboss=True),
        SekiroLocationData("FP1: Dragon's Tally Board - Vermilion Bridge, boss drop", "Dragon's Tally Board",
                           prominent=True, boss=True),
        SekiroLocationData("FP1: Prayer Bead - beside Mibu Manor, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("FP1: Prayer Bead - Great Sakura, miniboss drop", "Prayer Bead", miniboss=True),
    ],
    "Fountainhead Palace (underwater progression)": [
        SekiroLocationData("FP2: Divine Dragon's Tears - Sanctuary, boss drop", "Divine Dragon's Tears",
                           prominent=True, progression=True, boss=True),
        SekiroLocationData("FP2: Memory: Divine Dragon", "Memory: Divine Dragon", boss=True),
        SekiroLocationData("FP2: Treasure Carp Scale - Feeding Grounds, feed Great Carp once", "Treasure Carp Scale x3",
                           npc=True, conditional=True),
        SekiroLocationData("FP2: Treasure Carp Scale - Feeding Grounds, feed Great Carp twice", "Treasure Carp Scale",
                           npc=True, conditional=True),
        # Missable if one does not complete the Great Carp feeding quest
        SekiroLocationData("FP2: Divine Grass - Feeding Grounds, Attendant for Great White Whisker", "Divine Grass",
                           missable=True, npc=True, conditional=True),
        # Missable if Pot Noble Harunaga's bait is not fed to Great Carp
        SekiroLocationData("FP2: Lapis Lazuli - Koremori's pot after Truly Precious Bait", "Lapis Lazuli",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("FP2: Light Coin Purse - underwater, near Pot Noble Koremori", "Light Coin Purse"),
        SekiroLocationData("FP2: Scrap Magnetite - underwater, near Pot Noble Koremori", "Scrap Magnetite x3"),
        SekiroLocationData("FP2: Red Lump - underwater, right of demolished bridge", "Red Lump"),
        SekiroLocationData("FP2: Precious Bait - underwater, below Feeding Grounds", "Precious Bait"),
        SekiroLocationData("FP2: Ceramic Shard - underwater, entrance to Great Carp ravine", "Ceramic Shard x2"),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, inside house along right wall #1",
                           "Treasure Carp Scale"),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, inside house along right wall #2",
                           "Treasure Carp Scale"),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, inside house along right wall #3",
                           "Treasure Carp Scale"),
        SekiroLocationData("FP2: Precious Bait - underwater, building beneath Great Sakura miniboss", "Precious Bait"),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, giant skeleton near headless #1",
                           "Treasure Carp Scale"),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, giant skeleton near headless #2",
                           "Treasure Carp Scale"),
        SekiroLocationData("FP2: Precious Bait - underwater, log near headless", "Precious Bait"),
        SekiroLocationData("FP2: Light Coin Purse - underwater, near bottom of Great Carp ravine", "Light Coin Purse"),
        SekiroLocationData("FP2: Adamantite Scrap - underwater, further bottom of Great Carp ravine",
                           "Adamantite Scrap"),
        SekiroLocationData("FP2: Mibu Balloon of Soul - Palace Grounds, pool of water", "Mibu Balloon of Soul x3"),
        SekiroLocationData("FP2: Dragon's Blood Droplet - left of Sanctuary idol", "Dragon's Blood Droplet"),
        SekiroLocationData("FP2: Heavy Coin Purse - Feeding Grounds, bridge", "Heavy Coin Purse"),
        SekiroLocationData("FP2: Light Coin Purse - underwater, building overlooking headless", "Light Coin Purse"),
        SekiroLocationData("FP2: Lump of Grave Wax - underwater, building with Old Woman on roof", "Lump of Grave Wax"),
        SekiroLocationData("FP2: Ako's Sugar - Feeding Grounds, behind building in back corner", "Ako's Sugar x2",
                           hidden=True),
        SekiroLocationData("FP2: Ungo's Sugar - Feeding Grounds, up stairs from idol", "Ungo's Sugar x2"),
        SekiroLocationData("FP2: Yashariku's Spiritfall - underwater, headless drop", "Yashariku's Spiritfall",
                           miniboss=True, headless=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, further out from first bridge, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, near first bridge, Carp drop", "Treasure Carp Scale",
                           carp=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, beneath Feeding Grounds, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, right wall before building, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, near first house of area, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, under Sakura Branch, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("FP2: Treasure Carp Scale - underwater, middle of the lake, Carp drop",
                           "Treasure Carp Scale", carp=True),
        SekiroLocationData("FP2: Gourd Seed - Palace Grounds, chest", "Gourd Seed"),
        SekiroLocationData("FP2: Prayer Bead - underwater, chest near giant fish skeleton", "Prayer Bead"),
    ],
    "Ashina Castle (Central Forces)": [
        # Missable if Blackhat Badger's quest is not followed
        SekiroLocationData("AC/C: Mibu Pilgrimage Balloon - complete Blackhat Badger quest", "Mibu Pilgrimage Balloon",
                           missable=True),
        SekiroLocationData("AC/C: Secret Passage Key - Emma", "Secret Passage Key", npc=True, progression=True),
        SekiroLocationData("AC/C: Fistful of Ash - courtyard before Old Grave idol", "Fistful of Ash"),
        SekiroLocationData("AC/C: Ministry Dousing Powder - main stairway, middle", "Ministry Dousing Powder"),
        SekiroLocationData("AC/C: Ako's Sugar - area right of main stairway", "Ako's Sugar x3"),
        SekiroLocationData("AC/C: Fulminated Mercury - main stairway, alcove on right", "Fulminated Mercury"),
        SekiroLocationData("AC/C: Yashariku's Sugar - Isshin's dojo, near miniboss", "Yashariku's Sugar x2"),
        SekiroLocationData("AC/C: Pellet - upper tower, before stairs to Ashina Dojo", "Pellet x3"),
        SekiroLocationData("AC/C: Gokan's Sugar - courtyard left of Ashina Castle idol", "Gokan's Sugar x3"),
        SekiroLocationData("AC/C: Adamantite Scrap - main stairway, top", "Adamantite Scrap x2"),
        SekiroLocationData("AC/C: Adamantite Scrap - upper tower, map room", "Adamantite Scrap"),
        SekiroLocationData("AC/C: Bundled Jizo Statue - path to serpent shrine, enemy drop", "Bundled Jizo Statue",
                           drop=True),
        SekiroLocationData("AC/C: Prayer Bead - Isshin's dojo, miniboss drop", "Prayer Bead", miniboss=True),
    ],
    "Ashina Outskirts (Central Forces)": [
        # Missable if Kotaro was not sent to Anayama
        SekiroLocationData("AO/C: Promissory Note - Anayama the Peddler", "Promissory Note", missable=True, shop=True,
                           conditional=True),
        SekiroLocationData("AO/C: Lapis Lazuli - Flames of Hatred, boss drop", "Lapis Lazuli x2", boss=True),
        SekiroLocationData("AO/C: Memory: Hatred Demon", "Memory: Hatred Demon", prominent=True, boss=True),
        SekiroLocationData("AO/C: Adamantite Scrap - near headless warning sign", "Adamantite Scrap"),
        SekiroLocationData("AO/C: Adamantite Scrap - top of tower near Stairway idol", "Adamantite Scrap"),
        SekiroLocationData("AO/C: Adamantite Scrap - gate before stairs to Inosuke's house", "Adamantite Scrap"),
        SekiroLocationData("AO/C: Fulminated Mercury - explosive crates after lookout building", "Fulminated Mercury"),
        SekiroLocationData("AO/C: Fulminated Mercury - explosive crates at tower near destroyed house",
                           "Fulminated Mercury"),
        SekiroLocationData("AO/C: Lump of Grave Wax - stairs leading to Tengu tower", "Lump of Grave Wax"),
        SekiroLocationData("AO/C: Lump of Grave Wax - base of second tower on cliffside", "Lump of Grave Wax"),
        SekiroLocationData("AO/C: Ministry Dousing Powder - after crossing rebuilt bridge",
                           "Ministry Dousing Powder x2"),
        SekiroLocationData("AO/C: Gachiin's Sugar - lookout building, middle room", "Gachiin's Sugar x2"),
        SekiroLocationData("AO/C: Heavy Coin Purse - lookout building, right room", "Heavy Coin Purse"),
        SekiroLocationData("AO/C: Pellet - left from base of tower near Stairway idol", "Pellet x2"),
        SekiroLocationData("AO/C: Fistful of Ash - base of tower near Stairway idol", "Fistful of Ash x3"),
        SekiroLocationData("AO/C: Gachiin's Sugar - behind Anayama's first shop", "Gachiin's Sugar x3"),
        SekiroLocationData("AO/C: Ministry Dousing Powder - explosive crates after Inosuke's house",
                           "Ministry Dousing Powder x2"),
        SekiroLocationData("AO/C: Pellet - destroyed house, second floor", "Pellet x3"),
        SekiroLocationData("AO/C: Dragon's Blood Droplet - inside Tengu tower, ground floor", "Dragon's Blood Droplet"),
        SekiroLocationData("AO/C: Prayer Bead - courtyard before lookout building, miniboss drop", "Prayer Bead",
                           miniboss=True),
    ],
    "Ashina Reservoir (Central Forces)": [
        SekiroLocationData("AR/C: Memory: Saint Isshin", "Memory: Saint Isshin", prominent=True, boss=True,
                           conditional=True),
        SekiroLocationData("AR/C: Fulminated Mercury - behind miniboss against gate", "Fulminated Mercury"),
        SekiroLocationData("AR/C: Pellet - under bridge before Secret Passage", "Pellet x3"),
        SekiroLocationData("AR/C: Ministry Dousing Powder - tree near miniboss", "Ministry Dousing Powder x2"),
        SekiroLocationData("AR/C: Dragon Flash - final boss drop", "Dragon Flash", boss=True, conditional=True),
        SekiroLocationData("AR/C: Prayer Bead - miniboss drop", "Prayer Bead", miniboss=True),
    ],
}

location_name_groups: dict[str, set[str]] = {
    # We could insert these locations automatically with setdefault(), but we set them up explicitly
    # instead so we can choose the ordering.
    "Prominent": set(),
    "Progression": set(),
    "Prayer Beads": set(),
    "Boss Rewards": set(),
    "Miniboss Rewards": set(),
    "Headless": set(),
    "Drops": set(),
    "Friendly": set(),
    "Prosthetics": set(),
    "Esoteric Texts": set(),
    "Skills": set(),
    "Upgrade": set(),
    "Currency": set(),
    "Memories": set(),
    "Unique": set(),
    "Gourd Seeds": set(),
    "Miscellaneous": set(),
    "Hidden": set(),
    "Offering Box": set(),
}

location_descriptions = {
    "Prominent": "A small number of locations that are in very obvious locations. Mostly boss "
                 "drops. Ideal for setting as priority locations.",
    "Progression": "Locations that contain items in vanilla which unlock other locations.",
    "Prayer Beads": "Locations that contain Prayer Beads in vanilla.",
    "Gourd Seeds": "Locations that contain Gourd Seeds in vanilla.",
    "Boss Rewards": "Boss drops. Bosses are strong enemies that drop memories.",
    "Miniboss Rewards": "Miniboss drops. Minibosses are enemies with unique health bars that do not drop memories.",
    "Headless": "Headless miniboss drops. These locations contain the spiritfall items in vanilla",
    "Drops": "Drops from anything other than bosses, including minibosses, treasure carps, NPCs or normal enemies.",
    "Friendly": "Locations that contain items given by friendly NPCs as part of their quests or from "
                "non-violent interaction.",
    "Prosthetics": "Locations that contain a prosthetic tool unlock item in vanilla.",
    "Esoteric Texts": "Locations that contain an esoteric text item in vanilla.",
    "Skills": "Locations that contain skills found as item drops, such as "
              "Shinobi Medicine or Ninjutsu Techniques.",
    "Upgrade": "Locations that contain non-unique upgrade materials for prosthetic tools in vanilla.",
    "Currency": "Locations that contain coin pouches and treasure carp scales in vanilla.",
    "Memories": "Locations that contain memories in vanilla.",
    "Unique": "Locations that contain items which can be obtained once in a run, such as keys, notes, "
              "reusable items, prosthetics & unique upgrades.",
    "Miscellaneous": "Locations that contain generic stackable items in vanilla, such as sugars, "
                     "mibu balloons, resistance buffs and so on.",
    "Hidden": "Locations that are particularly difficult to find, such as in crawl spaces, "
              "down hidden drops, behind walls and so on.",
    "Offering Box": "Locations that contain items which move into the Offering Box after "
                    "becoming unavailable elsewhere."
}

location_dictionary: dict[str, SekiroLocationData] = {}
for location_name, location_table in location_tables.items():
    location_dictionary.update({location_data.name: location_data for location_data in location_table})

    for location_data in location_table:
        if not location_data.is_event:
            for group_name in location_data.location_groups():
                location_name_groups[group_name].add(location_data.name)

    # Allow entire locations to be added to location sets.
    if not location_name.endswith(" Shop"):
        location_name_groups[location_name] = set([
            location_data.name for location_data in location_table
            if not location_data.is_event
        ])

location_name_groups["Fountainhead Palace"] = (
    location_name_groups["Fountainhead Palace (before underwater progression)"]
    .union(location_name_groups["Fountainhead Palace (underwater progression)"])
)
del location_name_groups["Fountainhead Palace (before underwater progression)"]
del location_name_groups["Fountainhead Palace (underwater progression)"]
