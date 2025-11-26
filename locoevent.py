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
        "All Stop"		# Special case if using CBUS controller which has all stop
        ]
        
        
        
    
    def __init__(self, event_type, event_data):
        self.event_type = event_type
        self.data = event_data # dict

    def type (self):
        return "Loco"