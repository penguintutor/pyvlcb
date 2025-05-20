import os
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

class StealDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        loader = QUiLoader()
        basedir = os.path.dirname(__file__)
        self.ui = loader.load(os.path.join(basedir, "stealdialog.ui"), None)
        self.setWindowTitle("Loco already taken")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.ui)
        self.setLayout(main_layout)
        #self.open()
        
        self.ui.cancelButton.clicked.connect (self.reject)

    #def reject(self):
    #    self.close()
        