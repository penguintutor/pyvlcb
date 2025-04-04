# Provides ability to automate actions
# Also handles the creation of the GUI process and messages between the GUI and the app

from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindowUI
import time
import queue

class VLCBAutomate ():
    def __init__ (self, requests, responses, commands, status):
        
        # Create extra set of queues to communicate with GUI process
        self.gui_requests = Queue()    
        self.gui_responses = Queue()   # Typically these are responses to requests, but could be error / not connected - also copy of requests from automate
        self.gui_commands = Queue()    # These are commands to the server - eg. shutdown / connect on new port
        self.gui_status = Queue()      # Response to commands and/or error messages with CANUSB4

        # create processes
        # process for handling events
        self.gui_process = Process(target=self.start_gui, args=(self.gui_requests, self.gui_responses, self.gui_commands, self.gui_status))
        
        
    def start_gui(self, gui_requests, gui_responses, gui_commands, gui_status):
        app = App()
        window = MainWindowUI(gui_requests, gui_responses, gui_commands, gui_status)
        app.exec()
        #while True:
        #    print ("GUI running")
        #    time.sleep(1)
        
    def run (self):
        self.gui_process.start()
        while True:
            print ("Process running")
            time.sleep(0.5)
            # Run automation here
            pass
        
        
        self.gui_process.join()

class App(QApplication):
    def __init__ (self):
        super().__init__()
        
