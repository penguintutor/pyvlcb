import os
from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal
from PySide6.QtWidgets import QMainWindow, QTextBrowser
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()
basedir = os.path.dirname(__file__)

app_title = "VLCB Console"

class MainWindowUI(QMainWindow):
    
    def __init__(self, requests, responses, commands, status):
        super().__init__()
        
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
        
    # Send exit to automate as well as closing app
    def quit_app(self):
        self.commands.put("exit")
        QCoreApplication.quit()