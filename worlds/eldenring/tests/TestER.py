from test.bases import WorldTestBase

from worlds.eldenring.items import item_table
from worlds.eldenring.locations import location_tables, region_order

class EldenRingTest(WorldTestBase):
    game = "EldenRing"
    def testLocationDefaultItems(self):
        for locations in location_tables.values():
            for location in locations:
                if location.default_item_name:
                    self.assertIn(location.default_item_name, item_table)

    def testLocationsUnique(self):
        names = set()
        for locations in location_tables.values():
            for location in locations:
                self.assertNotIn(location.name, names)
                names.add(location.name)

class TestAccess(WorldTestBase):
    game = "EldenRing"
    def testEnia(self) -> None:
        """test enia remembrances"""
        return
        remembrances = [
            (
                "Remembrance of the Grafted",
                ["Axe of Godrick", "Grafted Dragon"]
            ),
            (
                "Remembrance of the Full Moon Queen", 
                ["Carian Regal Scepter", "Rennala's Full Moon"]
            ),
            (
                "Remembrance of the Starscourge",
                ["Starscourge Greatsword", "Lion Greatbow"]
            ),
            (
                "Remembrance of the Regal Ancestor",
                ["Winged Greathorn", "Ancestral Spirit's Horn"]
            ),
            (
                "Remembrance of the Omen King",
                ["Morgott's Cursed Sword", "Regal Omen Bairn"]
            ),
            (
                "Remembrance of the Naturalborn",
                ["Ash of War: Waves of Darkness", "Bastard's Stars"]
            ),
            (
                "Remembrance of the Blasphemous",
                ["Rykard's Rancor", "Blasphemous Blade"]
            ),
            (
                "Remembrance of the Lichdragon",
                ["Fortissax's Lightning Spear", "Death Lightning"]
            ),
            (
                "Remembrance of the Fire Giant",
                ["Giant's Red Braid", "Burn, O Flame!"]
            ),
            (
                "Remembrance of the Blood Lord",
                ["Mohgwyn's Sacred Spear", "Bloodboon"]
            ),
            (
                "Remembrance of the Black Blade",
                ["Maliketh's Black Blade", "Black Blade"]
            ),
            (
                "Remembrance of the Dragonlord",
                ["Dragon King's Cragblade", "Placidusax's Ruin"]
            ),
            (
                "Remembrance of Hoarah Loux",
                ["Axe of Godfrey", "Ash of War: Hoarah Loux's Earthshaker"]
            ),
            (
                "Remembrance of the Rot Goddess",
                ["Hand of Malenia", "Scarlet Aeonia"]
            ),
            (
                "Elden Remembrance",
                ["Marika's Hammer", "Sacred Relic Sword"]
            ),
        ]
        for (remembrance, items) in remembrances:
            location = [f"RH: {item} - Enia for {remembrance}" for item in items]
            have_items = [[remembrance]]
            self.assertAccessDependency(location, have_items, True)
            
    def testEquipCham(self) -> None:
        """test equip of cham"""
        # NOTE (region-spine surgery, SPEC-region-spine-surgery.md SS3.4/3.5): the early
        # `return` below makes this method dead code -- nothing past it ever executes, so
        # the "Rold Medallion" / "Haligtree Secret Medallion (Left/Right)" strings in the
        # have_items literal further down are inert, not a live test failure. They are
        # LEFT AS-IS deliberately rather than rewritten, since editing dead code risks
        # papering over a future refactor that removes the guard without revisiting the
        # body. Medallions are unpooled (inject=False) by this surgery (Track D); if this
        # test is ever revived, replace the medallion entries with the corresponding locks
        # (Rold Medallion -> Mountaintops Lock, Haligtree Secret Medallion (L/R) ->
        # Haligtree Lock) per RUNBOOK-SPINE-SURGERY.md.
        return
        equipments = [ # done
            ( # RA mainboss
                "RLA mainboss", #"Rennala, Queen of the Full Moon", # boss
                "RLA: Remembrance of the Full Moon Queen - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Queen's Crescent Crown", 
                    "Queen's Robe",
                    "Queen's Leggings", 
                    "Queen's Bracelets"
                ]
            ),
            ( # MH mainboss
                "EBH/HR mainboss", #"Malenia Blade of Miquella", # boss
                "EBH/HR: Remembrance of the Rot Goddess - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Malenia's Winged Helm", 
                    "Malenia's Armor",
                    "Malenia's Gauntlet", 
                    "Malenia's Greaves"
                ]
            ),
            ( # LAC mainboss
                "LAC/QB mainboss", #"Godfrey, First Elden Lord", # boss
                "LAC/QB: Remembrance of Hoarah Loux - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Elden Lord Crown", 
                    "Elden Lord Armor",
                    "Elden Lord Bracers", 
                    "Elden Lord Greaves"
                ]
            ),
            ( # TSC boss
                "TSC/SCIG boss", #"Elemer of the Briar", # boss
                "TSC/SCIG: Briar Greatshield - boss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Briar Helm", 
                    "Briar Armor",
                    "Briar Gauntlets", 
                    "Briar Greaves"
                ]
            ),
            ( # MH boss
                "MH/HTP boss", #"Loretta, Knight of the Haligtree", # boss
                "MH/HTP: Loretta's Mastery - boss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Royal Knight Helm", 
                    "Royal Knight Armor",
                    "Royal Knight Gauntlets", 
                    "Royal Knight Greaves"
                ]
            ),
            ( # FA mainboss
                "FA/BGB mainboss", #"Maliketh, the Black Blade", # boss
                "FA/BGB: Remembrance of the Black Blade - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Maliketh's Helm", 
                    "Maliketh's Armor",
                    "Maliketh's Gauntlets", 
                    "Maliketh's Greaves"
                ]
            ),
            ( # MotG/(CS) mainboss
                "MotG/(CS) mainboss", #"Commander Niall", # boss
                "MotG/(CS): Veteran's Prosthesis - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Veteran's Helm", 
                    "Veteran's Armor",
                    "Veteran's Gauntlets", 
                    "Veteran's Greaves"
                ]
            ),
            ( # WD mainboss
                "CL/(WD) mainboss", #"Starscourge Radahn", # boss
                "CL/(WD): Remembrance of the Starscourge - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Radahn's Redmane Helm", 
                    "Radahn's Lion Armor",
                    "Radahn's Gauntlets", 
                    "Radahn's Greaves"
                ]
            ),
            ( # LRC mainboss
                "LRC/QB mainboss", #"Morgott, The Omen King", # boss
                "LRC/QB: Remembrance of the Omen King - mainboss drop", # a drop from boss, so we can do 'can get' check
                ["Fell Omen Cloak"]# item
            ),
            ( # MP mainboss
                "MP/(MDM) mainboss", # "Mohg, Lord of Blood", # boss
                "MP/(MDM): Remembrance of the Blood Lord - mainboss drop", # a drop from boss, so we can do 'can get' check
                ["Lord of Blood's Robe"]# item
            ),
        ]

        for (boss, boss_location, eq_items) in equipments:
            # cant get to wailing dunes for radahns check, why idk
            
            location = [f"RH: {item} - Enia shop, defeat {boss}" for item in eq_items]
            have_items = [["Godrick's Great Rune", "Rykard's Great Rune", "Rusty Key", "Academy Glintstone Key", "Rold Medallion", 
                           "Dectus Medallion (Left)", "Dectus Medallion (Right)", "Drawing-Room Key",
                           "Haligtree Secret Medallion (Left)", "Haligtree Secret Medallion (Right)",
                           "Smithing-Stone Miner's Bell Bearing [1]", "Smithing-Stone Miner's Bell Bearing [2]",
                           "Somberstone Miner's Bell Bearing [1]", "Somberstone Miner's Bell Bearing [2]"]] 
            # bells are for the bell rules for access to mountaintops, farum needs 3 and 4, ash needs som 5
            self.assertAccessDependency(location, have_items, True)
            
    def testLocAccess(self) -> None:
        """test region access"""
        # NOTE (region-spine surgery, SPEC-region-spine-surgery.md SS3.4/3.5): same
        # dead-code situation as testEquipCham above -- the early `return` makes the
        # medallion strings in have_items below inert. See RUNBOOK-SPINE-SURGERY.md for
        # the medallion-unpool replacement-gate decision if this test is revived.
        return
        have_items = [["Godrick's Great Rune", "Rykard's Great Rune", "Rusty Key", "Academy Glintstone Key", "Rold Medallion", 
                        "Dectus Medallion (Left)", "Dectus Medallion (Right)", "Drawing-Room Key",
                        "Haligtree Secret Medallion (Left)", "Haligtree Secret Medallion (Right)",
                        "Smithing-Stone Miner's Bell Bearing [1]", "Smithing-Stone Miner's Bell Bearing [2]",
                        "Somberstone Miner's Bell Bearing [1]", "Somberstone Miner's Bell Bearing [2]",]] 
        
        self.assertAccessDependency([], have_items)
              
#pytest worlds/eldenring/tests   