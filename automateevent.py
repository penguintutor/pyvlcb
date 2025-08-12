# Special events for automation and perhaps logic operations
class AutomateEvent:
    def __init__(self, event_type, data_dict):
        self.event_type = event_type
        self.data = data_dict
        
    def type (self):
        return "Automate"