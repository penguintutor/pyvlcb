#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from mainwindow import MainWindowUI
from locowindow import LocoWindow

class App(QApplication):
    def __init__ (self, args):
        super().__init__()
        
    
# We can connect to the QApplication's focusChanged signal
# This allows us to handle focus changes across the entire app
def handle_focus_change(old_focus, new_focus):
    # Check if the newly focused widget belongs to a LocoWindow
    if new_focus and isinstance(new_focus.window(), LocoWindow):
        # Find the active application-modal dialog
        for widget in QApplication.topLevelWidgets():
            # Check if the widget is a QDialog and is visible
            if isinstance(widget, QDialog) and widget.isVisible():
                # Check for ApplicationModal modality
                if widget.windowModality() == Qt.ApplicationModal:
                    # Manually raise the dialog to the front
                    widget.raise_()
                    widget.activateWindow()
                    break # We found and raised the dialog, so we can stop
        
# Create QApplication instance 
app = App(sys.argv)

# Monitor for focus change
app.focusChanged.connect(handle_focus_change)

# Create a Qt widget - main window
window = MainWindowUI()

#Start event loop
app.exec()

# Application end


