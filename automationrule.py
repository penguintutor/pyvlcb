
from devicemodel import device_model
from eventbus import event_bus

# Automation rule determines the actions
# Name is just a user friendly name for the step - does not need to be unique but helpful if it is
# Eg. Activate point 1, or Set Loco 1 speed 3
# Type is rule category - that could be
# Loco, VLCB, App, Gui, Timer etc.
# data is a dict with any additional parameters
# eg. data['loco_id'] is used if the rule controls a loco
# For all others then it needs to be all the parameters for the Event etc.
# For loco_id - must have already been converted to the actual DCC ID
# Done when the sequence is first activated (eg. request from user)
# Flow is not included in the rule - that must be done at a higher level
class AutomationRule:
    
# The event_map is taken from device_model.event_map
#     event_map = {
#         'VLCB': DeviceEvent,		# This should be used in preference to Device
#         'Device': DeviceEvent,
#         'Loco': LocoEvent,
#         'App': AppEvent,
#         'Gui': GuiEvent,
#         'Timer': TimerEvent
#         }
    
    
    
    def __init__ (self, rule_name, rule_type, data):
        self.name = rule_name
        self.type = rule_type
        self.data = data
        
        # Create the corresponding event
        self.event = device_model.event_map[self.type](self.data)
        
        
    # Runs the action
    def run (self):
        # Assuming this is an event then broadcast to event_bus
        event_bus.broadcast(self.event)
    
    def __repr__(self):
        return (f"Rule {self.rule_type}, {self.data}")
    
