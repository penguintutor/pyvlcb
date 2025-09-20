# A yard is a collection of Locos
# Allows locos to be added to collections. A loco can be in multiple yards
# Eg in future could have a default, steam, diesel, guest etc. (or any other name eg. era / company)
# The LocoYards are contained within the device_model allowing access through the singleton device_model 
# Todo Currently uses locoyard.json, but in future will allow multiple

import os
import json

class LocoYard:
    def __init__ (self, title, yard_file, loco_files=[]):
        self.title = title
        self.yard_file = yard_file
        # Each loco is saved by it's filename (does not include the basedir)
        # Can query details from the files through methods but not stored in the LocoYard
        self.loco_files = loco_files
        
        # Create directory names
        basedir = os.path.dirname(__file__)
        self.data_dir = os.path.join(basedir, "data")
        self.loco_dir = os.path.join(self.data_dir, "locos")
        # Load the yard
        # If it doesn't exist then assume new and it will get saved when edited (eg. loco added)
        try:
            with open(os.path.join(self.data_dir, self.yard_file), 'r') as data_file:
                self.data = json.load(data_file)
        except Exception as e:
            pass
            
    # Gets summary from file
    def load_file (self, filename):
        with open(filename, 'r') as data_file:
            loco_data = json.load(data_file)
        loco_id = self.loco_data["address"]
        loco_name = self.loco_data["display-name"]
        
    # Return a dict
    def to_json(self):
        return {
            'title': self.title,
            'filename': self.yard_file,
            'loco_files': self.loco_files
            }
    
    @classmethod
    def from_json(cls, data):
        return cls(data['title'], data['filename'], data['loco_files']) 
