import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindowUI

class App(QApplication):
    def __init__ (self, args):
        super().__init__()
        
# Create QApplication instance 
app = App(sys.argv)

# Create a Qt widget - main window
window = MainWindowUI()

#Start event loop
app.exec()

# Application end