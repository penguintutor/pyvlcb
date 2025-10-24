# Tracks events for app - open, close, update windows
# Used to update api objects from events

from event import Event

class AppEvent (Event):
    def __init__(self, data_dict={}):
        self.event_type = "App"
        self.data = data_dict
        self.action = self.data['action']
        
    def type (self):
        return "App"
           
    def get_response(self):
        if "response" in self.data.keys():
            return self.data['response']
        else:
            return ""