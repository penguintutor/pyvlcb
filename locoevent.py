# Tracks events against loco
# When we receive / send an event do we need to update devices and corresponding objects
class LocoEvent:
    def __init__(self, event_type, event_data):
        self.event_type = event_type
        self.data = event_data # dict

    def type (self):
        return "Loco"