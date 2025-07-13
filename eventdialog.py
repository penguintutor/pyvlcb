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
)
from devicemodel import device_model

class EventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Event Selection")
        self.setGeometry(200, 200, 300, 150)

#         self.data = {
#             "Node A": ["Event 1A", "Event 2A", "Event 3A"],
#             "Node B": ["Event 1B", "Event 2B"],
#             "Node C": ["Event 1C", "Event 2C", "Event 3C", "Event 4C"],
#         }

        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Node selection layout
        node_layout = QHBoxLayout()
        node_label = QLabel("Select Node:")
        self.node_combo = QComboBox()
        self.node_combo.addItem("None")
        self.node_combo.addItems(device_model.get_nodes_names())
        node_layout.addWidget(node_label)
        node_layout.addWidget(self.node_combo)
        main_layout.addLayout(node_layout)

        # Event selection layout
        event_layout = QHBoxLayout()
        event_label = QLabel("Select Event:")
        self.event_combo = QComboBox()
        event_layout.addWidget(event_label)
        event_layout.addWidget(self.event_combo)
        main_layout.addLayout(event_layout)

        # Connect the node combo box to update the event combo box
        self.node_combo.currentIndexChanged.connect(self.update_event_combo)

        # Initialize the event combo box with events for the first node
        self.update_event_combo(0) # Call with index 0 to populate initially

        # Dialog buttons (OK, Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def update_event_combo(self, index):
        # Updates the event_combo based on the selected node.
        selected_node = self.node_combo.currentText()
        if selected_node == "None":
            events = "NA"
        else:
            node_key = device_model.name_to_key(selected_node)
            events = device_model.get_events(node_key)
        self.event_combo.clear()
        self.event_combo.addItems(events)

    def get_selected_values(self):
        # Returns the selected node and event.
        selected_node = self.node_combo.currentText()
        selected_event = self.event_combo.currentText()
        return selected_node, selected_event
