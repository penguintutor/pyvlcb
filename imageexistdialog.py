import os
from pathlib import Path
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

class ImageExistDialog(QDialog):
    
    def __init__(self, parent, locos_dir):
        super().__init__(parent)
        self.gui = parent
        self.locosdir = locos_dir
        self.setModal(True)
        loader = QUiLoader()
        basedir = os.path.dirname(__file__)
        self.ui = loader.load(os.path.join(basedir, "imageexistdialog.ui"), None)
        self.setWindowTitle("Image already exists")
        self.setLayout(self.ui.layout())
        # Save action selected
        self.action = None
        # Set the saveButton as default - it will prompt if not given a new name
        self.ui.saveButton.setDefault(True)
        # Set message text to blank but  red
        self.ui.messageLabel.setText("")
        self.ui.messageLabel.setStyleSheet("color: red;")
        # handle button clicks
        self.ui.cancelButton.clicked.connect (self.cancel)
        self.ui.existingButton.clicked.connect (self.existing)
        self.ui.overwriteButton.clicked.connect (self.overwrite)
        self.ui.saveButton.clicked.connect (self.save)
        
    def existing (self):
        self.action = "existing"
        self.accept()
        
    def overwrite (self):
        self.action = "overwrite"
        self.accept()
    
    # save with new name
    # first check that it's now a valid name (not already exist)
    def save (self):
        # perform checks to see if the save should be accepted or not
        filename = self.ui.filenameEdit.text()
        if filename == "":
            self.ui.messageLabel.setText("New filename is required for save")
            return
        # also check that there are no path characters
        elif not self.is_just_filename (filename):
            self.ui.messageLabel.setText("Filename should not include path")
            return
        else:
            # Now check file doesn't exist
            new_path = os.path.join(self.locosdir, filename)
            if os.path.exists(new_path):
                self.ui.messageLabel.setText("File already exists use new filename")
                return
                
        # Reach here then passed above tests
        self.action = "save"
        self.accept()
        
    def cancel(self):
        self.reject()

        
    # Checks for simple filename without path
    def is_just_filename (self, filename):
        if not filename:
            return False
        
        # Use pathlib for checking
        file_path = Path(filename)
        
        if file_path.is_absolute():
            return False
        
        # If doesn't have a path then parent will be '.'
        return str(file_path.parent) == '.'