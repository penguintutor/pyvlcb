import os
from PySide6.QtCore import Qt, Signal, Slot, QFile
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

# loco directory is required for images
class AddLocoDialog(QDialog):
    
    def __init__(self, parent, locos_dir):
        super().__init__(parent)
        self.gui = parent
        self.locosdir = locos_dir
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
        self.ui.buttonBox.accepted.connect (self.accept)
        self.ui.buttonBox.rejected.connect (self.cancel)
        #self.ui.cancelButton.clicked.connect (self.cancel)
        #self.ui.stealButton.clicked.connect (self.steal)
        #self.ui.shareButton.clicked.connect (self.share)
        
        self.set_default_image()
        

    # set default image on preview
    def set_default_image(self):
        #image_preview_label = self.ui_widget.findChild(QLabel, "image_preview_label")
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
        

    def accept (self):
        # Validate any mandatory fields
        self.accept()
    
        
    def cancel(self):
        self.reject()

        