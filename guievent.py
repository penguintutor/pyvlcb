# Tracks events for graphics objects
# If a GUI object (including layout needs to trigger request then use this)
# Used by layout objects and other GUI objects (eg. console window)
class GuiEvent:
    def __init__(self, event_type, data_dict):
        self.event_type = event_type
        self.data = data_dict
        
    def type (self):
        return "Gui"