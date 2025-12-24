# Tracks events against loco
# When we receive / send an event do we need to update devices and corresponding objects
class LocoEvent:
    
    # List of type of events related to locos.
    # As a class variable so it can be used for GUI menus prior to creating event
    event_types = [
        "Set Speed",
        "Set Direction",
        "Stop",
        # Function includes sound etc. In the Loco view these are mapped based on the loco, but in
        # automation then the Loco may be changed and function may differ
        "Function",		# In menu this may be remapped to F1 / F2 etc. - perhaps spinbox
        "All Stop"		# Special case if using CBUS controller which has all stop - still need to have a session with a loco first
        ]
        
    def __init__(self, event_type, event_data):
        self.event_type = event_type
        self.data = event_data # dict

    def type (self):
        return "Loco"
    
    @classmethod
    def get_action_names(cls):
        #print (f"Returning Loco actions {cls.event_types}")
        return cls.event_types
    

    def get_action(self):
        return self.data["action"]
    
    def get_value(self):
        value = self.data.get("value", 0)
    
    def matches (self, event):
        if self.get_type() == event.get_type():
            if self.get_action() == event.get_action() and self.get_value() == event.get_value():
                return True
        return False