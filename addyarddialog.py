from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
)
from PySide6.QtCore import Qt


class AddYardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add New Yard")
        self.setFixedSize(300, 100)
        # Set the window flag to keep the dialog on top
        #self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # Set the dialog to be modal right here in the initializer
        #self.setModal(True)
        # Set the window to be application-modal
        self.setWindowModality(Qt.ApplicationModal)

        # Variable to store the new yard name
        self.new_yard = None

        # Main layout
        main_layout = QVBoxLayout(self)

        # Input field
        self.yard_name_edit = QLineEdit()
        self.yard_name_edit.setPlaceholderText("Enter yard name")
        main_layout.addWidget(QLabel("Yard Name:"))
        main_layout.addWidget(self.yard_name_edit)

        # OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        main_layout.addWidget(self.button_box)

        # Connect signals
        self.button_box.accepted.connect(self.accept_input)
        self.button_box.rejected.connect(self.reject)

    def accept_input(self):
        """
        Retrieves the text from the line edit and stores it.
        """
        self.new_yard = self.yard_name_edit.text()
        self.accept()