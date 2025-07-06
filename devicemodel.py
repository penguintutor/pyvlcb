# Device Model or known as a Domain Model
# manages the logical state of devices
from PySide6.QtCore import Qt, QObject, Signal, Slot
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from vlcbclient import VLCBClient
from eventbus import EventBus, event_bus
from deviceevent import DeviceEvent
from layoutevent import LayoutEvent

class DeviceModel(QObject):
    # This signal is internal to the model or for ViewModels to subscribe to
    # to react to state changes in the core data.
    model_updated = Signal(str) # Emits device_id when its state changes
    
    ### nodes
    #self.nodes[data_entry['NN']] = VLCBNode(data_entry['NN'], mode, vlcb_entry.can_id, data_entry['ManufId'], data_entry['ModId'] ,data_entry['Flags'])
    #self.nodes[data_entry['NN']].set_name(self.layout.node_name(data_entry['NN']))

    def __init__(self):
        super().__init__()
        # dict of nodes indexed by NN
        self.nodes = {
            #"device": {"status": "UNKNOWN", "event": None}
        }
        # Subscribe to events from the API layer
        #event_bus.device_event_signal.connect(self._update_device_status)
        #event_bus.layout_event_signal.connect(self._update_layout_status)
        
    def node_exists (self, node):
        if node in self.nodes.keys():
            return True
        return False
    
    # Add node if not exist - else returnFalse
    def add_node (self, node):
        if not node in self.nodes.keys():
            self.nodes[node.node_id] = node
            return True
        return False

    def set_name (self, node_id, name):
        if not node_id in self.nodes.keys():
            return False
        self.nodes[node_id].name = name
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
        self.nodes[node_id].add_ev(ev_id, en)
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

    def _update_device_status(self, event: DeviceEvent):
        if event.device_id in self._devices:
            self._devices[event.device_id]["status"] = event.status
            print(f"Model: {event.device_id} status updated to {event.status}")
            self.model_updated.emit(event.device_id) # Notify others of change

    def _update_layout_status(self, event: LayoutEvent):
        if event.device_id in self._devices:
            self._devices[event.device_id]["layout"] = event.layout_event
            print(f"Model: {event.device_id} updated to {event.layout_event}")
            self.model_updated.emit(event.device_id) # Notify others of change

    def get_device_info(self, device_id: str):
        return self._devices.get(device_id, {})

    def activate_device(self, device_id: str, status: bool):
        # This method is called by the ViewModel, which then publishes a command
        # This isn't strictly necessary as the ViewModel could publish directly,
        # but the Model can act as a central place for business rules/validation.
        print(f"Model: Activating device {device_id} to {status}")
        event_bus.publish(SetDeviceCommand(device_id, status))

# Singleton for the Device Model
device_model = DeviceModel()
