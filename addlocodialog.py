import os
import shutil
from pathlib import Path
from PySide6.QtCore import Qt, Signal, Slot, QFile
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from imageexistdialog import ImageExistDialog

# Dialog to get details about a loco
# Also allows upload of an image
# If image is already in locos directory then just add reference to it
# if not and file doesn't exist then copies to the locosdir
# if it does exist then dialog to rename or overwride
# locos directory is required for images

# These are the main GUI elements
# displayTextEdit
# dccIdEdit
# classEdit
# classNameEdit
# nameEdit
# numberEdit
# locoTypeCombo
# origRailwayEdit
# liveryRailwayEdit
# originalYearEdit
# liveryYearEdit
# wheelsEdit
# modelManufEdit
# decoderEdit
# summaryText
# imageLabel / self.default_pixmap / self.image_filename
        
class AddLocoDialog(QDialog):
    
    def __init__(self, parent, locos_dir):
        super().__init__(parent)
        self.gui = parent
        self.locosdir = locos_dir
        self.loco_id = None	# Set here when accept so no need to recalculate
        self.image_filename = ""
        #self.setModal(True)
        loader = QUiLoader()
        basedir = os.path.dirname(__file__)
        ui_filename = os.path.join(basedir, "addlocodialog.ui")
        ui_file = QFile (ui_filename)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, None)
        ui_file.close()
        self.setWindowTitle("Add New Loco")
        # Layout is set in the QT designer to GridLayout
        self.setLayout(self.ui.layout())
        
        # handle button clicks
        self.ui.buttonBox.accepted.connect (self.accept_click)
        self.ui.buttonBox.rejected.connect (self.cancel)
        self.ui.uploadImageButton.clicked.connect (self.upload_image)
        
                
        # Appears to be a bug relating to the focus
        # Set to the first widget
        self.ui.displayTextEdit.setFocus()
        
        self.set_default_image()
        

    # set default image on preview
    def set_default_image(self):
        image_preview_label = self.ui.imageLabel
        if image_preview_label:
            image_filename = os.path.join(self.locosdir, "default.png")
            self.default_pixmap = QPixmap(image_filename)
            if not self.default_pixmap.isNull():
                image_preview_label.setPixmap(self.default_pixmap.scaled(
                    image_preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                image_preview_label.setText("Default image not found.")


    # Upload and save the image
    def upload_image(self):
        file_dialog = QFileDialog(self,
                        caption="Select Image",
                        directory=self.locosdir,
                        filter="Images (*.png *.jpg *.jpeg *.bmp)",
                        fileMode=QFileDialog.FileMode.ExistingFile
                        )

        # Get filename
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            #print (f"Selected file {selected_file}")
            # later we will save just filename into self.image_filename
            filename = os.path.basename(selected_file)
            
            # Is the file in the locosdir
            if self.is_locosdir(selected_file):
                #print (f"{filename} in data directory")
                self.image_filename = filename
            # if not and doesn't exist in locosdir then copy
            else:
                # New path - includes filename
                new_path = os.path.join(self.locosdir, filename)
                if not (os.path.exists(new_path)):
                    shutil.copyfile (selected_file, new_path)
                    # Todo wrap above in try clause
                    self.image_filename = filename
                # File is not in locos directory and already matching file
                # Create new dialog to get new filename
                # Todo implement this
                else:
                    exist_dialog = ImageExistDialog (self, self.locosdir)
                    if exist_dialog.exec() == QDialog.Accepted:
                        # Handle dialog response here
                        # saved in self.dialog.action
                        if exist_dialog.action == "overwrite":
                            # copy over existing
                            shutil.copyfile (selected_file, new_path)
                            self.image_filename = filename
                        elif exist_dialog.action == "existing":
                            # just use the current filename
                            self.image_filename = filename
                        # For new file to be selected then we should have already checked
                        # that the filename is valid
                        elif exist_dialog.action == "save":
                            self.image_filename = exist_dialog.ui.filenameEdit.text()
                            new_path = os.path.join(self.locosdir, self.image_filename)
                            #print (f"Copying {selected_file} to {new_path}")
                            shutil.copyfile (selected_file, new_path)
                        else:
                            # Unknown state
                            return
                    # Most likely cancel pressed just ignore
                    else:
                        return
                
            
            # Update the preview with the new image
            #image_preview_label = self.ui_widget.findChild(QLabel, "image_preview_label")
            image_preview_label = self.ui.imageLabel
            if image_preview_label:
                pixmap = QPixmap(os.path.join(self.locosdir, self.image_filename))
                if not pixmap.isNull():
                    image_preview_label.setPixmap(pixmap.scaled(
                        image_preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    ))

   
   # check if a filepath is in the locosdir
    def is_locosdir(self, filepath):
        #print (f"Checking {filepath} in {self.locosdir}")
        try:
            #filepath = Path(filepath).resolve()
            #print (f"Filepath {filepath} {filepath.parent}")
            dir = os.path.dirname(filepath)
            return dir == self.locosdir
        except Exception as e:
            print(f"Error checking path: {e}")
            return False


    def accept_click (self):
        # Validate mandatory fields

        
        # loco_id (DCC ID) must exist
        # It should also be unique - but only when active not when created
        # This allows guest locos with same ID but not to be on the track
        # at the same time.
        
        # Check the DCCID is included and is a number
        dcc_id_text = self.ui.dccIDEdit.text()
        try:
            dcc_id_value = int(dcc_id_text)
        # Any errors warn and do not accept (submit)
        except:
            QMessageBox.warning(
                self, 
                "Input Error", # The title of the dialog
                "Please enter a valid number for a DCC ID." # The message content
            )
            return
        if (dcc_id_value < 1 or dcc_id_value > 9999):
            QMessageBox.warning(
                self,
                "Input Error", # The title of the dialog
                "DCC ID must be between 1 and 9999." # The message content
            )
            return
        
        # Store the loco_id so that it can be retrieved
        self.loco_id = dcc_id_value
        self.accept()
    
        
    def cancel(self):
        self.reject()

        