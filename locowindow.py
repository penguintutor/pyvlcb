import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from locoentry import LocoEntry


class LocoWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Loco Manager")
        self.setFixedSize(600, 400)

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

        # Examples
        self.add_loco_entry("0001", "A3 Class", "Flying Scotsman", "loco_image.png")
        self.add_loco_entry(2, "A4 Class", "Mallard", "loco_image.png")
        self.add_loco_entry(3, "Coronation Class", "Duchess of Sutherland", "loco_image.png")
        self.add_loco_entry(4, "A3 Class", "Flying Scotsman", "loco_image.png")

        
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

    def open_add_loco_dialog(self):
        print("Add new loco")
        # A custom QDialog would be instantiated and shown here.
        # Example: add_dialog = AddLocoDialog(self)
        #          add_dialog.exec()
