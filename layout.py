# Class to hold details about the layout / locos etc
# Reads data from layout.json file
# Todo in future add multiple layout files
import json
import os


# Holds specific information about the layout
# can also be useful for giving friendly names to replace nodeIDs
# layout_file - filename must be provided, but if not exist it will be created without warning

class Layout():
    def __init__ (self, layout_dir, layout_file):
        self.layout_file = layout_file
        self.layout_dir = layout_dir

        filename = os.path.join(self.layout_dir, self.layout_file)
        try:
            with open(filename, 'r') as data_file:
                self.layout_data = json.load(data_file)
        except:
            #print (f"No layout file '{filename}' using default values")
            self.layout_data = { }
        # If no title (eg. new filename - then set)
        if not ('title' in self.layout_data):
            self.layout_data['title'] = "Default Layout"
            
        # Check we have an objects file - if not then set default name
#         if 'layout-objs' in self.layout_data:
#             self.layout_objs_file = self.layout_data['layout-objs']
#         else:
#             # If not file specified then use default name = <name>-objects.json
#             # Using lower case
#             self.layout_objs_file = self.name.lower() + "-objects.json"
        
        
#         self.node_names = {
#             300: "Solenoid1",
#             301: "Servo1",
#             65535: "CANCAB",		# 0xffff
#             65534: "CANCMD"			# 0xfffe
#             }
#         # 2 dimension node, evid, name
#         self.ev_names = {
#             0: {22: "Solenoid1"},
#             300: {1: "Solenoid01", 2: "Solenoid02"},
#             301: {1: "Servo1"}
#             }

    # For the setters then unless part of a multi-item update then save immediately
    def set_layout_image (self, filename):
        self.layout_data['layoutimage'] = filename
        self.save_file()
        
        
    def get_layout_image (self):
        # check we have an image - if not return default
        # Only checks for a defined entry - can return invalid name if corrupt .json file or file deleted
        if 'layoutimage' in self.layout_data:
            return os.path.join(self.layout_dir, self.layout_data['layoutimage'])
        else:
            return os.path.join(os.path.dirname(__file__), "nolayout.png")
        
    def get_layout_objs_file (self):
        # Returns filename - file may not exist if this is new
        return self.layout_objs_file
    
    def save_file (self):
        filename = os.path.join(self.layout_dir, self.layout_file)
        try:
            with open(filename, 'w') as data_file:
                json.dump(self.layout_data, data_file, indent=4)
        except Exception as e:
            print (f"Error saving layout file {filename} {e}")
            
            
        
        
    # Returns list of lists. Each entry ["Friendly name", "filename"]
   # def get_locos (self):
   #     return self.layout_data['locos']
    
   # def get_loco_names (self):
   #     # Temp return empty string - looking to move to a new class
   #     return []
    
    #    names = []
    #    for loco_entry in self.layout_data['locos']:
    #        names.append(loco_entry[0])
    #    return names
    
    # Just return one loco name
    #def get_loco_name (self, num):
    #    return self.layout_data['locos'][num][0]
    
    # Get loco filename based on position in list
    # Based on same order as get_loco
    # Returns full path
    #def get_loco_filename (self, num):
    #    return os.path.join(self.loco_dir, self.layout_data['locos'][num][1])
        
        
    # Translation from node_id to friendly name
    # Ideally this should be done within the module, but could be supported here
    # Temporarily disabled
    def node_name (self, node_id):
        return f"Node: {node_id}"
#         #print (f"Node id {node_id}")
#         if (node_id in self.node_names.keys()):
#             #print (f" name {self.node_names[node_id]}")
#             return self.node_names[node_id]
#         else:
#             #print (f" name (from node) Node: {node_id}")
#             return f"Node: {node_id}"
        
    # As with node name - is this needed - need to implement differently
    # EV name normally use en, if not in lookup 
    def ev_name (self, node_id, ev_id, en=None):
        #if (node_id in self.ev_names.keys() and ev_id in self.ev_names[node_id].keys()):
        #    return self.ev_names[node_id][ev_id]
        if en != None:
            return f"{en:#08x}"
        else:
            return f"EV {ev_id}"