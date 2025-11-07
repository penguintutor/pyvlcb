# Tracks events for graphics objects
# If a GUI object (including layout needs to trigger request then use this)
# Used by layout objects and other GUI objects (eg. console window)

# 'name': self.name, 'value': self.state_value

from event import Event

class GuiEvent(Event):
    def __init__(self, data_dict):
        self.event_type = "Gui"
        self.data = data_dict
        if not 'event_type' in self.data:
            self.data['event_type'] = self.event_type
        
    def event_type (self):
        return "Gui"
    
    def get_type (self):
        return "Gui"
    
    def get_node (self):
        if 'node' in self.data:
            return self.data['node']
        return "Gui node"
    
    def get_event (self):
        if 'event' in self.data:
            return "Gui event"
        else:
            return 0
    
    def get_value (self):
        if "value" in self.data:
            return self.data['value']
        else:
            return "None"
    
    def __str__ (self):
        return (f"{self.get_type()} {self.get_node()} {self.get_event()} {self.get_value()}")