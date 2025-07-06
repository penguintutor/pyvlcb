# Event Driven architecture - EDA
# Bus to handle events


from PySide6.QtCore import Qt, QTimer, QObject, Signal, Slot
from deviceevent import DeviceEvent
from layoutevent import LayoutEvent



class EventBus(QObject):
    # Generic signals for different event types.
    # The payload of the signal is the event object 
    device_event_signal = Signal(DeviceEvent)
    layout_event_signal = Signal(LayoutEvent)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance
    
    def __init__ (self):
        return None
        self.device_event_signal.connect (self.device_event_trigger)
        self.layout_event_signal.connect (self.layout_event_trigger)

    def publish(self, event):
        if isinstance(event, DeviceEvent):
            self.device_event_trigger.emit(event)
        elif isinstance(event, LayoutEvent):
            self.layout_event_trigger.emit(event)
        # Add more event types here
        else:
            print(f"Warning: Unhandled event type published: {type(event)}")
            
    def device_event_trigger (self, event):
        pass
    
    def layout_event_trigger (self, event):
        pass

# Access the singleton EventBus
event_bus = EventBus()
