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
        
    def __str__ (self):
        return (f"{self.data['event_type']} {self.data['node']} {self.data['event']} {self.data['value']}")