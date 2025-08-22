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

class AddLabelDialog(QDialog):
    def __init__(self, object_names, parent=None):
        super().__init__(parent)
        self.object_names = object_names
        self.setWindowTitle("New Label")
        self.setGeometry(200, 200, 300, 150)
        
        # ID field is usually updated based on label text, but if user changes then no longer track
        # Only if new entry - existing probably don't want to change
        self.custom_id = False 

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
        
        # Label Text
        node_layout = QHBoxLayout()
        node_label = QLabel("Label Text:")
        self.node_label_textedit = QLineEdit()
        node_layout.addWidget(node_label)
        node_layout.addWidget(self.node_label_textedit)
        main_layout.addLayout(node_layout)

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
        
## No longer need id as based on guidevice so comment out
#         # Connect signals (to autocreate node_id)
#         self.node_label_textedit.textChanged.connect(self.on_label_text_changed)
#         # Connect textEdited for node_id_textedit to detect user modification
#         self.node_id_textedit.textEdited.connect(self.on_id_text_edited)
#         
#     def on_label_text_changed(self, text):
#         # Slot to handle text changes in self.node_label_textedit.
#         if not self.custom_id:
#             # Transform the text: replace spaces with '_' and append '_label'
#             transformed_text = text.replace(" ", "_") + "_label"
#             self.node_id_textedit.setText(transformed_text)
#             
#     def on_id_text_edited(self, text):
#         # Slot to set the flag if self.node_id_textedit is modified by the user.
#         # Once the user edits node_id_textedit, we stop auto-updating it
#         if not self.custom_id:
#             self.custom_id = True
#             #print("node_id_textedit has been modified by the user.")

    def get_selected_values(self):
        # Returns the selected node and event.
        gui_device = self.device_combo.currentText()
        node_text = self.node_label_textedit.text()
        #id_text = self.node_id_textedit.text()
        return [gui_device, node_text]
