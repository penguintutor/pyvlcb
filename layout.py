# Class to hold details about the layout / locos etc
# Reads data from layout.json file
# Todo in future add multiple layout files
import json
import os


# Holds specific information about the layout
# particularly useful for giving friendly names
# to replace nodeIDs
class Layout():
    def __init__ (self, layout_name, layout_dir, layout_file=None):
        self.name = layout_name
        self.layout_dir = layout_dir
        # If not file specified then default to name.json
        # Warning this will read and potentially write to the file if it already exists
        if layout_file != None:
            self.layout_file = layout_file
        else:
            layout_file = self.name+".json"
        # Create directory names
        #basedir = os.path.dirname(__file__)
        #self.data_dir = os.path.join(basedir, "data")
        #self.loco_dir = os.path.join(self.data_dir, "locos")
        #self.layout_dir = os.path.join(self.data_dir, "layout")
        filename = os.path.join(self.layout_dir, self.layout_file)
        try:
            with open(filename, 'r') as data_file:
                self.layout_data = json.load(data_file)
        except:
            print (f"No layout file '{filename}' using default values")
            self.layout_data = { }
        # Check we have an objects file - if not then set default name
        if 'layout-objs' in self.layout_data:
            self.layout_objs_file = self.layout_data['layout-objs']
        else:
            # If not file specified then use default name = <name>-objects.json
            # Using lower case
            self.layout_objs_file = self.name.lower() + "-objects.json"
        
        
        self.node_names = {
            300: "Solenoid1",
            301: "Servo1",
            65535: "CANCAB",		# 0xffff
            65534: "CANCMD"			# 0xfffe
            }
        # 2 dimension node, evid, name
        self.ev_names = {
            0: {22: "Solenoid1"},
            300: {1: "Solenoid01", 2: "Solenoid02"},
            301: {1: "Servo1"}
            }
        
    def get_layout_image (self):
        # check we have an image - if not return default
        # Only checks for a defined entry - can return invalid name if corrupt .json file or file deleted
        if 'layout-image' in self.layout_data:
            return os.path.join(self.layout_dir, self.layout_data['layout-image'])
        else:
            return os.path.join(os.path.dirname(__file__), "nolayout.png")
        
    def get_layout_objs_file (self):
        # Returns filename - file may not exist if this is new
        return self.layout_objs_file
        
    # Returns list of lists. Each entry ["Friendly name", "filename"]
    def get_locos (self):
        return self.layout_data['locos']
    
    def get_loco_names (self):
        # Temp return empty string - looking to move to a new class
        return []
    
        names = []
        for loco_entry in self.layout_data['locos']:
            names.append(loco_entry[0])
        return names
    
    # Just return one loco name
    def get_loco_name (self, num):
        return self.layout_data['locos'][num][0]
    
    # Get loco filename based on position in list
    # Based on same order as get_loco
    # Returns full path
    def get_loco_filename (self, num):
        return os.path.join(self.loco_dir, self.layout_data['locos'][num][1])
        
        
    def node_name (self, node_id):
        #print (f"Node id {node_id}")
        if (node_id in self.node_names.keys()):
            #print (f" name {self.node_names[node_id]}")
            return self.node_names[node_id]
        else:
            #print (f" name (from node) Node: {node_id}")
            return f"Node: {node_id}"
        
    # EV name normally use en, if not in lookup 
    def ev_name (self, node_id, ev_id, en=None):
        if (node_id in self.ev_names.keys() and ev_id in self.ev_names[node_id].keys()):
            return self.ev_names[node_id][ev_id]
        elif en != None:
            return f"{en:#08x}"
        else:
            return f"EV {ev_id}"