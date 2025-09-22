import sys
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle, QComboBox, QMessageBox) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from locoentry import LocoEntry
from addyarddialog import AddYardDialog
from devicemodel import device_model 


class LocoWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setWindowTitle("Loco Manager")
        self.setFixedSize(650, 400)
        
        # List containing filenames holding the loco info
        # and whether it is enabled or not (filename, enabled
        self.loco_files = []

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft)

        header_label = QLabel("Manage Locos")
        header_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(header_label)

        # Spacer to push add button to the right
        header_layout.addStretch(1)
        
        # Yard selection button
        self.yard_label = QLabel("Yard: ")
        header_layout.addWidget(self.yard_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        self.yard_selection_combo = QComboBox()
        self.yard_selection_combo.setMinimumWidth(100)
        self.yard_selection_combo.addItems(device_model.get_yard_list())
        header_layout.addWidget(self.yard_selection_combo, alignment=Qt.AlignTop | Qt.AlignLeft)
        
        header_layout.addSpacing (60)

        # Add Yard button (top right)
        self.add_yard_button = QPushButton("Add Yard")
        self.add_yard_button.clicked.connect(self.open_add_yard_dialog)
        header_layout.addWidget(self.add_yard_button, alignment=Qt.AlignTop | Qt.AlignRight)

        # Add Loco button (top right)
        self.add_loco_button = QPushButton("Add Loco")
        self.add_loco_button.clicked.connect(self.open_add_loco_dialog)
        header_layout.addWidget(self.add_loco_button, alignment=Qt.AlignTop | Qt.AlignRight)

        main_layout.addLayout(header_layout)

        # Scrollable area for loco rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.loco_list_widget = QWidget()
        self.loco_list_layout = QVBoxLayout(self.loco_list_widget)
        self.loco_list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.loco_list_widget)
        main_layout.addWidget(self.scroll_area)

        # Bottom bar with OK button
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.addStretch(1)
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(80, 30)
        self.ok_button.clicked.connect(self.close)
        bottom_bar_layout.addWidget(self.ok_button)

        main_layout.addLayout(bottom_bar_layout)
        
        # references to dialogs (so we can keep them on top)
        self.dialog = None
        # Watch if he dialog loses focus
        #self.parent.windowActivated.connect(self.raise_dialog)

#         # Examples
#         self.add_loco_entry("0001", "A3 Class", "Flying Scotsman", "loco_image.png")
#         self.add_loco_entry(2, "A4 Class", "Mallard", "loco_image.png")
#         self.add_loco_entry(3, "Coronation Class", "Duchess of Sutherland", "loco_image.png")
#         self.add_loco_entry(4, "A3 Class", "Flying Scotsman", "loco_image.png")

        
    def update (self):
        pass
    
    def display (self):
        self.show()
    
    # Gets summary from file
    def load_file (self, filename):
        with open(filename, 'r') as data_file:
            loco_data = json.load(data_file)
        loco_id = self.loco_data["address"]
        loco_name = self.loco_data["display-name"]


    def add_loco_entry(self, loco_id, loco_class, loco_name, loco_image_path):
        loco_entry = LocoEntry(loco_id, loco_class, loco_name, loco_image_path)
        self.loco_list_layout.addWidget(loco_entry)
    
    # Converts a string of text into a valid filename.
    # Replaces spaces with underscores and removes or replaces characters
    # that are not allowed in most common file systems.
    def title_to_filename(self, text):
        # Replace spaces with underscores
        filename = text.replace(' ', '_')

        # Remove characters that are generally not allowed in filenames.
        # The regex pattern [^\w\s\-] matches any character that is NOT a word
        # character (alphanumeric and underscore), whitespace, or a hyphen.
        # The underscore replacement in the first step is why we want to keep
        # the underscore in the valid characters here.
        filename = re.sub(r'[^\w\.\-]', '', filename)
        filename = filename.lower() + ".json"
        return filename

    def open_add_yard_dialog(self):
        self.dialog = AddYardDialog(self)
        #self.parent.windowActivated.connect(self.raise_dialog)
        
        # Show the dialog and wait for user input
        if self.dialog.exec() == QDialog.Accepted:
            # The OK button was pressed
            if self.dialog.new_yard:
                # New yard name is title
                new_yard = self.dialog.new_yard
                # create filename
                filename = self.title_to_filename(new_yard)
            else:
                QMessageBox.warning(self, "Invalid Input", "The yard name cannot be empty.")
                return
        else:
            # Cancel button pressed or dialog closed
            return
        # Check yard doesn't exist
        if (device_model.check_yard_exist(filename)):
            QMessageBox.warning(self, "Warning", "The yard already exists.")
            return
        else:
            # create the new yard
            device_model.add_yard (new_yard, filename)
            # Add it to the combobox
            self.yard_selection_combo.addItem(new_yard)



    def open_add_loco_dialog(self):
        print("Add new loco")
        # A custom QDialog would be instantiated and shown here.
        # Example: add_dialog = AddLocoDialog(self)
        #          add_dialog.exec()
        
    
#     # If the dialog (add yard or add loco) loses focus then raise
#     def raise_dialog(self):
#         print ("Raise")
#         # Check if the dialog exists and is visible before raising it
#         if self.dialog and self.dialog.isVisible():
#             print (f"Raising dialog {self.dialog}")
#             self.dialog.raise_()
#             self.dialog.activateWindow()
