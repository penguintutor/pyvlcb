import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, Signal, QEvent
from devicemodel import device_model


# A simple class to represent a single row for a loco
class LocoEntry(QWidget):
    
    # If this object is clicked (perform an edit)
    clicked = Signal(QWidget)
    
    def __init__(self, loco_id, loco_name, loco_image_path, filename, parent=None):
        super().__init__(parent)
        self.locowin = parent
        self.loco_id = loco_id
        #self.loco_class = loco_class
        self.loco_name = loco_name
        self.loco_image_path = loco_image_path
        self.filename = filename		# filename provides a unique id

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(10)
        row_layout.setAlignment(Qt.AlignLeft)

        # Loco ID
        self.id_label = QLabel(f"ID: {loco_id}")
        self.id_label.setFixedWidth(70)
        row_layout.addWidget(self.id_label)

        # Loco Name
        self.name_label = QLabel(loco_name)
        self.name_label.setFixedWidth(350)
        row_layout.addWidget(self.name_label)

        # Spacer to push buttons to the right
        row_layout.addStretch(1)

        # Loco Image
        self.image_label = QLabel()
        pixmap = QPixmap(loco_image_path).scaled(100, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(100, 40)
        row_layout.addWidget(self.image_label)

        # Enabled checkbox
        self.enable_label = QLabel("Enable")
        row_layout.addWidget(self.enable_label)
        self.enable_checkbox = QCheckBox()
        self.enable_checkbox.checkStateChanged.connect(self.enable_disable)
        row_layout.addWidget(self.enable_checkbox)

#         # Delete Button (Trash Icon)
#         self.delete_button = QPushButton()
#         self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
#         self.delete_button.setFixedSize(QSize(24, 24))
#         self.delete_button.clicked.connect(self.show_delete_dialog)
#         self.delete_button.setProperty("class", "showicon") # Set a class so that the stylesheet shows theicon
#         row_layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignVCenter)

    # If clicked then update enabled list
    def enable_disable(self):
        # note that our saved filename is full path - so just get the basename
        basename = os.path.basename(self.filename)
        if self.enable_checkbox.isChecked():
            device_model.enable_loco(basename)
        else:
            device_model.disable_loco(basename)
        # Send updated signal
        # locowin locowindow, parent is mainwindow
        self.locowin.parent.updated_locos_signal.emit()
        # also tell mainwindow to save settings
        self.locowin.parent.save_settings_signal.emit()

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

    # Watch for a mouse press event to allow editing an entry
    def mousePressEvent(self, event):
        # Exclude the enabled label and checkbox
        # Get the rectangle of the label, relative to LocoEntry
        label_rect = self.enable_label.geometry()
        # Get the rectangle of the checkbox, relative to LocoEntry
        checkbox_rect = self.enable_checkbox.geometry()
        # Combine the rects into one excluded area
        excluded_rect = label_rect.united(checkbox_rect)
        
        # Check if the click position is inside the excluded area
        if excluded_rect.contains(event.pos()):
            # Toggle the checkbox
            self.enable_checkbox.toggle()
            # If the click is on the excluded area, ignore the event 
            # to prevent it from triggering the LocoEntry.clicked signal.
            event.ignore()
            return
        
        # If not the excluded area then emit a signal that this is clicked
        # This is picked up by LocoWindow to initiate edit dialog
        self.clicked.emit(self)
        
        # IMPORTANT: Call the base class implementation
        super().mousePressEvent(event)