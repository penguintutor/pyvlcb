# Event Driven architecture - EDA
# 


from PySide6.QtCore import Qt, QTimer, QObject



class EventBus(QObject):
    # Generic signals for different event types.
    # The payload of the signal is the event object 
    device_event_trigger = Signal(DeviceEvent)
    layout_event_trigger = Signal(LayoutEvent)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    def publish(self, event):
        if isinstance(event, DeviceEvent):
            self.device_event_trigger.emit(event)
        elif isinstance(event, LayoutEvent):
            self.layout_event_trigger.emit(event)
        # Add more event types here
        else:
            print(f"Warning: Unhandled event type published: {type(event)}")

# Access the singleton EventBus
event_bus = EventBus()
