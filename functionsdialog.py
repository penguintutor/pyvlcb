import sys, os
import re
from PySide6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle, QComboBox, QMessageBox) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from functionentry import FunctionEntry


class FunctionsDialog(QDialog):
       
    def __init__(self, parent, functions=[]):
        super().__init__(parent)
        self.parent = parent
        self.functions = functions
        self.function_entries = []

        self.setWindowTitle("Edit functions")
        self.setFixedSize(600, 400)

        main_layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft)

        header_label = QLabel("Edit functions")
        header_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(header_label)
        
        # Spacer to push button to the right
        header_layout.addStretch(1)

        # Add Function button (top right)
        self.add_function_button = QPushButton("Add Function")
        self.add_function_button.clicked.connect(self.add_function)
        header_layout.addWidget(self.add_function_button, alignment=Qt.AlignTop | Qt.AlignRight)

        
        main_layout.addLayout(header_layout)

        # Scrollable area for function rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.function_list_widget = QWidget()
        self.function_list_layout = QVBoxLayout(self.function_list_widget)
        self.function_list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.function_list_widget)
        main_layout.addWidget(self.scroll_area)

        # Bottom bar with OK button
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.addStretch(1)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self.close)
        bottom_bar_layout.addWidget(self.cancel_button)
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(80, 30)
        self.ok_button.clicked.connect(self.ok_click)
        bottom_bar_layout.addWidget(self.ok_button)

        main_layout.addLayout(bottom_bar_layout)
        
        self.update()

    # Read in the selected filter and add the locos to the display
    def update (self):
        # First clear all existing (option may be to determine whether to keep any but keeping it simple)
        self.clear_function_list ()
        num_functions = len(self.functions)
        for i in range (0, num_functions):
            self.add_function_entry(i, self.functions[i])
        if num_functions < 1:
            # If no functions add a single entry
            self.add_function_entry(num_functions, ["","","",""])
            
            
    def clear_function_list (self):
        layout = self.function_list_layout
        while layout.count():
            # remove from layout
            item = layout.takeAt(0)
            
            #  Set to delete
            if item.widget() is not None:
                widget = item.widget()
                widget.hide()
                widget.deleteLater()
    
    def display (self):
        self.show()
        
    def add_function (self):
        # Add a new entry to the functions
        self.functions.append(["","","",""])
        num_functions = len(self.functions)
        # Add an entry to the GUI
        self.add_function_entry(num_functions, ["","","",""])
        
    
    def add_function_entry(self, id, function={}):
        self.function_entries.append(FunctionEntry(id, function))
        # Add listener to the connect
        #loco_entry.clicked.connect(self.loco_edit)
        self.function_list_layout.addWidget(self.function_entries[-1])
        
    # OK pressed
    # Update self.functions with all the values
    def ok_click (self):
        # clear existing entries
        self.functions = []
        for function_entry in self.function_entries :
            # Read in from entry and add to list
            self.functions.append(function_entry.get_list())
        self.accept()
    
