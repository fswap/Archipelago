from test.bases import WorldTestBase

from worlds.dark_souls_3.Items import item_dictionary
from worlds.dark_souls_3.Locations import location_tables

class SekiroTest(WorldTestBase):
    game = "Sekiro: Shadows Die Twice"

    def testLocationDefaultItems(self):
        for locations in location_tables.values():
            for location in locations:
                if location.default_item_name:
                    self.assertIn(location.default_item_name, item_dictionary)

    def testLocationsUnique(self):
        names = set()
        for locations in location_tables.values():
            for location in locations:
                self.assertNotIn(location.name, names)
                names.add(location.name)