# Provides ability to automate actions
# Also handles the creation of the GUI process and messages between the GUI and the app

from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindowUI
import time
import queue

class VLCBAutomate ():
    def __init__ (self, requests, responses, commands, status):
        self.debug = False
        self.requests = requests
        self.responses = responses
        self.commands = commands
        self.status = status
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

    # This 
    def run (self):
        self.gui_process.start()
        while True:
            if self.debug:
                print ("Checking loop")
            # First check if any commands from the gui
            # those normally take priority, but only send one at a time as otherwise could
            # result in not clearing any off the status and/or response queue
            try:
                gui_command = self.gui_commands.get_nowait()
            except queue.Empty:
                if self.debug:
                    print ("Queue empty")
                pass
            else:
                if self.debug:
                    print (f"Command received {gui_command}")
                # If quit pass on to the app, then break out of the loop
                # If app has already closed then this will meet join at the end
                if gui_command == "quit" or gui_command == "exit":
                    self.commands.put("exit")
                    break
                # for other commands then pass through to the app
                else:
                    self.commands.put(command)
                    pass
            
            if self.debug:
                print ("Any status")
            # Check for any responses to commands these should be approx 1:1 so don't need to keep polling
            try:
                current_status = self.status.get_nowait()
            except queue.Empty:
                if self.debug:
                    print ("Status empty")
            else:
                # print any response received
                if self.debug:
                    print (f"Status {current_status}")
            
            # Check to see if we have any responses 
            # Do this to clear input queue before sending any new requests
            try:
                response = self.responses.get_nowait()
            except queue.Empty:
                if self.debug:
                    print ("Response queue empty")
            else:
                if self.debug:
                    print (f"Response received {response}")
                # Pass the response to the gui
                self.gui_responses.put(response)
            # Todo Handle errors
            
            if self.debug:
                print ("Any requests")
            # Do we have a request from the gui to send out?
            # If so send it now
            try:
                gui_request = self.gui_requests.get_nowait()
                # If it's a string convert to bytestring
                if isinstance(gui_request, str):
                    gui_request = gui_request.encode('utf-8')
            except queue.Empty:
                pass
            else:
                if self.debug:
                    print(f"Sending {gui_request}")
                self.requests.put(gui_request)
                # Also echo to gui_responses
                self.gui_responses.put(gui_request)
                
            # Todo check if we have any of our own requests to send out
            
            
            # Short sleep to reduce number of checks
            time.sleep(0.5)

        if self.debug:
            print ("Automate loop closed")
        self.gui_process.join()

class App(QApplication):
    def __init__ (self):
        super().__init__()
        
