import os
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal
from PySide6.QtWidgets import QMainWindow, QTextBrowser, QTableWidget, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from eventbus import EventBus, event_bus
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
import queue

loader = QUiLoader()
basedir = os.path.dirname(__file__)


class ConsoleWindowUI(QMainWindow):
    
    def __init__(self, mainwindow):
        super().__init__()
        self.debug = False
        self.mainwindow = mainwindow
        
        self.window_title = "VLCB Console"
        
        self.vlcb = VLCB()
        
        # Holds new entries as they are added
        # the UI will then update and remove them
        self.new_entries = []
        
        # Monitor event bus for app updates
        event_bus.app_event_signal.connect (self.app_update)
        
        # Each entry represents a row on the table
        # Each row is a list of the individual entries
        self.console_entries = []
        
        self.ui = loader.load(os.path.join(basedir, "console.ui"), None)
        self.setWindowTitle(self.window_title)
        
        # Set column width for first column to ensure data fits
        self.ui.consoleTable.setColumnWidth(0, 150)
        self.ui.consoleTable.setColumnWidth(2, 200)
        
        # File Menu
        self.ui.actionClose.triggered.connect(self.close_window)
        
        # Command shortcuts
        self.ui.commandSelect.currentIndexChanged.connect (self.command_changed)
        self.ui.scrollCheckBox.toggled.connect (self.scroll_checkbox)
        self.ui.sendCommandButton.clicked.connect (self.send_command)
        self.ui.makeCommandButton.clicked.connect (self.make_command)
        self.ui.arg1Select.currentIndexChanged.connect (self.arg1_changed)
        
        self.setCentralWidget(self.ui)
        
        # Run command changed to setup command combobox
        self.command_changed()
        
    def app_update (self, app_event):
        #print (f"App Event {app_event.data}")
        if app_event.event_type == "newdata":
            self.add_log(app_event.get_response())
            self.update_log()
        if app_event.event_type == "showconsole":
            self.show()
            self.showNormal()
            self.raise_()
            self.activateWindow()
        
    # log_details is unformatted string
    # Extract details and store as:
    # Cbus data (original string), can_id, op_code, data
    def add_log (self, resp_string):
        # If it's blank then ignore
        if resp_string == "":
            return
        self.new_entries.append(resp_string)
        
        
    def update_log (self):
        #print (f"Updating console with {self.new_entries}")
        while len(self.new_entries) > 0:
            resp_string = self.new_entries.pop(0)
            log_details = self.vlcb.log_entry(resp_string)
            # Add new row to the table
            row_num = self.ui.consoleTable.rowCount()
            self.ui.consoleTable.setRowCount(row_num + 1)
            #print (f"Log details : {log_details}")
            for i in range(0, len(log_details)):
                self.ui.consoleTable.setItem(row_num, i, QTableWidgetItem(log_details[i]))
                # Add tooltip with title of opcode
                self.ui.consoleTable.item(row_num, i).setToolTip(VLCBopcode.opcode_title(log_details[3]))
            
        # If in scrollmode then go to the bottom
        if self.ui.scrollCheckBox.isChecked():
            self.ui.consoleTable.scrollToBottom()
        
    # Command pulldown menu (QComboBox)
    # Set the other argument lists
    def command_changed (self):
        command = self.ui.commandSelect.currentText()
        # Commands with no arguments
        if  command == "Discover":
            num_args = 0
        # Commands which need a node id
        elif (command == "Query Node Number Events Configured" or
              command == "Query Node Number Available Events" or
              command == "Query Node Stored Events" ):
            num_args = 1
            # Add nodes to arg1
            self.ui.arg1Select.clear()
            for node_id in sorted(self.mainwindow.nodes.keys()):
                self.ui.arg1Select.addItem(str(node_id))
        # Command that takes node_id, EV ID and State (on/off)
        elif (command == "Accessory Command"):
            num_args = 3
            # Add nodes to arg1
            self.ui.arg1Select.clear()
            self.ui.arg2Select.clear()
            for node_id in sorted(self.mainwindow.nodes.keys()):
                self.ui.arg1Select.addItem(str(node_id))
            # Now call arg1_changed to update next field with EVID
            self.arg1_changed()
        else:
            num_args = 0
        
        # Only show arguments with options
        if num_args < 1:
            self.ui.arg1Select.hide()
        else:
            self.ui.arg1Select.show()
        if num_args < 2:
            self.ui.arg2Select.hide()
        else:
            self.ui.arg2Select.show()
        if num_args < 3:
            self.ui.arg3Select.hide()
        else:
            self.ui.arg3Select.show()
            # It's arg1 that determines if this is needed
            self.arg1_changed()
            self.arg2_changed()

    # This is called by commands that need arg 2 (eg. EVID) and typically arg 3 (On / Off)
    def arg1_changed(self):
        # Set arg 2
        self.ui.arg2Select.clear()
        # first get node_id - to lookup ev id
        node_id = self.arg1_nodeid()
        if node_id == None:
            return
        for ev_id in sorted(self.mainwindow.nodes[node_id].ev.keys()):
            self.ui.arg2Select.addItem(str(ev_id))
        # Assume arg 3 still gives On/Off
            
    # This is called by commands that need arg 3
    # Defaults to On/Off
    def arg2_changed(self):
        pass
    #    # Set arg 3
    #    self.ui.arg3Select.clear()
    #    # first get node_id - to lookup ev id
    #    node_id = self.arg1_nodeid()
    #    if node_id == None:
    #        return
    #    print (f"Node {node_id} + evs {self.mainwindow.nodes[node_id].ev.keys()}")
    #    for ev_id in sorted(self.mainwindow.nodes[node_id].ev.keys()):
    #        self.ui.arg3Select.addItem(str(ev_id))
    #    # Assume arg 3 still gives On/Off
            
            
    # Generate command
    def make_command (self):
        command = self.ui.commandSelect.currentText()
        if command == "Discover":
            self.ui.commandEdit.setText(self.vlcb.discover())
        elif command == "Query Node Number Events Configured":
            node_id = self.arg1_nodeid()
            if node_id == None:
                return
            self.ui.commandEdit.setText(self.vlcb.discover_evn(node_id))
        elif command == "Query Node Number Available Events":
            node_id = self.arg1_nodeid()
            if node_id == None:
                return
            self.ui.commandEdit.setText(self.vlcb.discover_nevn(node_id))
        elif command == "Query Node Stored Events":
            node_id = self.arg1_nodeid()
            if node_id == None:
                return
            self.ui.commandEdit.setText(self.vlcb.discover_nerd(node_id))
        elif (command == "Accessory Command"):
            node_id = self.arg1_nodeid()
            if node_id == None:
                return
            ev_id = self.arg2_evid()
            if ev_id == None:
                return
            state_str = self.ui.arg3Select.currentText()
            if state_str == "On":
                state_str = "on"
            elif state_str == "Off":
                state_str = "off"
            else:
                return
            self.ui.commandEdit.setText(self.vlcb.accessory_command(node_id, ev_id, state_str))
            
            
        
    # Get nodeid from argument 1
    def arg1_nodeid (self):
        try :
            node_str = self.ui.arg1Select.currentText()
            node_id = int(node_str)
            # If no node_id, or it's not a number return
        except:
            return None
        # Also check number is not negative or too large
        if node_id < 0 or node_id > 65535:
            return None
        return node_id
    
    # Get ev_id from argument 2
    def arg2_evid (self):
        try :
            ev_str = self.ui.arg2Select.currentText()
            ev_id = int(ev_str)
            # If no node_id, or it's not a number return
        except:
            return None
        # Also check number is not negative or too large
        if ev_id < 0 or ev_id > 65535:
            return None
        return ev_id
            
    # Uses main window to send the contents of commandEdit
    def send_command (self):
        # If no string then ignore
        command_string = self.ui.commandEdit.text()
        if command_string == "":
            return
        self.mainwindow.api.start_request(command_string)
        
    # Update checkbox wording
    def scroll_checkbox (self):
        if self.ui.scrollCheckBox.isChecked():
            self.ui.scrollCheckBox.setText("Scroll on ")
        else:
            self.ui.scrollCheckBox.setText("Scroll off")
        
    # Close actually hides so we can continue to capture logs
    def close_window(self):
        self.hide()