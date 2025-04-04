import os
from multiprocessing import Lock, Process, Queue, current_process
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QTextBrowser
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()
basedir = os.path.dirname(__file__)

app_title = "VLCB Console"

class MainWindowUI(QMainWindow):
    
    def __init__(self, requests, responses, commands, status):
        super().__init__()
        
        self.ui = loader.load(os.path.join(basedir, "console.ui"), None)
        self.ui.setWindowTitle(app_title)
        
        self.setCentralWidget(self.ui)
        self.show()