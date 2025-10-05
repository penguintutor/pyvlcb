# List of all locos
# Doesn't hold details of the locos, just the filenames so that they can be loaded
# Tracks which are enabled / disabled but does not save in the locos.json file
# Enabled is stored in the layout file allowing allocating locos to the specific layout

import os
import json
from loco import Loco

class LocoList:
    def __init__ (self, locos_dir, locos_file):
        self.locos_dir = locos_dir
        self.filename = locos_file	# locos_file needs full pathname (as not in locos_dir)
        #self.loco_filenames = [] (filenames is just the dict keys - use .keys() instead)
        # Locos is a dictionary of Locos
        # The index is the filename
        self.locos = {}
        
        self.enabled_locos = []	# This is whether it's allowed in this session - not if it's been aquired etc
        # The order that they are stored in this list determines how they are returned
        # Load the locos.json file
        self.load_file()
        
    # Return all locos as a list (not a dict as they are stored)
    def get_all_locos (self):
        loco_list = []
        for loco in self.locos.values():
            loco_list.append(loco)
        return loco_list
    
    # Create a loco with defaults 
    def add_loco (self, filename, loco_id):
        full_path = os.path.join(self.locos_dir, filename)
        # Do not allow creating existing file (should be checked before here error to console only)
        if loco_file in self.locos:
            print (f"Loco file already exists {filename}")
            return None
        self.locos[filename] = Loco (loco_id, filename=full_path)
        return self.locos[filename]
        
    def add_loco_file (self, loco_file):
        # check it's valid and not a duplicate
        if loco_file in self.locos:
            print ("Loco already exists {loco_file}")
            return
        full_path = os.path.join(self.locos_dir, loco_file)
        # loco_file json file must be created before adding
        if not os.path.exists(full_path):
            print ("File not found {loco_file}")
            return
        self.locos.append(loco_file)
        self.load_loco(loo_file)
        # save
        self.save_file()
        
    def load_loco (self, filename):
        full_path = os.path.join(self.locos_dir, filename)
        self.locos[filename] = Loco.from_file(full_path)
            
    # Gets all locos from file (filename should include path)
    def load_file (self, locos_file = None):
        if locos_file == None:
            locos_file = self.filename
        try:
            with open(locos_file, 'r') as data_file:
                loco_filenames = json.load(data_file)
        except Exception as e:
            print (f"No locos found, add new locos {e}")
            return
        for filename in loco_filenames:
            # Now load each file
            self.load_loco (filename)
            
        
    def save_file (self, locos_file = None):
        if locos_file == None:
            locos_file = self.filename
        with open(locos_file, 'w') as data_file:
            json.dump(self.locos.keys(), data_file, indent=4)