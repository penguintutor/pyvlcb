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
from timerevent import TimerEvent

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
    timer_event_signal = Signal(TimerEvent)
    
    # Is automation enabled. If not then don't apply rules.
    # If excessive calls (eg. excessive recursion) then stop automatically
    automation_enabled = True
    
    # Track number of automation events
    automation_count = 0
    max_automation_count = 100
    
    # Store registered event forwarding rules
    # Each entry contains a list consisting of [event, action]
    event_rules = []


    # Map to Classes
    event_map = {
        'VLCB': DeviceEvent,
        'Device': DeviceEvent,
        'Loco': LocoEvent,
        'App': AppEvent,
        'Gui': GuiEvent,
        'Timer': TimerEvent
        }

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    # Publish is used to send an event notification which originates in the application
    # It can be called by other classes (eg. GUI notification)
    # It first calls apply_rules which will trigger an rule events
    # then broadcsts to the appropriate signal
    # To register an event publish with the appropriate event type
    def publish(self, event):
        # Apply automation rules by consuming the input
        self.consume(event)
        # broadcast the signal
        self.broadcast(event)
        
    
    # Broadcast signal
    def broadcast(self, event):
        # Broadcast the event
        if isinstance(event, AppEvent):
            self.app_event_signal.emit(event)
        elif isinstance(event, GuiEvent):
            self.gui_event_signal.emit(event)
        elif isinstance(event, DeviceEvent):
            self.device_event_signal.emit(event)
        elif isinstance(event, LocoEvent):
            self.loco_event_signal.emit(event)
        elif isinstance(event, TimerEvent):
            self.timer_event_signal.emit(event)
        else:
            print(f"Warning: Unhandled event type published: {type(event)}")
        
    # Consume is used to handle incoming events
    # It does not publish a new event
    # Called directly from CBUS events, or as part of publish to act as a consumer
    def consume(self, event):
        # Apply automation rules
        # (includes internal mapping - eg. from CBUS to gui)
        if self.automation_enabled:
            self.apply_rules (event)

    def del_entry (self, rule_id):
        del self.event_rules[rule_id]

    # Apply automation rules based on the event
    def apply_rules (self, event):
        # Add number of events
        self.automation_count += 1
        #print (f"Num automation {self.automation_count}")
        # Have we reached maximum
        if self.automation_count >= self.max_automation_count:
            print ("*** Warning automation events exceeded ***")
            # Todo call a gui event to notify userrr
            self.automation_enabled = False
            # Allowed to continue for this event, but then stop
        
        # Get the event type to save making multiple calls to type method
        event_type = type(event)
        #print (f"Applying rules for {event}")
        # Apply across all rules
        #print (f"Event {event}")
        for rule in self.event_rules:
            #print (f"Event rules {self.event_rules}")
            # rule[0] is the event we are monitoring for
            if isinstance(rule[0], event_type):
                #print (f"Rule matches type {event_type} - {rule[0]}")
                # Matches same type pass to the event to see if this matches
                # This allows each event type to look for certain features
                if rule[0].matches(event):
                    # Print number automation events in queue along with details of matching event
                    #print (f"{self.automation_count} - Match {event}")
                    #self.publish (rule[1])
                    # Broadcast rather than publish
                    # Automation will be received from the incoming deviceevent
                    self.broadcast (rule[1])
        # Decrement once rules applied
        self.automation_count -= 1

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
            #print (f"File not found {self.rules_filename} - {e}")
            print (f"File not found {self.rules_filename}")
        

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
