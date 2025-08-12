# Tracks events for app - open, close, update windows
# Used to update api objects from events
class AppEvent:
    def __init__(self, event_type, data_dict={}):
        self.event_type = event_type
        self.data = data_dict
        
    def type (self):
        return "App"
        
    def get_response(self):
        if "response" in self.data.keys():
            return self.data['response']
        else:
            return ""