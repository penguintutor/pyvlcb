# Abstract class for shared methods in events

import copy

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
    # Added a simple matches method, but should be overridden by subclasses
    def matches(self, other_event):
        # Simple match logic for testing
        # Match if type is the same and value is the same
        return (isinstance(other_event, type(self)) and
                self.event_type == other_event.event_type)

    def __dict__ (self):
        # Create a dict with event_type added
        return_dict = copy.copy(self.data)
        return_dict['event_type'] = self.event_type
        return return_dict

    # Default string - override in relevant sub classes
    def __str__ (self):
        return (f"{self.data['event_type']} {self.data}")

    def __eq__(self, other):
        # Useful for assertions
        return isinstance(other, type(self)) and self.__dict__() == other.__dict__()

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"
    