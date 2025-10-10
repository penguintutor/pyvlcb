# Class to hold details about the layout / locos etc
# Reads data from layout.json file
# Todo in future add multiple layout files
import json
import os
from guiobject import GuiObject
from devicemodel import device_model


# Holds specific information about the layout
# can also be useful for giving friendly names to replace nodeIDs
# layout_file - filename must be provided, but if not exist it will be created without warning

class Layout():
    def __init__ (self, mainwindow, layout_dir, layout_file):
        self.mainwindow = mainwindow
        self.layout_file = layout_file
        self.layout_dir = layout_dir
        
        # general settings are stored in self.layout_data
        # Objects on the GUI are saved under guiobjects
        self.guiobjects = []
        self.load_file()


    def load_file (self):
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
            
        # Load the guiobjects from self.layout_data['guiobjects']
        # First reset guiobjects so we don't add to the end of existing
        self.guiobjects = []
        for entry in self.layout_data['guiobjects']:
            if 'object' in entry.keys():
                if entry['object'] == 'gui':
                    #self.railway.guiobjects.append(GuiObject(self, entry['type'], entry['name'], {}))
                    self.add_gui_device(entry['type'], entry['name'])
                elif entry['object'] == 'button':
                    gui_node_id = self.gui_name_toid(entry['guiobject'])
                    self.guiobjects[gui_node_id].add_button(entry['button_type'], entry['settings'], entry['pos'])
                elif entry['object'] == 'label':
                    gui_node_id = self.gui_name_toid(entry['guiobject'])
                    self.guiobjects[gui_node_id].add_label(entry['label_type'], entry['settings'], entry['pos'])
            
                
    def add_gui_device (self, device_type, device_name):
        self.guiobjects.append(GuiObject(self, device_type, device_name, {}))
        # Add to node tree
        #print (f"Adding to node tree {self.railway.guiobjects[-1].name}")
        device_model.add_gui_node(self.guiobjects[-1])
        
    # Labels and buttons are added to guiobjects 
    # Here pos is optional so it's moved to the end
    def add_label (self, gui_node_name, label_type, settings, pos=(5,5)):
        gui_node_id = self.gui_name_toid(gui_node_name)
        # check gui node is valid (no reason it shouldn't be)
        if gui_node_id < 0:
            print (f"Invalid gui name {gui_node_name}")
        self.guiobjects[gui_node_id].add_label (label_type, settings, pos)
        
    def add_button (self, gui_node_name, button_type, settings, pos=(5,5)):
        gui_node_id = self.gui_name_toid(gui_node_name)
        # check gui node is valid (no reason it shouldn't be)
        if gui_node_id < 0:
            print (f"Invalid gui name {gui_node_name}")
        self.guiobjects[gui_node_id].add_button (button_type, settings, pos)
        
    # From name get pos in list
    # used when adding buttons / labels etc.
    def gui_name_toid (self, gui_name):
        for i in range (0, len(self.guiobjects)):
            if self.guiobjects[i].name == gui_name:
                return i
        # Shouldn't return -1 as gui wouldn't show name that doesn't exist
        return -1
        
        
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
        
        # Add all gui objects into self.layout_data['guiobjects']
        
        # clear out any existing objects
        self.layout_data['guiobjects'] = []
        
        for object in self.guiobjects:
            self.layout_data['guiobjects'].extend(object.get_save_objects())
        
        
        try:
            with open(filename, 'w') as data_file:
                json.dump(self.layout_data, data_file, indent=4)
        except Exception as e:
            print (f"Error saving layout file {filename} {e}")
            
    def gui_object_names (self):
        return_list = []
        for object in self.guiobjects:
            return_list.append(object.name)
        return return_list
                   
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