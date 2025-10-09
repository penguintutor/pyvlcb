import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle, QLineEdit, QComboBox) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, Signal, QEvent


# A simple class to represent a single row for a loco
class FunctionEntry(QWidget):
    
    # If this object is clicked (perform an edit)
    #clicked = Signal(QWidget)
    
    def __init__(self, function_id, function=["","","",""], parent=None):
        super().__init__(parent)
        self.function_id = function_id
        self.function = function

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(10)
        row_layout.setAlignment(Qt.AlignLeft)

        # Function ID
        self.id_label = QLabel(f"ID: {function_id}")
        self.id_label.setFixedWidth(70)
        row_layout.addWidget(self.id_label)

        # Function reference [0]
        self.function_ref_edit = QLineEdit ()
        # If blank then set to Fx
        if self.function[0] == "":
            self.function[0] = f"F{function_id}"
        self.function_ref_edit.setText(self.function[0])
        self.function_ref_edit.setToolTip("Button ref. normally Fx")
        self.function_ref_edit.setFixedWidth(70)
        row_layout.addWidget(self.function_ref_edit)

        # Function description [1]
        self.function_desc_edit = QLineEdit ()
        self.function_desc_edit.setText(self.function[1])
        self.function_desc_edit.setToolTip("Action (eg. Sound)")
        self.function_desc_edit.setFixedWidth(100)
        row_layout.addWidget(self.function_desc_edit)
        
        # Function type (eg. "none", "trigger", "toggle") [2]
        self.function_type_combo = QComboBox()
        self.function_type_combo.addItems(["None", "Latch", "Trigger"])
        self.function_type_combo.setToolTip("Latch toggles on and off, trigger activates briefly.")
        # When saved they are lower case so setCurrentText needs first char as cap
        if (self.function[2] != ""):
            self.function_type_combo.setCurrentText(self.function[2].capitalize())
        row_layout.addWidget(self.function_type_combo)


        # Function comment [3]
        self.function_comment_edit = QLineEdit ()
        self.function_comment_edit.setText(self.function[3])
        self.function_comment_edit.setToolTip("Comments")
        self.function_comment_edit.setFixedWidth(100)
        row_layout.addWidget(self.function_comment_edit)
        
    # Return a list with the current values
    # No checks the mainwindows has some error handling for invalid values
    def get_list (self):
        return  [
            self.function_ref_edit.text(),
            self.function_desc_edit.text(),
            self.function_type_combo.currentText().lower(),
            self.function_comment_edit.text()
            ]
            
            

    
