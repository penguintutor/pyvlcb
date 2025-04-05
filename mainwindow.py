import os
from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal
from PySide6.QtWidgets import QMainWindow, QTextBrowser
from PySide6.QtUiTools import QUiLoader
import queue

loader = QUiLoader()
basedir = os.path.dirname(__file__)

app_title = "VLCB Console"

class MainWindowUI(QMainWindow):
    
    def __init__(self, requests, responses, commands, status):
        super().__init__()
        self.debug = True
        
        self.requests = requests
        self.responses = responses
        self.commands = commands
        self.status = status
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_responses)
        self.timer.start()
        
        self.ui = loader.load(os.path.join(basedir, "console.ui"), None)
        self.ui.setWindowTitle(app_title)
        
        # File Menu
        self.ui.actionExit.triggered.connect(self.quit_app)
        
        self.setCentralWidget(self.ui)
        self.show()
        
    def check_responses(self):
        print ("Checking for GUI updates")
        # Check status from commands first
        try:
            status_resp = self.status.get_nowait()
        except queue.Empty:
            if self.debug:
                print ("Status queue empty")
        else:
            if self.debug:
                print (f"Status received {status_resp}")
            # Todo add to the console
            
        # Check to see if we have any responses from cbus
        # Do this to clear input queue before sending any new requests
        try:
            response = self.responses.get_nowait()
        except queue.Empty:
            if self.debug:
                print ("Response queue empty")
        else:
            if self.debug:
                print (f"Response received {response}")
            text_response = response.decode("utf-8")
            # Pass the response to the gui console
            self.ui.textLog.append(text_response)
            
        # Todo Handle errors
        
    # Send exit to automate as well as closing app
    def quit_app(self):
        self.commands.put("exit")
        QCoreApplication.quit()