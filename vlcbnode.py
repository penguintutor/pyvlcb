# This class object is intended for for use within the GUI only
# It closely couples the nodes to QStandardItems which makes it easier to update the GUI
# but at the expense of couplnig this to the GUI. There is also a last updated field
# so it's possible to see if the node has become stale

from PySide6.QtGui import QStandardItemModel, QStandardItem
from time import time


#ManufId,ModId,Flags
# Stores Nodes defined / discovered
class VLCBNode():
    def __init__ (self, node_id, can_id, manuf_id, mod_id, flags):
        self.node_id = node_id
        self.can_id = can_id
        self.manuf_id = manuf_id
        self.mod_id = mod_id
        self.flags = flags
        self.events = []
        self.time_updated = time()
        self.gui_node = QStandardItem(f"Unknown, {self.node_id}, {self.can_id}")
        self.numev = -1 # If number events unknown then set to -1
        
    # updates any of the entries - based on dict
    # Node_id cannot be changed as that is the unique identifier for the node
    # That will be ignored along with any unrecognised values
    # If any values changed then returns number of updates, if they are still the same then returns 0
    # tihs does not include the time_updated field which is always updated but not counted
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
        node_string = f"Unknown, NodeId: {self.node_id}, CanId: {self.can_id}"
        # If we have num eve add that to the string
        if self.numev >= 0:
            node_string += f", NumEv: {self.numev}"
        return node_string
    
    # Update QStandardItem with current string values
    def update_gui_node_string (self):
        self.gui_node.setText(self.__str__())
    
    def update_time (self):
        self.time_updated = time()
        
    def set_numev (self, numev):
        self.numev = numev
        self.update_gui_node_string()
        
    