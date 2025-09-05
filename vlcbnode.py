# This class object is intended for for use within the GUI only
# It closely couples the nodes to QStandardItems which makes it easier to update the GUI
# but at the expense of coupling this to the GUI. There is also a last updated field
# so it's possible to see if the node has become stale

from PySide6.QtGui import QStandardItemModel, QStandardItem
from time import time
from vlcbev import VLCBEv

#ManufId,ModId,Flags
# Stores Nodes defined / discovered
class VLCBNode():
    def __init__ (self, node_id, mode, can_id, manuf_id, mod_id, flags):
        self.name = node_id            # Initially set to node id
        # device_type exists over all types - inc Gui / VLCB etc.
        self.device_type = "VLCB"
        # If layout has a real name then that will replace this later
        # Special case if node = 0xffff then it's a CAB controller
#         if node_id == 0xffff:
#             self.name = "CANCAB"
#         elif node_id == 0xfffe:
#             self.name = "CANCMD"
#         else:
#             self.name = node_id            # Initially set to node id
        self.node_id = node_id
        self.mode = mode   # Set to SLiM / FLiM if replies with own can_id
        self.can_id = can_id
        self.manuf_id = manuf_id
        self.mod_id = mod_id
        self.flags = flags
        #self.events = []
        self.time_updated = time()
        # GUI node is used to provide entry for the model view
        self.gui_node = QStandardItem(f"{self.name}, {self.node_id}, {self.can_id}")
        #self.gui_node = QStandardItem(f"{self.name}")
        self.numev = -1 # If number events unknown then set to -1
        self.evspc = -1 # event space
        # Events are stored as a dictionary with the ev_id as the index
        self.ev = {}
        
        
    def get_ev_names (self):
        #print (f"Getting Ev Names from {self.name}")
        #print (f" EV {self.ev}")
        list_names = []
        for key in self.ev.keys():
            #print (f" This EV {self.ev[key]}")
            list_names.append(self.ev[key].get_name())
        #print (f"EV names {list_names}")
        return list_names
        
    def get_gui_node (self):
        return self.gui_node
        
    # Sets name and updates the GUI string
    def set_name (self, name):
        #print (f"Setting name to {name}")
        self.name = name
        self.update_gui_node_string()

    # Check if item is this node (or a child of this node)
    # Returns None (if not found)
    #### Or list with node_id, ev_id (or 0 if top level)
    # or item if is
    def check_item (self, item):
        if self.gui_node == item:
            #print ("This node")
            #return ([self.node_id, 0])
            return self
        for key, ev in self.ev.items():
            if ev.gui_node == item:
                #return ([self.node_id, ev.ev_id])
                return ev
        return None
        
    # Adds ev node
    # Does not register to the treeview - that needs to be performed on the gui thread
    # Instead returns the node created so that device_model can emit that to gui thread
    def add_ev(self, ev_id, en):
        # Only add if new - otherwise try update
        if ev_id in self.ev.keys():
            self.ev[ev_id].update_en (en)
            return
        self.ev[ev_id]=VLCBEv(self, ev_id, en)
        return self.ev[ev_id]

        # Add Row left to the caller as that can access gui thread
        #self.gui_node.appendRow(self.ev[ev_id].gui_node)

        
    # field is to be updated - this needs to be coded manually
    # Features included = "name"
    def update_ev(self, ev_id, field, value):
        if not ev_id in self.ev.keys():
            return False
        if field == "name":
           self.ev[ev_id].set_name(value)
           return True
        # Unknown field
        else:
            return False
        
    # updates any of the entries - based on dict
    # Node_id cannot be changed as that is the unique identifier for the node
    # That will be ignored along with any unrecognised values
    # If any values changed then returns number of updates, if they are still the same then returns 0
    # this does not include the time_updated field which is always updated but not counted
    def update_node(self, upd_dict):
        # update time
        self.update_time()
        # Uses new python switch case feature (version 3.10 updwards)
        items_changed = 0
        for key,value in upd_dict.items():
            match key:
                case 'CanId':
                    if self.can_id != value:
                        self.can_id = value
                case 'ManufId':
                    if self.manuf_id != value:
                        self.manuf_id = value
                        items_changed += 1
                case 'ModId':
                    if self.mod_id != value:
                        self.mod_id = value
                        items_changed += 1
                case 'Flags':
                    if self.flags != value:
                        self.flags = value
                        items_changed += 1
        # If any items changed then also update the QStandardItem
        self.update_gui_node_string()
        return items_changed
    
    def __str__ (self):
        #print (f"Str -name {self.name}")
        return f"{self.name}, {self.node_id}, {self.can_id}"
        
    def extended_string (self):
        node_string = self.__str__()
        # If we have num ev add that to the string
        if self.numev >= 0:
            node_string += f", NumEv: {self.numev}"
        if self.evspc >= 0:
            node_string += f", EvSpc: {self.evspc}"
        return node_string
    
    def node_string (self):
        return f"{self.node_id} / {self.can_id}"
    
    def manuf_string (self):
        return f"{self.manuf_id} / {self.mod_id}"
    
    def ev_num_string (self):
        if self.numev != -1 and self.evspc != -1:
            return f"{self.numev} / {self.evspc}"
        # If don't have both number of events and event space then just return empty string
        return ("")
    
    # Update QStandardItem with current string values
    def update_gui_node_string (self):
        self.gui_node.setText(self.__str__())
    
    def update_time (self):
        self.time_updated = time()
        
    # Set the number of events
    def set_numev (self, numev):
        # An update to an event etc. also updates time
        self.update_time()
        self.numev = numev
        self.update_gui_node_string()
        
    # Sets the event space
    def set_evspc (self, evspc):
        # An update to an event etc. also updates time
        self.update_time()
        self.evspc = evspc
        self.update_gui_node_string()
        
    