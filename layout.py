# Class to hold details about the layout / locos etc
# Reads data from layout.json file
import json
import os


# Holds specific information about the layout
# particularly useful for giving friendly names
# to replace nodeIDs
class Layout():
    def __init__ (self, layout_file):
        self.layout_file = layout_file
        # Create directory names
        basedir = os.path.dirname(__file__)
        self.data_dir = os.path.join(basedir, "data")
        self.loco_dir = os.path.join(self.data_dir, "locos")
        self.layout_dir = os.path.join(self.data_dir, "layout")
        with open(os.path.join(self.data_dir, self.layout_file), 'r') as data_file:
            self.layout_data = json.load(data_file)
        
        
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
        return os.path.join(self.layout_dir, self.layout_data['layout-image'])
        
    # Returns list of lists. Each entry ["Friendly name", "filename"]
    def get_locos (self):
        return self.layout_data['locos']
    
    def get_loco_names (self):
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