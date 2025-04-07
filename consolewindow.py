import os
from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal
from PySide6.QtWidgets import QMainWindow, QTextBrowser, QTableWidget, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from pyvlcb import VLCB
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
        
        # Each entry represents a row on the table
        # Each row is a list of the individual entries
        self.console_entries = []
        
        self.ui = loader.load(os.path.join(basedir, "console.ui"), None)
        self.ui.setWindowTitle(self.window_title)
        
        # File Menu
        self.ui.actionClose.triggered.connect(self.close_window)
        
        # Command shortcuts
        self.ui.commandSelect.currentIndexChanged.connect (self.command_changed)
        self.ui.scrollCheckBox.toggled.connect (self.scroll_checkbox)
        self.ui.sendCommandButton.clicked.connect (self.send_command)
        
        self.setCentralWidget(self.ui)
        # Don't show - allows console to be created but not displayed
        # Call show manually to open the windo
        #self.show()
        
    # log_details is list with fields:
    # Cbus data (original string), can_id, op_code, data
    def add_log (self, log_details):
        # Add new row to the table
        row_num = self.ui.consoleTable.rowCount()
        self.ui.consoleTable.setRowCount(row_num + 1)
        # Add empty list to next position in list
        self.console_entries.append([])
        this_row = self.console_entries[-1]
        for i in range(0, len(log_details)):
            this_row.append(QTableWidgetItem(log_details[i]))
            self.ui.consoleTable.setItem(row_num, i, this_row[i])
            
        # If in scrollmode then go to the bottom
        if self.ui.scrollCheckBox.isChecked():
            self.ui.consoleTable.scrollToBottom()
        
    # Command pulldown menu (QComboBox)
    def command_changed (self):
        if self.ui.commandSelect.currentText() == "Discover":
            self.ui.commandEdit.setText(self.vlcb.discover())
            
    # Uses main window to send the contents of commandEdit
    def send_command (self):
        # If no string then ignore
        command_string = self.ui.commandEdit.text()
        if command_string == "":
            return
        self.mainwindow.requests.put(command_string)
        
    # Update checkbox wording
    def scroll_checkbox (self):
        if self.ui.scrollCheckBox.isChecked():
            self.ui.scrollCheckBox.setText("Scroll on ")
        else:
            self.ui.scrollCheckBox.setText("Scroll off")
        
    # Close actually hides so we can continue to capture logs
    def close_window(self):
        self.hide()