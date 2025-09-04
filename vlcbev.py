# This class object is intended for for use within the GUI only
# It closely couples the nodes to QStandardItems which makes it easier to update the GUI
# but at the expense of coupling this to the GUI. 

from PySide6.QtGui import QStandardItemModel, QStandardItem
from time import time


#ManufId,ModId,Flags
# Stores Nodes defined / discovered
class VLCBEv():
    def __init__ (self, node, ev_id, en):
        self.name = f"{en:#08x}"
        # device_type exists over all types - inc Gui / VLCB etc.
        self.device_type = "VLCB"
        self.node = node    # Link to parent
        self.ev_id = ev_id  # Index of event EN#
        self.en = en        # Stored value of the event (EN3 to EN0)
        self.gui_node = QStandardItem(f"EV {self.ev_id} : {self.name}")
        
    # Sets name and updates the GUI string
    def set_name (self, name):
        self.name = name
        self.update_gui_node_string()
        
    def get_name (self):
        return self.name

    # Is it long format
    # basic check just look for <= ffff for short
    def is_long (self):
        if self.en <= 0xffff:
            return False
        return True

    def long_string (self):
        if self.is_long():
            return "Long"
        else:
            return "Short"
        
    def update_gui_node_string (self):
        self.gui_node.setText(self.__str__())
        
    # shorter version just updates the en if applicable
    def update_en(self, en):
        if en == self.en:
            return False
        self.en = en
        self.gui_node.setText(f"EV {self.ev_id} : {self.name}")
        
    # updates any of the entries - based on dict
    # ev_id cannot be changed as that is the unique identifier for the node
    # That will be ignored along with any unrecognised values
    def update_node(self, upd_dict):
        #
        # Uses new python switch case feature (version 3.10 updwards)
        items_changed = 0
        for key,value in upd_dict.items():
            match key:
                case 'EN':
                    if self.en != value:
                        self.en = value
                        items_changed += 1
        return items_changed
    
    def __str__ (self):
        node_string = f"EV {self.ev_id}, {self.name}"
        return node_string
    

        
    