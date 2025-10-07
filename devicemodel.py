# Device Model or known as a Domain Model
# manages the logical state of devices
import os
import json
from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from vlcbclient import VLCBClient
from eventbus import EventBus, event_bus
from locolist import LocoList
from loco import Loco
from deviceevent import DeviceEvent
from locoevent import LocoEvent
from appevent import AppEvent
from guievent import GuiEvent
from automateevent import AutomateEvent


# Many of the methods in there (particularly when related to self.locos)
# are just used to hand off to the other class. This maintains device_model as
# the primary interface to decouple from LocoList etc.

## Serialize / Deserialize yards
# The serialize_event function must be defined before it is used.
# def serialize_yard(obj):
#     if isinstance(obj, LocoYard):
#         return obj.__dict__()
#     raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')
# 
# def deserialize_yard(data):
#     return EventBus.event_map[data["event_type"]] (data)

class DeviceModel(QObject):
    # This signal is internal to the model or for ViewModels to subscribe to
    # to react to state changes in the core data.
    # model_updated = Signal(str) # Emits device_id when its state changes
    
    # Map to Classes
    event_map = {
        'VLCB': DeviceEvent,		# This should be used in preference to Device
        'Device': DeviceEvent,
        'Loco': LocoEvent,
        'App': AppEvent,
        'Gui': GuiEvent,
        'Automate': AutomateEvent
        }
    
    # Used to update treeview on gui thread
    add_node_signal = Signal(QStandardItem, QStandardItem)

    def __init__(self):
        super().__init__()
        
        # dict of nodes indexed by NN
        self.nodes = {}
        
        # Yards are used to load locos from
        # Don't actually store the locos in here, but the yard is used for grouping the locos

        # Locos is now replaced with a Loco_list
        # can't create until we've loaded the directories so set to None initially
        self.locos = None
        
        # These directories and filenames as specified when first loading the loco
        # Listed here for easy reference
        self.locos_dir = None

        
        # Other nodes are stored in here for lookup in menus or eventbus
        # Every "node" must be added to the device model
        self.other_nodes = {
            'App': [],
            'Gui': [],
            # 'DeviceEvent': [], # Device are stored in self.nodes
            # 'Loco': [], # Loco are in self.locos
            'Automate': []
        }
        
        # Subscribe to events from the API layer
        #event_bus.device_event_signal.connect(self._update_device_status)
        #event_bus.gui_event_signal.connect(self._update_layout_status)
        
        # layout used for getting user name for devices
        self.layout = None
        # Also add any node information to QStandardItemModel
        # The GUI nodes are contained within the node class instances. This is specific to the node list in TreeView
        self.node_model = QStandardItemModel()
        self.node_model.setHorizontalHeaderLabels(['Nodes'])

    # Get the loco object from the loco name
    def get_loco_from_name (self, name):
        return self.locos.get_loco_from_name (name)
        
        
    def save_yards (self):
        # Convert each LocoYard object to JSON-serializable dictionary
        json_yard_list = [yard.to_json() for yard in self.yards]
        try:
            with open(self.yards_file, 'w') as data_file:
                json.dump(json_yard_list, data_file, indent=4)
        except Exception as e:
            print (f"Error saving yard file {self.yards_file} {e}")
            
    # Load the locos file by opening in LocoList 
    def load_locos (self, locos_path, locos_filename):
        # Is this the first time we've seen locos_dir?
        # if so save - if not then ignore the path
        if self.locos_dir == None:
            self.locos_dir = locos_path
        # If the LocoList is not initialized then we do that here
        if self.locos == None:
            #full_path = os.path.join(self.data_dir, locos_filename)
            self.locos = LocoList (self.locos_dir, locos_filename)
        # If not then call load file against existing
        else:
            #full_path = os.path.join(self.data_dir, locos_filename)
            self.locos.load_file (locos_filename)

    # Get all locos as Loco objects            
    def get_all_locos (self):
        return self.locos.get_all_locos()
    
    # Get enabled locos - returns list of displaynames (or equivelant)
    def get_enabled_locos (self):
        # If locos not initialised yet return empty list
        if self.locos == None:
            return []
        return self.locos.get_enabled_locos()
                

    # Return Gui object matching name
    # Or return None
    def get_guiobject_name (self, name):
        for node in self.other_nodes['Gui']:
            if node.name == name:
                return node
        return None
        
    # Given a node respond with Event type
    # Eg. device, loco, app, gui, automate (in that order - if duplicate - although should not be duplicates) 
    def get_type_node (self, node_name):
        # First lookup own devices
        for key, this_node in self.nodes.items():
            if this_node.name == node_name:
                return "VLCB"
        for loco in self.locos:
            if this_loco.name == node_name:
                return "Loco"
        # todo test this
        for other_event in self.other_nodes:
            for this_event in other_event:
                if this_event == node_name:
                    return this_event.type()
                
    # Get list of nodes by names
    # Default return All types - including VLCB & Gui etc.
    def get_nodes_names(self, type="all"):
        #print (f"Getting node names {type}")
        #print (f"Nodes {self.nodes}")
        #print (f"Keys {self.nodes.keys()}")
        node_list = []
        # VLCB devices
        if type=="all" or type=="VLCB":
            for key in self.nodes.keys():
                node_list.append(self.nodes[key].name)
        # Gui devices
        if type=="all" or type=="Gui":
            for node in self.other_nodes['Gui']:
                node_list.append(node.name)
        return node_list
    

    
    # From name to key for DeviceEvents
    # Key is node_id so returning key will return node_id
    def name_to_key(self, name, type="VLCB"):
        if type == "VLCB":
            for key in self.nodes.keys():
                # match on either name or string
                if self.nodes[key].name == name or str(self.nodes[key]) == name:
                    #print (f"name match {name}, key {key}")
                    return key
        elif type in self.other_nodes.keys():
            for i in range(len(self.other_nodes[type])):
                if self.other_nodes[type][i].name == name:
                    return i
        return None

    # Based on node_id and evnaame get event_id
    def evname_to_evid (self, node_id, evname):
        node = self.nodes[node_id]
        for key in node.ev.keys():
            # Allow either event name, or if used in dialog allow __str__ format
            if node.ev[key].name == evname or str(node.ev[key]) == evname:
                return key
        return None
        
    
    # get events for specified node
    def get_events(self, node, type="VLCB"):
        #print (f"Get events {node}, {type}")
        if type == "VLCB":
            if node in self.nodes.keys():
                return self.nodes[node].get_ev_names()
        # Todo add Gui here
        elif type in self.other_nodes.keys():
            #print (f"Checking for EVs {self.other_nodes[type]}")
            return self.other_nodes[type][node].get_ev_names()
        return ""
        
    # set layout from mainwindow
    def set_layout (self, layout):
        self.layout = layout
        
    # Default add a loco with no details
    # Note that this does not save the file, or add it to the locos.json file
    # Instead that needs to be called separately when confirming
    # that the save was successful
    def add_loco (self, filename, loco_id=0):
        new_loco = self.locos.add_loco(filename, loco_id)
        return (new_loco)
    
    # Remove loco - if deleted or fail to save
    # delete = False does not clean up the <loco>.json file
    # Set to true to remove the loco file (images are not deleted in case used elsewhere)
    def remove_loco (self, filename, delete=False):
        self.locos.remove_loco (filename, delete)
    
    # Save locos to file
    def save_locos (self):
        self.locos.save_file()
        
    def node_exists (self, node):
        if node in self.nodes.keys():
            return True
        return False
    
    # Add node if not exist - else returnFalse
    # Only used for devices - also see add_gui_node
    def add_node (self, node):
        if not node in self.nodes.keys():
            self.nodes[node.node_id] = node
            # Also set name
            self.set_name (node.node_id, self.layout.node_name(node.node_id))
            
            # Add the node to the top level of the qtreeview
            # child nodes are added through the node as child on gui_node
            self.node_model.appendRow(self.nodes[node.node_id].get_gui_node())
            return True
        return False
    
    # Add GUI node - initially just add to tree view
    def add_gui_node (self, gui_object):
        # Adds this to the top level of the tree view
        # child nodes are added through the gui_object as child on gui_node
        self.node_model.appendRow(gui_object.get_gui_node())
        # Add the entire gui_object to other_nodes
        self.other_nodes['Gui'].append(gui_object)

    def set_name (self, node_id, name):
        if not node_id in self.nodes.keys():
            return False
        # This must be through method and not directly editing name
        # so as to be updated in the QStandardItem
        self.nodes[node_id].set_name(name)
        return True

    def set_numev (self, node_id, numev):
        if not node_id in self.nodes.keys():
            return False
        self.nodes[node_id].set_numev(numev)
        return True
    
    def set_evspc (self, node_id, evspc):
        if not node_id in self.nodes.keys():
            return False
        self.nodes[node_id].set_evspc(evspc)
        return True
    
    def add_ev(self, node_id, ev_id, en):
        #print (f"Adding EV {node_id}, {ev_id}, {en}")
        if not node_id in self.nodes.keys():
            return False
        # Add the EV
        ev_node = self.nodes[node_id].add_ev(ev_id, en)
        # Send signal so that the gui thread can perform addRow
        self.add_node_signal.emit (self.nodes[node_id].gui_node, ev_node.gui_node)
        # Update the name based on layout
        name = self.layout.ev_name(node_id, ev_id, en)
        self.update_ev(node_id, ev_id, "name", name)
        
        
        return True

    def update_node (self, node_id, upd_dict):
        return self.nodes[node_id].update_node(upd_dict)
    
    # updates event, field is the field to update (eg. "name")
    def update_ev (self, node_id, ev_id, field, value):
        if not node_id in self.nodes.keys():
            return False
        return self.nodes[node_id].update_ev(ev_id, field, value)
        
    
    def get_gui_node (self, node_id):
        return self.nodes[node_id].gui_node


    def get_device_info(self, device_id: str):
        return self._devices.get(device_id, {})
    
    # uses filename only (strip using basename prior to calling this)
    def get_loco_from_filename (self, filename):
        # pass to locolist to reduce coupling
        return self.locos.get_loco_from_filename (filename)


# Singleton for the Device Model
device_model = DeviceModel()
