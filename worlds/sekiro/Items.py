import dataclasses
from collections.abc import Generator
from dataclasses import dataclass
from enum import IntEnum
from typing import ClassVar

from BaseClasses import Item, ItemClassification


class SekiroItemCategory(IntEnum):
    ESOTERIC_TEXTS = 0
    SKILLS = 1
    HEALING = 2
    INCENSE = 3
    MEMORIES = 4
    MISC = 5
    CURRENCY = 6
    UNIQUE = 7
    UPGRADE = 8


@dataclass
class SekiroItemData:
    __item_id: ClassVar[int] = 100000
    """The next item ID to use when creating item data."""

    name: str
    sekiro_code: int | None
    category: SekiroItemCategory

    base_name: str | None = None
    """The name of the individual item, if this is a multi-item group."""

    classification: ItemClassification = ItemClassification.filler
    """How important this item is to the game progression."""

    ap_code: int | None = None
    """The Archipelago ID for this item."""

    count: int = 1
    """The number of copies of this item included in each drop."""

    inject: bool = False
    """If this is set, the randomizer will try to inject this item into the game.

    This is used for items such as covenant rewards that aren't realistically reachable in a
    randomizer run, but are still fun to have available to the player. If there are more locations
    available than there are items in the item pool, these items will be used to help make up the
    difference.
    """

    filler: bool = False
    """Whether this is a candidate for a filler item to be added to fill out extra locations."""

    skip: bool = False
    """Whether to omit this item from randomization and replace it with filler or unique items."""

    @property
    def unique(self):
        """Whether this item should be unique, appearing only once in the randomizer."""
        return self.category not in {
            SekiroItemCategory.MISC, SekiroItemCategory.CURRENCY, SekiroItemCategory.UPGRADE,
            SekiroItemCategory.HEALING,
        }

    def __post_init__(self):
        self.ap_code = self.ap_code or SekiroItemData.__item_id
        if not self.base_name: self.base_name = self.name
        SekiroItemData.__item_id += 1

    def item_groups(self) -> list[str]:
        """The names of item groups this item should appear in.

        This is computed from the properties assigned to this item."""
        names = []
        if self.classification == ItemClassification.progression: names.append("Progression")
        if self.category == SekiroItemCategory.INCENSE: names.append("Unique")
        names.append({
                         SekiroItemCategory.ESOTERIC_TEXTS: "Esoteric Texts",
                         SekiroItemCategory.SKILLS: "Skills",
                         SekiroItemCategory.MISC: "Miscellaneous",
                         SekiroItemCategory.INCENSE: "Incense",
                         SekiroItemCategory.UNIQUE: "Unique",
                         SekiroItemCategory.MEMORIES: "Memories",
                         SekiroItemCategory.CURRENCY: "Currency",
                         SekiroItemCategory.UPGRADE: "Upgrade",
                         SekiroItemCategory.HEALING: "Healing",
                     }[self.category])
        return names

    def counts(self, counts: list[int]) -> Generator["SekiroItemData", None, None]:
        """Returns an iterable of copies of this item with the given counts."""
        yield self
        for count in counts:
            yield dataclasses.replace(
                self,
                ap_code = None,
                name = f"{self.base_name} x{count}",
                base_name = self.base_name,
                count = count,
                filler = False, # Don't count multiples as filler by default
            )

class SekiroItem(Item):
    game: str = "Sekiro: Shadows Die Twice"
    data: SekiroItemData

    def __init__(
            self,
            player: int,
            data: SekiroItemData,
            classification = None):
        super().__init__(data.name, classification or data.classification, data.ap_code, player)
        self.data = data

    @staticmethod
    def event(name: str, player: int) -> "SekiroItem":
        data = SekiroItemData(name, None, SekiroItemCategory.MISC,
                              skip = True, classification = ItemClassification.progression)
        data.ap_code = None
        return SekiroItem(player, data)


