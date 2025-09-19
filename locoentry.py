import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize


# A simple class to represent a single row for a loco
class LocoEntry(QWidget):
    def __init__(self, loco_id, loco_class, loco_name, loco_image_path, parent=None):
        super().__init__(parent)
        self.loco_id = loco_id
        self.loco_class = loco_class
        self.loco_name = loco_name
        self.loco_image_path = loco_image_path

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(10)
        row_layout.setAlignment(Qt.AlignLeft)

        # Loco ID
        self.id_label = QLabel(f"ID: {loco_id}")
        self.id_label.setFixedWidth(50)
        row_layout.addWidget(self.id_label)

        # Loco Class
        self.class_label = QLabel(loco_class)
        self.class_label.setFixedWidth(120)
        row_layout.addWidget(self.class_label)

        # Loco Name
        self.name_label = QLabel(loco_name)
        self.name_label.setFixedWidth(150)
        row_layout.addWidget(self.name_label)

        # Loco Image
        self.image_label = QLabel()
        pixmap = QPixmap(loco_image_path).scaled(100, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(100, 40)
        row_layout.addWidget(self.image_label)

        # Spacer to push buttons to the right
        row_layout.addStretch(1)

        # Delete Button (Trash Icon)
        self.delete_button = QPushButton()
        self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.delete_button.setFixedSize(QSize(24, 24))
        self.delete_button.clicked.connect(self.show_delete_dialog)
        row_layout.addWidget(self.delete_button)

    def show_delete_dialog(self):
        msg_box = QDialog(self)
        msg_box.setWindowTitle("Confirm Deletion")
        layout = QVBoxLayout(msg_box)
        layout.addWidget(QLabel("Are you sure you want to delete this loco?"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, msg_box)
        buttons.accepted.connect(self.delete_row)
        buttons.rejected.connect(msg_box.reject)
        layout.addWidget(buttons)

        msg_box.exec()

    def delete_row(self):
        print(f"Deleting Loco with ID: {self.loco_id}")
        self.deleteLater()