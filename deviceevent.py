# Tracks events against devices.
# When we receive / send an event do we need to update devices and corresponding objects
from event import Event

# event_data is a dictionary of key values
class DeviceEvent (Event):
    def __init__(self, event_data):
        super().__init__()
        # Set type after parent constructor
        #self.event_type = "Device"
        self.data = event_data
        self.data["event_type"] = "Device"
        
    # Uses getters to allow different data (eg. node vs node_id)
    # Node may be friendly name
    # If not node then return node_id instead
    # always return string
    def get_node (self):
        if 'node' in self.data:
            return self.data['node']
        return str(self.data['node_id'])
    
    # Always node_id number
    def get_node_id (self):
        return self.data['node_id']
    
    # could be id or friendly name
    def get_event (self):
        if 'event' in self.data:
            return self.data['event']
        return str(self.data['event_id'])
    
    # Always event_id number
    def get_event_id (self):
        return self.data['event_id']
        
    def get_value (self):
        return self.data['value']
        
    # Does this event match
    def matches (self, event):
#         print ("Checking for node")
#         print (f"Self {self.data}")
#         print (f"Event {event.data}")
        if self.get_node() == event.get_node() or self.get_node_id() == event.get_node_id():
            #print (f"Checkng for event_id Self {self.data} Event {event.data}")
            if self.get_event_id() == event.get_event_id() and self.get_value() == event.get_value():
                return True
        return False
        
        
    def __str__ (self):
        return (f"{self.get_type()} {self.get_node()} {self.get_event()} {self.get_value()}")