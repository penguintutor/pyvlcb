# Special events for timer automation
class TimerEvent:
    def __init__(self, event_type, data_dict):
        self.event_type = event_type
        self.data = data_dict
        
    def event_type (self):
        return "Timer"