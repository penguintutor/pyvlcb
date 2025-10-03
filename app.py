#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from mainwindow import MainWindowUI
from locowindow import LocoWindow
from addlocodialog import AddLocoDialog

class App(QApplication):
    def __init__ (self, args):
        super().__init__()
        
# Windows with dialogs are ones that may lose focus to their dialogs
# Add to this list to ensure their dialogs are kept on top
# These can be mainwindows (such as LocoWindow) or dialogs with subdialogs (eg. AddLocoDialog)
windows_with_dialogs = (LocoWindow, AddLocoDialog)
# Dialogs that need to get raised
dialog_types = (QDialog, QFileDialog, QMessageBox)
    
# We can connect to the QApplication's focusChanged signal
# This allows us to handle focus changes across the entire app
def handle_focus_change(old_focus, new_focus):
    # Check if the newly focused widget belongs to a LocoWindow
    if new_focus and isinstance(new_focus.window(), windows_with_dialogs):
        #print (f"New focus {new_focus.window()}")
        # Find the active application-modal dialog
        for widget in QApplication.topLevelWidgets():
            # Check if the widget is a QDialog and is visible
            if isinstance(widget, dialog_types) and widget.isVisible():
                #print (f"Widget is {widget}")
                # Check for ApplicationModal modality
                if widget.windowModality() == Qt.ApplicationModal:
                    # Manually raise the dialog to the front
                    widget.raise_()
                    widget.activateWindow()
                    # The first dialog window is the last opened
                    # after raising that stop
                    break 
        
# Create QApplication instance 
app = App(sys.argv)

app.setStyle('Fusion')

new_font = QFont("Sans Serif", 10) 
app.setFont(new_font)

# Load and apply QSS file
try:
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
except FileNotFoundError:
    print("Stylesheet file not found.")
except Exception as e:
    print (f"Error stylesheet not loaded {e}")

# Monitor for focus change
app.focusChanged.connect(handle_focus_change)

# Create a Qt widget - main window
window = MainWindowUI()

#Start event loop
app.exec()

# Application end


