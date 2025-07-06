import os
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from layout import Layout
from pyvlcb import VLCB
from loco import Loco
from apihandler import ApiHandler

# Tracks and geneerates events(activities) against a loco
# When we receive / send an event do we need to update devices and corresponding objects
# Currently heavily reliant on mw (mainwindow) from the parent
# perhaps decouple in futures
class ControlLoco:
    def __init__(self, parent, vlcb):
        self.mw = parent
        self.api = parent.api
        self.vlcb = vlcb
        self.loco = Loco()

    def release (self):
        # Release old loco
        if self.loco.status == "on" and self.loco.session != 0:
            # Sends a release but doesn't check for a response
            self.api.start_request(self.vlcb.release_loco(self.loco.session))
            self.loco.released()
            # Normally would want to stop the keep alive but we are hoping to aquire a new session immediately after
            # So the keep alive will just ignore until aquired

    def load_file (self, filename):

        self.loco.load_file (filename)
        loco_name = self.loco.loco_name

        self.mw.ui.locoStatusLabel.setText(f"Aquiring {loco_name}")

        #self.api.start_request(self.vlcb.allocate_loco(self.loco.loco_id))
        # start_request moved away from controlloco
        self.loco.status = 'rloc'
        
        # Add images and summary
        if "image" in self.loco.loco_data:
            loco_image = QPixmap(os.path.join(self.mw.layout.loco_dir, self.loco.loco_data['image']))
            self.mw.ui.locoImage.setPixmap(loco_image)
        else:
            self.mw.ui.locoImage.setPixmap(QPixmap())
        if "summary" in self.loco.loco_data:
            self.mw.ui.locoInfoText.setText(self.loco.loco_data['summary'])
        else:
            self.mw.ui.locoInfoText.setText("")
        
    # Update function selected features
    # When combobox / tab selected
    def function_selected (self, func_index):
        # get [status, type]
        status = self.loco.get_function_status(func_index)
        # If we don't have a status then the function button doesn't exist
        if status == None:
            self.mw.ui.locoFuncButton.setText(" - ")
            return
        # If trigger then button should be activate:
        if status[1] == "trigger":
            self.mw.ui.locoFuncButton.setText("Activate")
        elif status[1] == "latch":
            # if on - button will turn off
            if status[0] == 1:
                self.mw.ui.locoFuncButton.setText ("Turn Off")
            else:
                self.mw.ui.locoFuncButton.setText ("Turn On")
        # Eg if status is none then not supported
        else:
            self.mw.ui.locoFuncButton.setText (" -- ")
            
            
    # Button has been pressed
    def function_pressed (self, func_index):
        # get [status, type]
        status = self.loco.get_function_status(func_index)
        # If we don't have a status then the function doesn't exist
        if status == None:
            return
        
        # If trigger then button should be activate:
        if status[1] == "trigger":
            self.func_trigger (func_index)
            # no need to update button as still say activate
        else:
            # if <= F12 then send multiple times (NRMA standard)
            if func_index <= 12:
                #print (f"Func {func_index}, current {status[0]}, new {1-status[0]}")
                self.func_change (func_index, 1-status[0], 3)
            # otherwise send once
            else:
                self.func_change (func_index, 1-status[0])
            # Update button
            # perhaps separate functions to what is required
            self.mw.loco_function_selected()
            
    def steal_loco (self):
        # Check we have valid loco_id (if not reset)
        if (self.loco.loco_id == 0):
            self.reset_loco()
            return
        loco_id = self.loco.loco_id
        #loco_name = self.loco_list.loco_name(loco_id)
        loco_name = self.loco.loco_name
        self.mw.ui.locoStatusLabel.setText(f"Stealing {loco_name}")
        self.loco.status = 'gloc'
        self.api.start_request(self.vlcb.steal_loco(loco_id))
        
    def share_loco (self):
        # Check we have valid loco_id (if not reset)
        if (self.loco.loco_id == 0):
            self.reset_loco()
            return
        loco_id = self.loco.loco_id
        #loco_name = self.loco_list.loco_name(loco_id)
        loco_name = self.loco.loco_name
        self.mw.ui.locoStatusLabel.setText(f"Req sharing {loco_name}")
        self.api.start_request(self.vlcb.share_loco(loco_id))
        
    # Reset loco selection in GUI and remove references
    def reset_loco (self):
        # remove keep alive timer if active
        if self.api.kalive_timer.isActive():
                self.api.kalive_timer.stop()
        self.loco.reset()
        # Change combo after reset - that way the post change
        # will not send a release message
        self.mw.ui.locoComboBox.setCurrentIndex(0)
        self.mw.ui.locoStatusLabel.setText(f"None active")
        
        
    ### Function change and Function Trigger are tied into QTimer so need to be part of mainwindow
    ### Local functions pass to the main windos
    def func_change (self, func_index, value, num_send = 1, delay = 2):
        self.api.loco_func_change (func_index, value, num_send, delay)
        
    def func_trigger (self, func_index):
         self.api.loco_func_trigger(func_index)
            
    # This is used based on the dial
    def change_speed (self, new_speed):
        # If not in a session then ignore
        if self.loco.is_active():
            # Special case if stop and 0 then reset stop
            if self.loco.status == "stop" and new_speed == 0:
                self.loco.status = "on"
                self.mw.ui.locoStatusLabel.setText ("Ready")
            self.loco.set_speed (new_speed)
            self.api.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.mw.update_lcd()
        
        
    def forward (self):
        self.loco.set_direction (1)
        if self.loco.is_active():
            self.api.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.mw.update_lcd()
        
    def reverse (self):
        self.loco.set_direction (0)
        if self.loco.is_active():
            self.api.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.mw.update_lcd()
        
        
    # Emergency stop - current loco
    # To reset need to set speed to 0 on the dial
    def stop (self, msg="STOP!"):
        self.loco.set_stop()
        if self.loco.session != 0:
            # check we have a session
            # don't check status as this is emergency stop so send regardless
            self.api.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.mw.ui.locoStatusLabel.setText (msg)
        self.mw.update_lcd()
        
    def stop_all (self):
        self.api.start_request(self.vlcb.loco_stop_all())