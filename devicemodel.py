# Device Model or known as a Domain Model
# manages the logical state of devices
from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from vlcbclient import VLCBClient
from eventbus import EventBus, event_bus
#from deviceevent import DeviceEvent
#from guievent import GuiEvent
from loco import Loco

class DeviceModel(QObject):
    # This signal is internal to the model or for ViewModels to subscribe to
    # to react to state changes in the core data.
    model_updated = Signal(str) # Emits device_id when its state changes
    

    def __init__(self):
        super().__init__()
        # dict of nodes indexed by NN
        self.nodes = {}
        # typically the GUI will have one loco = [0]
        # allow more to allow automation
        self.locos = []
        # Subscribe to events from the API layer
        #event_bus.device_event_signal.connect(self._update_device_status)
        #event_bus.gui_event_signal.connect(self._update_layout_status)
        
        # layout used for getting user name for devices
        self.layout = None
        # Also add any node information to QStandardItemModel
        # The GUI nodes are contained within the node class instances. This is specific to the node list in TreeView
        self.node_model = QStandardItemModel()
        self.node_model.setHorizontalHeaderLabels(['Nodes'])
        
    def get_nodes_names(self):
        #print (f"Nodes {self.nodes}")
        #print (f"Keys {self.nodes.keys()}")
        node_list = []
        for key in self.nodes.keys():
            node_list.append(self.nodes[key].name)
        return node_list
    
    def name_to_key(self, name):
        for key in self.nodes.keys():
            if self.nodes[key].name == name:
                #print (f"name match {name}, key {key}")
                return key
        return None
    
    # get events for specified node
    def get_events(self, node):
        if node in self.nodes.keys():
            return self.nodes[node].get_ev_names()
        else:
            return ""
        
    # set layout from mainwindow
    def set_layout (self, layout):
        self.layout = layout
        
    def add_loco (self):
        self.locos.append(Loco())
        return (len(self.locos)-1)
        
    def node_exists (self, node):
        if node in self.nodes.keys():
            return True
        return False
    
    # Add node if not exist - else returnFalse
    def add_node (self, node):
        #print (f"Adding node {node.node_id}")
        if not node in self.nodes.keys():
            self.nodes[node.node_id] = node
            # Also set name
            #self.set_name (node.node_id, self.layout.node_name(node))
            self.set_name (node.node_id, self.layout.node_name(node.node_id))
            # Add the gui node to the node_model
            #print (f"GUI Node {self.nodes[node.node_id].get_gui_node().text()}")
            #print (f"Adding {node.node_id} - {self.nodes[node.node_id].get_gui_node()}")
            self.node_model.appendRow(self.nodes[node.node_id].get_gui_node())
            return True
        return False
    

    def set_name (self, node_id, name):
        #print (f"Set name in devicemodel {node_id} = {name}")
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
        if not node_id in self.nodes.keys():
            return False
        # Add the EV
        self.nodes[node_id].add_ev(ev_id, en)
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

#     def activate_device(self, device_id: str, status: bool):
#         # This method is called by the ViewModel, which then publishes a command
#         # This isn't strictly necessary as the ViewModel could publish directly,
#         # but the Model can act as a central place for business rules/validation.
#         print(f"Model: Activating device {device_id} to {status}")
#         event_bus.publish(SetDeviceCommand(device_id, status))

# Singleton for the Device Model
device_model = DeviceModel()
