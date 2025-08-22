import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
    QDialogButtonBox,
    QLineEdit
)
from devicemodel import device_model

class AddButtonDialog(QDialog):
    def __init__(self, object_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Button")
        self.setGeometry(200, 200, 300, 150)
        self.object_names = object_names
        
        #print (f"Parent {parent}")

        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Parent (GuiDevice)
        device_layout = QHBoxLayout()
        device_label = QLabel("Device:")
        self.device_combo = QComboBox()
        self.device_combo.addItem("Select device")
        self.device_combo.addItems(self.object_names)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        main_layout.addLayout(device_layout)
        
        # Button type
        type_layout = QHBoxLayout()
        type_label = QLabel("Button type:")
        self.type_combo = QComboBox()
        #self.type_combo.addItem("None")
        self.type_combo.addItems(["circle", "rectangle"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        main_layout.addLayout(type_layout)

#         # Name layout
#         id_layout = QHBoxLayout()
#         id_label = QLabel("Label ID:")
#         self.node_id_textedit = QLineEdit()
#         id_layout.addWidget(id_label)
#         id_layout.addWidget(self.node_id_textedit)
#         main_layout.addLayout(id_layout)

        # Dialog buttons (OK, Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_selected_values(self):
        # Returns the selected node and event.
        gui_device = self.device_combo.currentText()
        selected_type = self.type_combo.currentText()
        #id_text = self.node_id_textedit.text()
        return [gui_device, selected_type]
