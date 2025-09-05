# Abstract class for shared methods in events

class Event:
    def __init__(self):
        # Set here but override in sub class
        if not hasattr(self, 'data'):
            self.data = {"event_type":"unknown"}
        
    # Allow event_type or get_type to allow consistancy
    def event_type(self):
        return self.data["event_type"]
    def get_type(self):
        return self.data["event_type"]

    
#     def serialize_event(self):
#         if isinstance(self, Event):
#             return self.__dict__
#         raise TypeError(f'Object of type {self.__class__.__name__} is not JSON serializable')

    # This is temporary whilst implementing different event types
    # each event type must implement to see if the event matches the current event
    def matches(self, event):
        # Not supported for this event type
        print (f"Event {self.data['event_type']} not implemented matches")
        return False

    def __dict__ (self):
        #print (f"Returning dict {self.data}")
        return self.data

    # Default string - override in relevant sub classes
    def __str__ (self):
        return (f"{self.data['event_type']} {self.data}")

    
    