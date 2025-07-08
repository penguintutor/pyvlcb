# Event Driven architecture - EDA
# Bus to handle events


from PySide6.QtCore import Qt, QTimer, QObject, Signal, Slot
from deviceevent import DeviceEvent
from guievent import GuiEvent
from appevent import AppEvent



class EventBus(QObject):
    # Generic signals for different event types.
    # The payload of the signal is the event object
    # To register for the event notifications connect to these signals 
    device_event_signal = Signal(DeviceEvent)
    gui_event_signal = Signal(GuiEvent)
    app_event_signal = Signal(AppEvent)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    # To register an event publish with the appropriate event type
    def publish(self, event):
        if isinstance(event, DeviceEvent):
            self.device_event_signal.emit(event)
        elif isinstance(event, GuiEvent):
            self.gui_event_signal.emit(event)
        elif isinstance(event, AppEvent):
            self.app_event_signal.emit(event)
        # Add more event types here
        else:
            print(f"Warning: Unhandled event type published: {type(event)}")


# Access the singleton EventBus
event_bus = EventBus()
