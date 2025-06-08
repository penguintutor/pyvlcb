import os
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal
from PySide6.QtWidgets import QMainWindow, QTextBrowser, QTableWidget, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
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
        
        self.setCentralWidget(self.ui)
        
        # Run command changed to setup command combobox
        self.command_changed()
        
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
            self.ui.arg2Select.unhide()
        if num_args < 3:
            self.ui.arg3Select.hide()
        else:
            self.ui.arg3Select.unhide()

            
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
            
    # Uses main window to send the contents of commandEdit
    def send_command (self):
        # If no string then ignore
        command_string = self.ui.commandEdit.text()
        if command_string == "":
            return
        self.mainwindow.start_request(command_string)
        
    # Update checkbox wording
    def scroll_checkbox (self):
        if self.ui.scrollCheckBox.isChecked():
            self.ui.scrollCheckBox.setText("Scroll on ")
        else:
            self.ui.scrollCheckBox.setText("Scroll off")
        
    # Close actually hides so we can continue to capture logs
    def close_window(self):
        self.hide()