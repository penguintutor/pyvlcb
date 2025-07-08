import os
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from layout import Layout
from pyvlcb import VLCB
from loco import Loco
from apihandler import ApiHandler
from devicemodel import DeviceModel, device_model


# Tracks and generates events(activities) against a loco
# When we receive / send an event do we need to update devices and corresponding objects
# Currently heavily reliant on mw (mainwindow) from the parent
# perhaps decouple in futures
class ControlLoco:
    def __init__(self):
        # Index is the position in the list in the device_model
        # Create new loco in device_model and get index
        # For interactive this is normally position 0
        self.loco_index = device_model.add_loco()
        # loco moved to devicemodel

        
    def is_active(self):
        return device_model.locos[self.loco_index].is_active()
    
    def get_direction(self):
        return device_model.locos[self.loco_index].direction
    
    def speed_value(self):
        return device_model.locos[self.loco_index].speed_value()
    
    def get_name(self):
        return device_model.locos[self.loco_index].loco_name
    
    # Id is the loco id (eg DCC/running number) not index
    def get_id(self):
        #print (f"Loco index {self.loco_index} id {device_model.locos[self.loco_index].loco_id} name {device_model.locos[self.loco_index].loco_name}")
        return device_model.locos[self.loco_index].loco_id
    
    def is_aquiring(self):
        return device_model.locos[self.loco_index].is_aquiring
    
    def get_session (self):
        return device_model.locos[self.loco_index].session
    
    def set_session (self, session):
        device_model.locos[self.loco_index].session = session
    
    # Sets speed and direction together
    def set_speeddir (self, speeddir):
        device_model.locos[self.loco_index].set_speeddir(speeddir)
        
    def get_speeddir (self):
        return device_model.locos[self.loco_index].get_speeddir()
    
    def get_functions (self):
        return device_model.locos[self.loco_index].get_functions()
    
    def set_functions (self, fn1, fn2, fn3):
        device_model.locos[self.loco_index].set_functions(fn1, fn2, fn3)
        
    def get_function_status (self, func_index):
        # get [status, type]
        return (device_model.locos[self.loco_index].get_function_status(func_index))
    
    # This is the low level status - perhaps use is_aquiring or a similar method instead
    def get_status (self):
        return device_model.locos[self.loco_index].status
    
    def set_status (self, value):
        device_model.locos[self.loco_index].set_status(value)
        
    def set_function_dfun (self, func_index, value):
        # for a list need brackets around the method - or store in temp variable
        return (device_model.locos[self.loco_index].set_function_dfun (func_index, value))

        
    def function_reset (self):
        device_model.locos[self.loco_index].function_reset()

    def release (self):
        # Release old loco
        if device_model.locos[self.loco_index].status == "on" and device_model.locos[self.loco_index].session != 0:
            # Sends a release but doesn't check for a response
            #event_bus.publish(GuiEvent("start_request", {'command': 'release_loco', 'arg1': device_model.locos[self.loco_index].session}))
            # Seperate request for GUI elements
            device_model.locos[self.loco_index].released()
            # Normally would want to stop the keep alive but we are hoping to aquire a new session immediately after
            # So the keep alive will just ignore until aquired

        
    # Update function selected features
    # When combobox / tab selected
    def function_selected (self, func_index):
        # get [status, type]
        status = device_model.locos[self.loco_index].get_function_status(func_index)
        # If we don't have a status then the function button doesn't exist
        if status == None:
            return (" - ")
        # If trigger then button should be activate:
        if status[1] == "trigger":
            return ("Activate")
        elif status[1] == "latch":
            # if on - button will turn off
            if status[0] == 1:
                return ("Turn Off")
            else:
                return ("Turn On")
        # Eg if status is none then not supported
        else:
            return (" -- ")
            
            
    def steal_loco (self):
        # Check we have valid loco_id (if not reset)
        if (device_model.locos[self.loco_index].loco_id == 0):
            self.reset_loco()
            return ""
        loco_id = device_model.locos[self.loco_index].loco_id
        #loco_name = device_model.locos[self.loco_index]_list.loco_name(loco_id)
        loco_name = device_model.locos[self.loco_index].loco_name
        device_model.locos[self.loco_index].status = 'gloc'
        return (f"Stealing {loco_name}")
        
    def share_loco (self):
        # Check we have valid loco_id (if not reset)
        if (device_model.locos[self.loco_index].loco_id == 0):
            self.reset_loco()
            return ""
        loco_id = device_model.locos[self.loco_index].loco_id
        loco_name = device_model.locos[self.loco_index].loco_name
        return (f"Req sharing {loco_name}")
        
        
    # Reset loco selection in GUI and remove references
    def reset_loco (self):
        device_model.locos[self.loco_index].reset()
        # Send keepalive signal
        #event_bus.publish(AppEvent("keepalive", {'loco_id': self.loco_id}))
        # Change combo after reset - that way the post change
        # will not send a release message
        
    ### Function change and Function Trigger are tied into QTimer so need to be part of mainwindow
    # This is used based on the dial
    # Returns True if the loco is active - else false
    def change_speed (self, new_speed):
        # If not in a session then ignore
        if device_model.locos[self.loco_index].is_active():
            # Special case if stop and 0 then reset stop
            if device_model.locos[self.loco_index].status == "stop" and new_speed == 0:
                device_model.locos[self.loco_index].status = "on"
            device_model.locos[self.loco_index].set_speed (new_speed)
            return True
        return False
        
        
    def forward (self):
        device_model.locos[self.loco_index].set_direction (1)
        if device_model.locos[self.loco_index].is_active():
            return True
        return False
        
    def reverse (self):
        device_model.locos[self.loco_index].set_direction (0)
        if device_model.locos[self.loco_index].is_active():
            return True
        return False
        
        
    # Emergency stop - current loco
    # To reset need to set speed to 0 on the dial
    def stop (self, msg="STOP!"):
        device_model.locos[self.loco_index].set_stop()
        if device_model.locos[self.loco_index].session != 0:
            # check we have a session
            # don't check speed as this is emergency stop so send regardless
            return True
        return False
        
    # Same as a stop as far as ControlLoco is concerned
    def stop_all (self):
        self.stop()
