import os
from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal
from PySide6.QtWidgets import QMainWindow, QTextBrowser
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader
import queue
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from consolewindow import ConsoleWindowUI

loader = QUiLoader()
basedir = os.path.dirname(__file__)

app_title = "VLCB App"

class MainWindowUI(QMainWindow):
    
    def __init__(self, requests, responses, commands, status):
        super().__init__()
        self.debug = False
        
        self.requests = requests
        self.responses = responses
        self.commands = commands
        self.status = status
        
        self.nodes = {} # dict of nodes indexed by NN
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_responses)
        self.timer.start()
        
        # VLCB and node creation
        self.vlcb = VLCB()
        
        self.ui = loader.load(os.path.join(basedir, "mainwindow.ui"), None)
        self.setWindowTitle(app_title)
        
        # File Menu
        self.ui.actionExit.triggered.connect(self.quit_app)
        
        # Asset Menu
        self.ui.actionDiscover.triggered.connect(self.discover)
        
        # Tree view
        #self.ui.nodeTreeView.setColumnCount(3)
        #self.ui.setHeaderLabels(['Name', 'Number', 'Type'])
        self.node_model = QStandardItemModel()
        self.node_model.setHorizontalHeaderLabels(['Name', 'Number', 'Type'])
        self.ui.nodeTreeView.setModel(self.node_model)
        
        self.setCentralWidget(self.ui)
        self.ui.nodeTreeView.show()
        self.show()
        self.create_console()
        
        
        # Initial discover request
        self.discover()
        
    def create_console(self, show=True):
        self.console_window = ConsoleWindowUI(self)
        if show:
            self.console_window.show()
        
    def check_responses(self):
        #print ("Checking for GUI updates")
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
            self.console_window.add_log(text_response)
            # Check if we need to handle this further
            self.handle_incoming (text_response)
            
        # Todo Handle errors
        
    # This method is called whenever we get a valid response
    # Used to determine if further action is required (eg. discovery or update status)
    # Note this will see all cbus messages, including ones sent to/from other nodes
    def handle_incoming (self, response):
        vlcb_entry = self.vlcb.parse_input(response)
        # If not a valid entry then ignore
        if vlcb_entry == False:
            return
        # Look for specific responses
        if vlcb_entry.opcode() == 'PNN':    # PNN (Response to query node)
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # if we don't already have this device add it
            if not data_entry['NN'] in self.nodes.keys():
                self.nodes[data_entry['NN']] = VLCBNode(data_entry['NN'], data_entry['ManufId'], data_entry['ModId'] ,data_entry['Flags'])
                # Add to Tree View
                print ("Adding entry")
                node = QStandardItem(f"Unknown, {data_entry['NN']}, {vlcb_entry.can_id}")
                self.node_model.appendRow(node)
                
            else:
                # Update existing entry
                pass
            
        
    def discover (self):
        self.requests.put(self.vlcb.discover())
        
    # Send exit to automate as well as closing app
    def quit_app(self):
        self.commands.put("exit")
        QCoreApplication.quit()