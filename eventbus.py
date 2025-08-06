# Event Driven architecture - EDA
# Bus to handle events
# Also handles event forwarding signals based on registered event associations


from PySide6.QtCore import Qt, QTimer, QObject, Signal, Slot
from deviceevent import DeviceEvent
from appevent import AppEvent
from guievent import GuiEvent
from locoevent import LocoEvent
from automateevent import AutomateEvent

class EventBus(QObject):
    # Generic signals for different event types.
    # The payload of the signal is the event object
    # To register for the event notifications connect to these signals 
    app_event_signal = Signal(AppEvent)
    device_event_signal = Signal(DeviceEvent)
    gui_event_signal = Signal(GuiEvent)
    loco_event_signal = Signal(LocoEvent)
    automate_event_signal = Signal(AutomateEvent)
    
    # Store registered event forwarding rules
    # Each entry contains a list consisting of [event, action]
    event_rules = []

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    # To register an event publish with the appropriate event type
    def publish(self, event):
        if isinstance(event, AppEvent):
            self.app_event_signal.emit(event)
        elif isinstance(event, GuiEvent):
            self.gui_event_signal.emit(event)
        elif isinstance(event, DeviceEvent):
            self.device_event_signal.emit(event)
        elif isinstance(event, LocoEvent):
            self.loco_event_signal.emit(event)
        elif isinstance(event, AutomateEvent):
            self.automate_event_signal.emit(event)
        else:
            print(f"Warning: Unhandled event type published: {type(event)}")

    def add_rule (self, event, action):
        self.event_rules.append (event, action)


# Access the singleton EventBus
event_bus = EventBus()
