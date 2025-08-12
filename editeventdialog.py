import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget
)
from PySide6.QtCore import Qt
from devicemodel import device_model
from eventbus import event_bus

class EditEventDialog(QDialog):
    """
    A dialog window for editing event details with a grid layout for selections.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Event Details")
        self.setMinimumSize(600, 200) # Set a reasonable minimum size for the dialog

        # Main vertical layout for the dialog
        main_layout = QVBoxLayout(self)

        # Create the grid layout for event selections
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(20, 20, 20, 20) # Add some padding around the grid
        grid_layout.setSpacing(10) # Set spacing between grid cells

        # --- Grid Headers (Labels) ---
        # Column Headers (Top Row)
        column_headers = ["Event", "Action", "Options"]
        for i, header_text in enumerate(column_headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter) # Center align the text
            grid_layout.addWidget(label, 0, i + 1) # Row 0, columns 1, 2, 3

        # Row Headers (Left Column)
        row_headers = ["Node", "Event", "Value"]
        for i, header_text in enumerate(row_headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter) # Right align, vertically center
            grid_layout.addWidget(label, i + 1, 0) # Column 0, rows 1, 2, 3

        # --- Grid Content (QComboBoxes) ---
        # Populate the 3x3 grid with QComboBoxes
        self.selection_comboboxes = {} # Dictionary to store references to comboboxes
        for row in range(3):
            for col in range(3):
                combo_box = QComboBox()
                #combo_box.addItems([f"Select {row+1}-{col+1}", "Choice 1", "Choice 2", "Choice 3"])
                grid_layout.addWidget(combo_box, row + 1, col + 1)
                # Store reference for potential later access (e.g., getting selected values)
                self.selection_comboboxes[f"row{row}_col{col}"] = combo_box

        # Populate Event combo boxes
        self.selection_comboboxes["row0_col0"].addItem("Select Node")
        self.selection_comboboxes["row0_col0"].addItems(device_model.get_nodes_names())
        # Connect the event node combo box to update the event combo box
        self.selection_comboboxes["row0_col0"].currentIndexChanged.connect(self.update_event_combo)
        # Connect the event event combo box to update the state combo box
        self.selection_comboboxes["row1_col0"].currentIndexChanged.connect(self.update_event_state_combo)
        
        # Populate Action combo boxes
        self.selection_comboboxes["row0_col1"].addItem("Select Node")
        self.selection_comboboxes["row0_col1"].addItems(device_model.get_nodes_names())
        # Connect the event node combo box to update the event combo box
        self.selection_comboboxes["row0_col1"].currentIndexChanged.connect(self.update_action_combo)
        # Connect the event event combo box to update the state combo box
        self.selection_comboboxes["row1_col1"].currentIndexChanged.connect(self.update_action_state_combo)

        main_layout.addWidget(grid_widget) # Add the grid widget to the main layout

        # --- OK / Cancel Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch(1) # Pushes buttons to the right

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept) # Connect OK button to accept dialog
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject) # Connect Cancel button to reject dialog
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout) # Add the button layout to the main layout

    def get_selected_values(self):
        """
        Retrieves the currently selected values from all QComboBoxes in the grid.
        Returns a 2D dict using 'event', 'action', 'options'
        which is a dict of 'node', 'event', 'value'
        """
        # created empty dictionaries of the 3 columns
        selected_values = {'event':{}, 'action':{}, 'options': {}}
        # Currently keys are 'rowX_colY' and values are the selected text.
        #for key, combo_box in self.selection_comboboxes.items():
        #    selected_values[key] = combo_box.currentText()
        selected_values['event']['node'] = self.selection_comboboxes["row0_col0"].currentText()
        selected_values['event']['event'] = self.selection_comboboxes["row1_col0"].currentText()
        selected_values['event']['value'] = self.selection_comboboxes["row2_col0"].currentText()
        selected_values['action']['node'] = self.selection_comboboxes["row0_col1"].currentText()
        selected_values['action']['event'] = self.selection_comboboxes["row1_col1"].currentText()
        selected_values['action']['value'] = self.selection_comboboxes["row2_col1"].currentText()
        # todo
        # options not yet implemented as it depends upon the action Event
        return selected_values


    def update_event_combo(self, index):
        self.selection_comboboxes["row1_col0"].clear()
        # Updates the event_combo based on the selected node.
        selected_node = self.selection_comboboxes["row0_col0"].currentText()
        if selected_node == "None":
            events = ["NA"]
        else:
            node_key = device_model.name_to_key(selected_node)
            events = device_model.get_events(node_key)
            if events == []:
                events = ["NA"]
        self.selection_comboboxes["row1_col0"].addItems(events)
        
    
    def update_event_state_combo(self):
        self.selection_comboboxes["row2_col0"].clear()
        # For this just check that there is an event
        # If it's not "" or "NA" then it should have an on or off status
        # Default to on events
        selected_event = self.selection_comboboxes["row1_col0"].currentText()
        if selected_event == "NA" or selected_event == "":
            self.selection_comboboxes["row2_col0"].addItem("NA")
        else:
            self.selection_comboboxes["row2_col0"].addItem("On")
            self.selection_comboboxes["row2_col0"].addItem("Off")
        

    def update_action_combo(self, index):
        self.selection_comboboxes["row1_col1"].clear()
        # Updates the event_combo based on the selected node.
        selected_node = self.selection_comboboxes["row0_col1"].currentText()
        if selected_node == "None":
            events = ["NA"]
        else:
            node_key = device_model.name_to_key(selected_node)
            events = device_model.get_events(node_key)
            if events == []:
                events = ["NA"]
        self.selection_comboboxes["row1_col1"].addItems(events)
        
    
    def update_action_state_combo(self):
        self.selection_comboboxes["row2_col1"].clear()
        # For this just check that there is an event
        # If it's not "" or "NA" then it should have an on or off status
        # Default to on events
        selected_event = self.selection_comboboxes["row1_col1"].currentText()
        if selected_event == "NA" or selected_event == "":
            self.selection_comboboxes["row2_col1"].addItem("NA")
        else:
            self.selection_comboboxes["row2_col1"].addItem("On")
            self.selection_comboboxes["row2_col1"].addItem("Off")
        
