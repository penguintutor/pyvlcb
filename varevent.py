# Tracks events for variables
# This allows monitoring for a variable being a certain value

from event import Event

# Indicates new variable created or change to existing varible
# Dict should contain "name" "value" and "event_type" is new or change
class VarEvent(Event):
    def __init__(self, data_dict):
        self.event_type = "Var"
        self.data = data_dict
        if not 'event_type' in self.data:
            self.data['event_type'] = self.event_type
        
    def event_type (self):
        return "Var"
    
    def get_type (self):
        return "Var"
    
    def get_variable_name (self):
        return self.data["name"]
    
    # Get variable returns name and value as (key, value)
    def get_variable (self):
        return (self.data["name"], self.data["value"])
        
    # Wouldn't normally use this - just use get_variable_name instead
    # Used by __str__ as based on Gui event
    def get_node (self):
        return self.get_variable_name()
    
    # Event would normally be new or change
    def get_event (self):
        if 'event' in self.data:
            return self.data['event']
        else:
            return 0
    
    def get_value (self):
        return self.data['value']
    
    def __str__ (self):
        return (f"{self.get_type()} {self.get_node()} {self.get_event()} {self.get_value()}")