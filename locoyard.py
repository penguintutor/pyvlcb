# A yard is a collection of Locos
# Allows locos to be added to collections. A loco can be in multiple yards
# Eg in future could have a default, steam, diesel, guest etc. (or any other name eg. era / company)
# The LocoYards are contained within the device_model allowing access through the singleton device_model 
# Todo Currently uses locoyard.json, but in future will allow multiple


import json

class LocoYard:
    def __init__ (self, tite, yard_file):
        self.yard_file = yard_file
        
        # Create directory names
        basedir = os.path.dirname(__file__)
        self.data_dir = os.path.join(basedir, "data")
        self.loco_dir = os.path.join(self.data_dir, "locos")
        # Load the yard
        with open(os.path.join(self.data_dir, self.yard_file), 'r') as data_file:
            self.data = json.load(data_file)
            
    # Gets summary from file
    def load_file (self, filename):
        with open(filename, 'r') as data_file:
            loco_data = json.load(data_file)
        loco_id = self.loco_data["address"]
        loco_name = self.loco_data["display-name"]
