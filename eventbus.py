# Event Driven architecture - EDA
# Bus to handle events
# Also handles event forwarding signals based on registered event associations


from PySide6.QtCore import Qt, QTimer, QObject, Signal, Slot
import json
from event import Event
from deviceevent import DeviceEvent
from appevent import AppEvent
from guievent import GuiEvent
from locoevent import LocoEvent
from automateevent import AutomateEvent

# The serialize_event function must be defined before it is used.
def serialize_event(obj):
    #print (f"Obj {obj}")
    #print (f"Obj type {obj.__class__.__name__}")
    if isinstance(obj, Event):
        #print ("Is instance")
        return obj.__dict__()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def deserialize_event(data):
    return EventBus.event_map[data["event_type"]] (data)



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


    # Map to Classes
    event_map = {
        'Device': DeviceEvent,
        'Loco': LocoEvent,
        'App': AppEvent,
        'Gui': GuiEvent,
        'Automate': AutomateEvent
        }

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
        #print (f"Event {event.__class__.__name__} : Action {action.__class__.__name__}")
        self.event_rules.append([event, action])
        #print (f"Last rule {self.event_rules[-1]}")
        
    def num_rules (self):
        return len(self.event_rules)
    
    # Load rules file must include a filename
    # which is then stored allowing save_rules to be used without a filename
    # filename should be full path - created in mainwindow
    def load_rules (self, filename):
        self.rules_filename = filename
        try:
            with open(self.rules_filename, 'r') as data_file:
                raw_data = json.load(data_file)
                #print (f"Data {new_data}")
                
                self.event_rules = [
                    [deserialize_event(event_data) for event_data in rule_pair]
                    for rule_pair in raw_data
                ]

        except Exception as e:
            # Could be new file
            print (f"File not found {self.rules_filename} - {e}")
        
    
  
    
    def save_rules (self):
        try:
            with open(self.rules_filename, 'w') as data_file:
                #json.dump(self.event_rules, data_file, indent=4)
                json.dump(self.event_rules, data_file, default=serialize_event, indent=4)
                
#                 serialized_rules = [
#                     [serialize_event(event) for event in rule_pair]
#                     for rule_pair in self.event_rules
#                     ]
#                 serialized_rules = []
#                 for rule_group in self.event_rules:
#                     serialized_rules.append([serialize_event(rule_group[0]), serialize_event(rule_group[1])])
                        
                #print (f"serialized_rules {serialized_rules}")
                
                #json.dump(serialized_rules, data_file, indent=4)


        except Exception as e:
            # Could be new file
            print (f"Save failed {self.rules_filename} - {e}")


# Access the singleton EventBus
event_bus = EventBus()
