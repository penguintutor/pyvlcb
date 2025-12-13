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
        # Stores the filename which is unique and allows easy lookup
        
        # Load the locos.json file
        self.load_file()
        
    def get_loco_from_filename (self, filename):
        if filename in self.locos.keys():
            return self.locos[filename]
        else:
            return None
        
    # get a loco entry based on the display name
    # does not guarentee only one match which filename does
    # returns first occurance
    def get_loco_from_name (self, name):
        for loco in self.locos.values():
            if name == loco.loco_name:
                return loco
        # If not found return None
        return None
        
        
    # Return all locos as a list (not a dict as they are stored)
    # Returns the Loco objects
    def get_all_locos (self):
        loco_list = []
        for key, loco in self.locos.items():
            loco_list.append(loco)
        return loco_list
    
    # Get enabled locos - return as a list of names (displayname or equivelant)
    def get_enabled_locos (self):
        loco_names = []
        # special case if none enabled then return all
        if len(self.enabled_locos) == 0:
            for loco in self.locos.values():
                loco_names.append (loco.loco_name)
        else:
            #print (f"self.locos {self.locos}")
            #print (f"Enabled locos {self.enabled_locos}")
            for filename in self.enabled_locos:
                if filename in self.locos:
                    loco_names.append (self.locos[filename].loco_name)
                # If not a known loco then skip (possibly loco removed but still in settings)
        return loco_names
    
    # Create a loco with defaults 
    def add_loco (self, filename, loco_id):
        full_path = os.path.join(self.locos_dir, filename)
        # Do not allow creating existing file (should be checked before here error to console only)
        if filename in self.locos:
            print (f"Loco file already exists {filename}")
            return None
        self.locos[filename] = Loco (loco_id, filename=full_path)
        return self.locos[filename]
    
    # Remove loco - if deleted or fail to save
    # delete = False does not clean up the <loco>.json file
    # Set to true to remove the loco file (images are not deleted in case used elsewhere)
    def remove_loco (self, filename, delete=False):
        # remove from self.locos:
        if filename in self.locos:
            del self.locos[filename]
        if delete == True:
            # Delete file if it exists
            # Just wrap in a try so that if file is not found then it's skipped
            full_path = os.path.join(self.locos_dir, filename)
            try:
                os.remove(full_path)
            except FileNotFoundError:
                # Just return false - no other error needed at this stage
                return False
            except OSError as e:
                # Perhaps permissions - give a warning to console only
                if e.errno == errno.EACCESS:
                    print(f"Permission denied. Could not delete {full_path}.")
                else:
                    print(f"Error attempting to delete {full_path} - {E}")
                return False
        # If not asked to delete file, or file deleted successfully
        return True        
        
    # Adds a loco to this list from a file
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
        #print (f"Loading loco {filename}")
        full_path = os.path.join(self.locos_dir, filename)
        self.locos[filename] = Loco.from_file(full_path)
        #print (f"Locos {self.locos}")
           
    # Gets all locos from file (filename should include path)
    def load_file (self, locos_file = None):
        if locos_file == None:
            locos_file = self.filename
        try:
            with open(locos_file, 'r') as data_file:
                loco_filenames = json.load(data_file)
                #print (f"Loaded locos {loco_filenames} from {locos_file}")
        except Exception as e:
            print (f"No locos found, add new locos {e}")
            return
        for filename in loco_filenames:
            # Now load each file
            self.load_loco (filename)
            
    # Saves the locosfile locos.json
    def save_file (self, locos_file = None):
        if locos_file == None:
            locos_file = self.filename
        with open(locos_file, 'w') as data_file:
            #print (f"Saving locos {self.locos.keys()} to {locos_file}")
            json.dump(list(self.locos.keys()), data_file, indent=4)