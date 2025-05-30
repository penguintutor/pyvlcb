import os
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

class StealDialog(QDialog):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.gui = parent
        self.setModal(True)
        loader = QUiLoader()
        basedir = os.path.dirname(__file__)
        self.ui = loader.load(os.path.join(basedir, "stealdialog.ui"), None)
        self.setWindowTitle("Loco already taken")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.ui)
        self.setLayout(main_layout)
        # handle button clicks
        self.ui.cancelButton.clicked.connect (self.cancel)
        self.ui.stealButton.clicked.connect (self.steal)
        self.ui.shareButton.clicked.connect (self.share)
        
    def steal (self):
        self.gui.steal_loco_signal.emit()
        self.accept()
        
    def share (self):
        self.gui.share_loco_signal.emit()
        self.accept()
    
        
    def cancel(self):
        # Send signal to reset gui selection
        self.gui.reset_loco_signal.emit()
        self.reject()

        