_all_items = [
    # Currency
    SekiroItemData("Light Coin Purse", 0x40000E74, SekiroItemCategory.CURRENCY, filler = True),
    SekiroItemData("Heavy Coin Purse", 0x40000E78, SekiroItemCategory.CURRENCY),
    SekiroItemData("Bulging Coin Purse", 0x40000E7C, SekiroItemCategory.CURRENCY,
                   classification = ItemClassification.useful),
    *SekiroItemData("Treasure Carp Scale", 0x40002710, SekiroItemCategory.CURRENCY,
                    classification = ItemClassification.useful).counts([3, 5]),

    # Esoteric Texts
    SekiroItemData("Shinobi Esoteric Text", 0x40000B68, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),
    SekiroItemData("Prosthetic Esoteric Text", 0x40000B69, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),
    SekiroItemData("Ashina Esoteric Text", 0x40000B6A, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),
    SekiroItemData("Senpou Esoteric Text", 0x40000B6B, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),

    # Healing
    SekiroItemData("Prayer Bead", 0x40000FA0, SekiroItemCategory.HEALING,
                   classification = ItemClassification.useful),
    SekiroItemData("Gourd Seed", 0x40001130, SekiroItemCategory.HEALING,
                   classification = ItemClassification.useful),

    # Incense
    SekiroItemData("Lotus of the Palace", 0x400009C4, SekiroItemCategory.INCENSE,
                   classification = ItemClassification.progression),
    SekiroItemData("Shelter Stone", 0x400009C5, SekiroItemCategory.INCENSE,
                   classification = ItemClassification.progression),
    SekiroItemData("Aromatic Branch", 0x400009C6, SekiroItemCategory.INCENSE,
                   classification = ItemClassification.progression),
    SekiroItemData("Mortal Blade", 0x40000960, SekiroItemCategory.INCENSE,
                   classification=ItemClassification.progression),

    # Memories
    SekiroItemData("Memory: Gyoubu Oniwa", 0x40001450, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Lady Butterfly", 0x40001451, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Genichiro", 0x40001452, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Screen Monkeys", 0x40001453, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Guardian Ape", 0x40001454, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Corrupted Monk", 0x40001455, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Great Shinobi", 0x40001456, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Foster Father", 0x40001457, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: True Monk", 0x40001458, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Divine Dragon", 0x40001459, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Hatred Demon", 0x4000145A, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Saint Isshin", 0x4000145B, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    #For now injected as unreachable in regular ending.
    # redo when implementing alternate ending for Shura
    SekiroItemData("Memory: Isshin Ashina", 0x4000145C, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Memory: Headless Ape", 0x4000145D, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),

    # Misc
    *SekiroItemData("Pellet", 0x40000BCC, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    SekiroItemData("Divine Grass", 0x40000BE0, SekiroItemCategory.MISC),
    *SekiroItemData("Red Lump", 0x40000BEA, SekiroItemCategory.MISC).counts([2]),
    SekiroItemData("Sweet Rice Ball x2", 0x40000BF4, SekiroItemCategory.MISC, count = 2),
    SekiroItemData("Persimmon", 0x40000BFE, SekiroItemCategory.MISC, classification = ItemClassification.progression),
    SekiroItemData("Rice", 0x40000C08, SekiroItemCategory.MISC, classification = ItemClassification.progression),
    SekiroItemData("Fine Snow", 0x40000C09, SekiroItemCategory.MISC, skip = True),
    *SekiroItemData("Antidote Powder", 0x40000C80, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Dousing Powder", 0x40000C8A, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Ministry Dousing Powder", 0x40000C8B, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Pacifying Agent", 0x40000C94, SekiroItemCategory.MISC).counts([2, 3, 5]),
    *SekiroItemData("Eel Liver", 0x40000C9E, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Contact Medicine", 0x40000CB2, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Bite Down", 0x40000CDA, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Ako's Sugar", 0x40000D48, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Yashariku's Sugar", 0x40000D52, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Ungo's Sugar", 0x40000D5C, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Gokan's Sugar", 0x40000D66, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Gachiin's Sugar", 0x40000D70, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Divine Confetti", 0x40000D7A, SekiroItemCategory.MISC,
                    classification = ItemClassification.useful).counts([2, 3, 5]),
    *SekiroItemData("Ceramic Shard", 0x40000DAC, SekiroItemCategory.MISC, filler = True).counts([2, 3, 4]),
    *SekiroItemData("Fistful of Ash", 0x40000DB6, SekiroItemCategory.MISC, filler = True).counts([2, 3, 5]),
    *SekiroItemData("Oil", 0x40000DC0, SekiroItemCategory.MISC, filler = True).counts([2, 3, 5]),
    *SekiroItemData("Snap Seed", 0x40000DCA, SekiroItemCategory.MISC).counts([2, 3, 5]),
    *SekiroItemData("Mibu Balloon of Wealth", 0x40000E10, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Mibu Balloon of Soul", 0x40000E1A, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Mibu Possession Balloon", 0x40000E24, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Mibu Balloon of Spirit", 0x40000E2E, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    SekiroItemData("Bundled Jizo Statue", 0x40000E88, SekiroItemCategory.MISC,
                   classification = ItemClassification.useful),
    SekiroItemData("Dragon's Blood Droplet", 0x400015E0, SekiroItemCategory.MISC,
                   classification = ItemClassification.useful),
    SekiroItemData("Ashina Sake", 0x4000238C, SekiroItemCategory.MISC, skip=True),
    SekiroItemData("Unrefined Sake", 0x4000238D, SekiroItemCategory.MISC, skip=True),
    SekiroItemData("Monkey Booze", 0x4000238E, SekiroItemCategory.MISC, skip=True),
    SekiroItemData("Dragonspring Sake", 0x4000238F, SekiroItemCategory.MISC, skip=True),
    SekiroItemData("Precious Bait", 0x400023DC, SekiroItemCategory.MISC,
                   classification = ItemClassification.progression),

    # Skills
    SekiroItemData("Bloodsmoke Ninjutsu", 0x40000834, SekiroItemCategory.SKILLS),
    SekiroItemData("Puppeteer Ninjutsu", 0x4000083E, SekiroItemCategory.SKILLS,
                   classification=ItemClassification.progression),
    SekiroItemData("Bestowal Ninjutsu", 0x40000848, SekiroItemCategory.SKILLS),
    SekiroItemData("Mibu Breathing Technique", 0x40000974, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.progression),
    SekiroItemData("Anti-air Deathblow Text", 0x40000992, SekiroItemCategory.SKILLS),
    SekiroItemData("Dragon Flash", 0x4000099C, SekiroItemCategory.SKILLS),
    SekiroItemData("Shinobi Medicine Rank 1", 0x400009A6, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Floating Passage Text", 0x4000099D, SekiroItemCategory.SKILLS),
    SekiroItemData("Shinobi Medicine Rank 2", 0x400009A7, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    # For now injected as unreachable in regular ending.
    # redo when implementing alternate ending for Shura
    SekiroItemData("One Mind", 0x4000099E, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shinobi Medicine Rank 3", 0x400009A8, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("A Beast's Karma", 0x400009AB, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Breath of Life: Shadow", 0x400009B0, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Breath of Nature: Shadow", 0x400009B1, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),

    # Unique
    SekiroItemData("Shinobi Prosthetic", 0x40000906, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Aromatic Flower", 0x400009C7, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mechanical Barrel", 0x40000B5E, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Sweet Rice Ball", 0x40000BF5, SekiroItemCategory.UNIQUE),
    SekiroItemData("Taro Persimmon", 0x40000BFF, SekiroItemCategory.UNIQUE, inject = True),
    SekiroItemData("Green Mossy Gourd", 0x40000CE4, SekiroItemCategory.UNIQUE),
    SekiroItemData("Withered Red Gourd", 0x40000CEE, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mottled Purple Gourd", 0x40000CF8, SekiroItemCategory.UNIQUE),
    SekiroItemData("Ako's Spiritfall", 0x40000D16, SekiroItemCategory.UNIQUE),
    SekiroItemData("Yashariku's Spiritfall", 0x40000D20, SekiroItemCategory.UNIQUE),
    SekiroItemData("Ungo's Spiritfall", 0x40000D2A, SekiroItemCategory.UNIQUE),
    SekiroItemData("Gokan's Spiritfall", 0x40000D34, SekiroItemCategory.UNIQUE),
    SekiroItemData("Gachiin's Spiritfall", 0x40000D3E, SekiroItemCategory.UNIQUE),
    SekiroItemData("Five-color Rice", 0x40000DFC, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mibu Pilgrimage Balloon", 0x40000E38, SekiroItemCategory.UNIQUE),
    #Inject as it is currently out of logic as a quest reward
    SekiroItemData("Jinza's Jizo Statue", 0x40000E89, SekiroItemCategory.UNIQUE, inject = True),
    SekiroItemData("Ceremonial Tanto", 0x40000ED8, SekiroItemCategory.UNIQUE),
    SekiroItemData("Nightjar Monocular", 0x40000F3C, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mask Fragment: Right", 0x4000157C, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mask Fragment: Left", 0x4000157D, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mask Fragment: Dragon", 0x4000157E, SekiroItemCategory.UNIQUE),
    SekiroItemData("Divine Dragon's Tears", 0x40002328, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Sakura Droplet", 0x40002331, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Young Lord's Bell Charm", 0x40002332, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Father's Bell Charm", 0x40002333, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Ornamental Letter", 0x4000233C, SekiroItemCategory.UNIQUE),
    SekiroItemData("Red Carp Eyes", 0x4000235C, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Dragon's Tally Board", 0x40002364, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Promissory Note", 0x40002365, SekiroItemCategory.UNIQUE),
    SekiroItemData("Water of the Palace", 0x4000236E, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Great White Whisker", 0x4000236F, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Red and White Pinwheel", 0x40002378, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    #Skip this to force Kotaro to go to quest, as we do not generate the Kotaro Senpou quest items
    SekiroItemData("White Pinwheel", 0x40002379, SekiroItemCategory.UNIQUE, skip = True),
                   #classification = ItemClassification.progression,
    SekiroItemData("Rice for Kuro", 0x40002382, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Frozen Tears", 0x40002383, SekiroItemCategory.UNIQUE),
    SekiroItemData("Truly Precious Bait (Harunaga)", 0x400023DD, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Truly Precious Bait (Koremori)", 0x400023DE, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Fresh Serpent Viscera", 0x400023E8, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Dried Serpent Viscera", 0x400023E9, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Herb Catalogue Scrap", 0x400023F0, SekiroItemCategory.UNIQUE),
    SekiroItemData("Dosaku's Note", 0x400023F5, SekiroItemCategory.UNIQUE),
    SekiroItemData("Rat Description", 0x400023F6, SekiroItemCategory.UNIQUE),
    SekiroItemData("Surgeon's Bloody Letter", 0x400023F7, SekiroItemCategory.UNIQUE),
    SekiroItemData("Surgeon's Stained Letter", 0x400023F8, SekiroItemCategory.UNIQUE),
    SekiroItemData("Holy Chapter: Dragon's Return", 0x400023F9, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Immortal Severance Text", 0x400023FA, SekiroItemCategory.UNIQUE),
    SekiroItemData("Immortal Severance Scrap", 0x400023FB, SekiroItemCategory.UNIQUE),
    SekiroItemData("Fragrant Flower Note", 0x400023FC, SekiroItemCategory.UNIQUE),
    SekiroItemData("Okami's Ancient Text", 0x400023FD, SekiroItemCategory.UNIQUE),
    SekiroItemData("Page's Diary", 0x400023FE, SekiroItemCategory.UNIQUE),
    SekiroItemData("Holy Chapter: Infested", 0x400023FF, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Tomoe's Note", 0x40002400, SekiroItemCategory.UNIQUE),
    SekiroItemData("Flame Barrel Memo", 0x40002401, SekiroItemCategory.UNIQUE),
    SekiroItemData("Nightjar Beacon Memo", 0x40002402, SekiroItemCategory.UNIQUE),
    SekiroItemData("Isshin's Letter", 0x40002403, SekiroItemCategory.UNIQUE),
    SekiroItemData("Rotting Prisoner's Note", 0x40002404, SekiroItemCategory.UNIQUE),
    SekiroItemData("Sabimaru Memo", 0x40002405, SekiroItemCategory.UNIQUE),
    SekiroItemData("Valley Apparitions Memo", 0x40002407, SekiroItemCategory.UNIQUE),
    SekiroItemData("Three-story Pagoda Memo", 0x40002409, SekiroItemCategory.UNIQUE),
    SekiroItemData("Academics' Red Lump", 0x40000BED, SekiroItemCategory.UNIQUE),
    SekiroItemData("Hidden Tooth", 0x40000CDB, SekiroItemCategory.UNIQUE),
    SekiroItemData("Black Scroll", 0x4000240B, SekiroItemCategory.UNIQUE),
    SekiroItemData("Gatehouse Key", 0x400024BA, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Hidden Temple Key", 0x400024BB, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Secret Passage Key", 0x400024BC, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Gun Fort Shrine Key", 0x400024BD, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Shuriken Wheel", 0x400025E4, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Phantom Kunai", 0x400025E5, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Robert's Firecrackers", 0x400025EE, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    #Mark as progression if we implement it being there for Anayama
    SekiroItemData("Flame Barrel", 0x400025F8, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Pine Resin Ember", 0x400025F9, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Shinobi Axe of the Monkey", 0x40002602, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Mist Raven's Feathers", 0x4000260C, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Sabimaru", 0x40002616, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Iron Fortress", 0x40002620, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Large Fan", 0x4000262A, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Gyoubu's Broken Horn", 0x40002634, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Slender Finger", 0x4000263E, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Malcontent's Ring", 0x4000263F, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),


    # Upgrade
    *SekiroItemData("Scrap Iron", 0x40001770, SekiroItemCategory.UPGRADE, filler=True).counts([2, 3, 5]),
    *SekiroItemData("Scrap Magnetite", 0x4000177A, SekiroItemCategory.UPGRADE, filler=True).counts([2, 3]),
    *SekiroItemData("Adamantite Scrap", 0x40001784, SekiroItemCategory.UPGRADE, filler=True).counts([2]),
    *SekiroItemData("Black Gunpowder", 0x400017D4, SekiroItemCategory.UPGRADE, filler = True).counts([2, 3]),
    *SekiroItemData("Yellow Gunpowder", 0x40001838, SekiroItemCategory.UPGRADE, filler = True).counts([2, 3, 4]),
    SekiroItemData("Fulminated Mercury", 0x40001842, SekiroItemCategory.UPGRADE),
    *SekiroItemData("Lump of Fat Wax", 0x4000189C, SekiroItemCategory.UPGRADE).counts([2, 3]),
    *SekiroItemData("Lump of Grave Wax", 0x400018A6, SekiroItemCategory.UPGRADE).counts([2]),
    *SekiroItemData("Lapis Lazuli", 0x40001900, SekiroItemCategory.UPGRADE).counts([2]),

]

_skills_as_pickup = [
    # Skills usually obtained via Skill Tree. Keep for implementing option to also have them as item pickups.
    # This will have to be some sort of event pickup, as they have no actual item IDs.
    # Therefore, these are currently unused.
    SekiroItemData("Grappling Hook Attack", 0x00030D40, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Mid-air Deflection", 0x00030DA4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Mid-air Prosthetic Tool", 0x00030E08, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Mikiri Counter", 0x00030E6C, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Run and Slide", 0x00030ED0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Mid-air Combat Arts", 0x00030F34, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Vault Over", 0x00030F98, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Whirlwind Slash", 0x00033450, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shadowrush", 0x00033838, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Chasing Slice", 0x000497C8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Fang and Blade", 0x0004982C, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Projected Force", 0x00049890, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Living Force", 0x000498F4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Nightjar Slash", 0x0004BAF0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Nightjar Slash Reversal", 0x0004BB54, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ichimonji", 0x00064190, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ichimonji: Double", 0x000641F4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ashina Cross", 0x000645D8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Praying Strikes", 0x0007C7B0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Praying Strikes - Exorcism", 0x0007C814, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Senpou Leaping Kicks", 0x0007CBF8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("High Monk", 0x0007CC5C, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shadowfall", 0x00095114, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Spiral Cloud Passage", 0x000954FC, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Empowered Mortal Draw", 0x000959E4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Suppress Presence", 0x000974A0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Suppress Sound", 0x00097504, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Virtuous Deed", 0x00098160, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Most Virtuous Deed", 0x000981C4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Emma's Medicine: Potency", 0x0009C400, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Emma's Medicine: Aroma", 0x0009C464, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("A Shinobi's Karma: Body", 0x0009E848, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("A Shinobi's Karma: Mind", 0x0009E8AC, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Sculptor's Karma: Blood", 0x0009E910, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Sculptor's Karma: Scars", 0x0009E974, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Breath of Life: Light", 0x000A1310, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Breath of Nature: Light", 0x000A13D8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shinobi Eyes", 0x000A14A0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Devotion", 0x000A1504, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ascending Carp", 0x000A1568, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Descending Carp", 0x000A15CC, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Flowing Water", 0x000A1630, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
]

item_name_groups: dict[str, set] = {
    "Esoteric Texts": set(),
    "Progression": set(),
    "Incense": set(),
    "Skills": set(),
    "Miscellaneous": set(),
    "Unique": set(),
    "Memories": set(),
    "Currency": set(),
    "Upgrade": set(),
    "Healing": set(),
}


item_descriptions = {
    "Progression": "Items that unlock locations.",
    "Incense": "Ingredients required for the incense to access the Fountainhead Palace.",
    "Memories": "Items dropped by major bosses to increase Attack Power.",
    "Healing": "Gourd Seeds and Prayer Beads.",
    "Esoteric Texts": "Items that unlock skill trees.",
    "Skills": "Skills obtained as Items, such as Shinobi Medicine and Ninjutsu Techniques.",
    "Unique": "Items that can be obtained once in a run, such as keys, notes, reusable items, prosthetics "
              "& unique upgrades. Doesn't include Skill Texts or Skills.",
    "Currency": "Coin Purses and Treasure Carp Scales.",
    "Upgrade": "Non-unique materials to upgrade prosthetic tools.",
    "Miscellaneous": "Generic stackable items, such as sugars, mibu balloons, resistance buffs and so on.",
}

for item_data in _all_items:
    for group_name in item_data.item_groups():
        item_name_groups[group_name].add(item_data.name)

filler_item_names = [item_data.name for item_data in _all_items if item_data.filler]
item_dictionary = {item_data.name: item_data for item_data in _all_items}
