# In almost all cases, we leave boss and enemy randomization up to the static randomizer.
# Edge cases may be necessary for Shichimen or similar, so keep this for now.
# If no edge cases, remove this file and all references from init as it is not needed.

from dataclasses import dataclass, field


@dataclass
class SekiroBossInfo:
    """The set of locations a given boss location blocks access to."""

    name: str
    """The boss's name."""

    id: int
    """The game's ID for this particular boss."""

    locations: set[str] = field(default_factory=set)
    """Additional individual locations that can't be accessed until the boss is dead."""


# Note: the static randomizer splits up some bosses into separate fights for separate phases, each
# of which can be individually replaced by Yhorm.
all_bosses = [
    SekiroBossInfo("Iudex Gundyr", 4000800, locations = {
        "CA: Coiled Sword - boss drop"
    }),
    SekiroBossInfo("Vordt of the Boreal Valley", 3000800, locations = {
        "HWL: Soul of Boreal Valley Vordt"
    }),
    SekiroBossInfo("Curse-rotted Greatwood", 3100800, locations = {
        "US: Soul of the Rotted Greatwood",
        "US: Transposing Kiln - boss drop",
        "US: Wargod Wooden Shield - Pit of Hollows",
        "FS: Hawkwood's Shield - gravestone after Hawkwood leaves",
        "FS: Sunset Shield - by grave after killing Hodrick w/Sirris",
        "US: Sunset Helm - Pit of Hollows after killing Hodrick w/Sirris",
        "US: Sunset Armor - pit of hollows after killing Hodrick w/Sirris",
        "US: Sunset Gauntlets - pit of hollows after killing Hodrick w/Sirris",
        "US: Sunset Leggings - pit of hollows after killing Hodrick w/Sirris",
        "FS: Sunless Talisman - Sirris, kill GA boss",
        "FS: Sunless Veil - shop, Sirris quest, kill GA boss",
        "FS: Sunless Armor - shop, Sirris quest, kill GA boss",
        "FS: Sunless Gauntlets - shop, Sirris quest, kill GA boss",
        "FS: Sunless Leggings - shop, Sirris quest, kill GA boss",
    }),
    SekiroBossInfo("Crystal Sage", 3300850, locations = {
        "RS: Soul of a Crystal Sage",
        "FS: Sage's Big Hat - shop after killing RS boss",
        "FS: Hawkwood's Shield - gravestone after Hawkwood leaves",
    }),
    SekiroBossInfo("Deacons of the Deep", 3500800, locations = {
        "CD: Soul of the Deacons of the Deep",
        "CD: Small Doll - boss drop",
        "CD: Archdeacon White Crown - boss room after killing boss",
        "CD: Archdeacon Holy Garb - boss room after killing boss",
        "CD: Archdeacon Skirt - boss room after killing boss",
        "FS: Hawkwood's Shield - gravestone after Hawkwood leaves",
    }),
    SekiroBossInfo("Abyss Watchers", 3300801, locations = {
        "FK: Soul of the Blood of the Wolf",
        "FK: Cinders of a Lord - Abyss Watcher",
        "FS: Undead Legion Helm - shop after killing FK boss",
        "FS: Undead Legion Armor - shop after killing FK boss",
        "FS: Undead Legion Gauntlet - shop after killing FK boss",
        "FS: Undead Legion Leggings - shop after killing FK boss",
        "FS: Farron Ring - Hawkwood",
        "FS: Hawkwood's Shield - gravestone after Hawkwood leaves",
    }),
    SekiroBossInfo("High Lord Wolnir", 3800800, locations = {
        "CC: Soul of High Lord Wolnir",
        "FS: Wolnir's Crown - shop after killing CC boss",
        "CC: Homeward Bone - Irithyll bridge",
        "CC: Pontiff's Right Eye - Irithyll bridge, miniboss drop",
    }),
    SekiroBossInfo("Pontiff Sulyvahn", 3700850, locations = {
        "IBV: Soul of Pontiff Sulyvahn",
    }),
    SekiroBossInfo("Old Demon King", 3800830, locations = {
        "SL: Soul of the Old Demon King",
    }),
    SekiroBossInfo("Aldrich, Devourer of Gods", 3700800, locations = {
        "AL: Soul of Aldrich",
        "AL: Cinders of a Lord - Aldrich",
        "FS: Smough's Helm - shop after killing AL boss",
        "FS: Smough's Armor - shop after killing AL boss",
        "FS: Smough's Gauntlets - shop after killing AL boss",
        "FS: Smough's Leggings - shop after killing AL boss",
        "AL: Sun Princess Ring - dark cathedral, after boss",
        "FS: Leonhard's Garb - shop after killing Leonhard",
        "FS: Leonhard's Gauntlets - shop after killing Leonhard",
        "FS: Leonhard's Trousers - shop after killing Leonhard",
    }),
    SekiroBossInfo("Dancer of the Boreal Valley", 3000899, locations = {
        "HWL: Soul of the Dancer",
        "FS: Dancer's Crown - shop after killing LC entry boss",
        "FS: Dancer's Armor - shop after killing LC entry boss",
        "FS: Dancer's Gauntlets - shop after killing LC entry boss",
        "FS: Dancer's Leggings - shop after killing LC entry boss",
    }),
    SekiroBossInfo("Dragonslayer Armour", 3010800, locations = {
        "LC: Soul of Dragonslayer Armour",
        "FS: Morne's Helm - shop after killing Eygon or LC boss",
        "FS: Morne's Armor - shop after killing Eygon or LC boss",
        "FS: Morne's Gauntlets - shop after killing Eygon or LC boss",
        "FS: Morne's Leggings - shop after killing Eygon or LC boss",
        "LC: Titanite Chunk - down stairs after boss",
    }),
    SekiroBossInfo("Consumed King Oceiros", 3000830, locations = {
        "CKG: Soul of Consumed Oceiros",
        "CKG: Titanite Scale - tomb, chest #1",
        "CKG: Titanite Scale - tomb, chest #2",
        "CKG: Drakeblood Helm - tomb, after killing AP mausoleum NPC",
        "CKG: Drakeblood Armor - tomb, after killing AP mausoleum NPC",
        "CKG: Drakeblood Gauntlets - tomb, after killing AP mausoleum NPC",
        "CKG: Drakeblood Leggings - tomb, after killing AP mausoleum NPC",
    }),
    SekiroBossInfo("Champion Gundyr", 4000830, locations = {
        "UG: Soul of Champion Gundyr",
        "FS: Gundyr's Helm - shop after killing UG boss",
        "FS: Gundyr's Armor - shop after killing UG boss",
        "FS: Gundyr's Gauntlets - shop after killing UG boss",
        "FS: Gundyr's Leggings - shop after killing UG boss",
        "UG: Hornet Ring - environs, right of main path after killing FK boss",
        "UG: Chaos Blade - environs, left of shrine",
        "UG: Blacksmith Hammer - shrine, Andre's room",
        "UG: Eyes of a Fire Keeper - shrine, Irina's room",
        "UG: Coiled Sword Fragment - shrine, dead bonfire",
        "UG: Soul of a Crestfallen Knight - environs, above shrine entrance",
        "UG: Life Ring+3 - shrine, behind big throne",
        "UG: Ring of Steel Protection+1 - environs, behind bell tower",
        "FS: Ring of Sacrifice - Yuria shop",
        "UG: Ember - shop",
        "UG: Priestess Ring - shop",
        "UG: Wolf Knight Helm - shop after killing FK boss",
        "UG: Wolf Knight Armor - shop after killing FK boss",
        "UG: Wolf Knight Gauntlets - shop after killing FK boss",
        "UG: Wolf Knight Leggings - shop after killing FK boss",
    }),
    SekiroBossInfo("Ancient Wyvern", 3200800),
    SekiroBossInfo("King of the Storm", 3200850, locations = {
        "AP: Soul of the Nameless King",
        "FS: Golden Crown - shop after killing AP boss",
        "FS: Dragonscale Armor - shop after killing AP boss",
        "FS: Golden Bracelets - shop after killing AP boss",
        "FS: Dragonscale Waistcloth - shop after killing AP boss",
        "AP: Titanite Slab - plaza",
        "AP: Covetous Gold Serpent Ring+2 - plaza",
        "AP: Dragonslayer Helm - plaza",
        "AP: Dragonslayer Armor - plaza",
        "AP: Dragonslayer Gauntlets - plaza",
        "AP: Dragonslayer Leggings - plaza",
    }),
    SekiroBossInfo("Nameless King", 3200851, locations = {
        "AP: Soul of the Nameless King",
        "FS: Golden Crown - shop after killing AP boss",
        "FS: Dragonscale Armor - shop after killing AP boss",
        "FS: Golden Bracelets - shop after killing AP boss",
        "FS: Dragonscale Waistcloth - shop after killing AP boss",
        "AP: Titanite Slab - plaza",
        "AP: Covetous Gold Serpent Ring+2 - plaza",
        "AP: Dragonslayer Helm - plaza",
        "AP: Dragonslayer Armor - plaza",
        "AP: Dragonslayer Gauntlets - plaza",
        "AP: Dragonslayer Leggings - plaza",
    }),
    SekiroBossInfo("Lothric, Younger Prince", 3410830, locations = {
        "GA: Soul of the Twin Princes",
        "GA: Cinders of a Lord - Lothric Prince",
    }),
    SekiroBossInfo("Lorian, Elder Prince", 3410832, locations = {
        "GA: Soul of the Twin Princes",
        "GA: Cinders of a Lord - Lothric Prince",
        "FS: Lorian's Helm - shop after killing GA boss",
        "FS: Lorian's Armor - shop after killing GA boss",
        "FS: Lorian's Gauntlets - shop after killing GA boss",
        "FS: Lorian's Leggings - shop after killing GA boss",
    })
]

default_yhorm_location = SekiroBossInfo("Yhorm the Giant", 3900800, locations = {
    "PC: Soul of Yhorm the Giant",
    "PC: Cinders of a Lord - Yhorm the Giant",
    "PC: Siegbräu - Siegward after killing boss",
})
