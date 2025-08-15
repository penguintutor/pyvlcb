# Abstract class for shared methods in events

class Event:
    def __init__(self):
        # Set here but override in sub class
        self.data = {"event_type":"unknown"}
        
    def type(self):
        #return self.event_type
        return self.data["event_type"]
    
#     def serialize_event(self):
#         if isinstance(self, Event):
#             return self.__dict__
#         raise TypeError(f'Object of type {self.__class__.__name__} is not JSON serializable')

    def __dict__ (self):
        #print (f"Returning dict {self.data}")
        return self.data

    # Default string - override in relevant sub classes
    def __str__ (self):
        return (f"{self.data['event_type']} {self.data}")

    
    