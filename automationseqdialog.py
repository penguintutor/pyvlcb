# Dialog for creating a new AutomationSequence.

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget, QFormLayout, QLineEdit, QSpinBox 
)
from PySide6.QtCore import Qt
from automationrule import AutomationRule
from automationsequence import AutomationStep, AutomationSequence
from automationstepdialog import AutomationStepDialog

class AutomationSeqDialog(QDialog):
    def __init__(self, parent, sequence=None):
        super().__init__(parent)
        self.parent = parent
        self.mainwindow = self.parent.mainwindow
        self.setWindowTitle("Automation Sequence")
        self.sequence = sequence # For editing, if passed
        self.steps = [] # Stores list of AutomationStep objects
        
        self._setup_ui()
        if sequence:
            self.load_sequence_data(sequence)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Title and Loco Count
        title_layout = QFormLayout()
        self.title_input = QLineEdit()
        self.num_locos_spinbox = QSpinBox()
        self.num_locos_spinbox.setRange(0, 3)
        self.num_locos_spinbox.setValue(0)
        title_layout.addRow("Sequence Title:", self.title_input)
        title_layout.addRow("Locos Required:", self.num_locos_spinbox)
        main_layout.addLayout(title_layout)

        main_layout.addWidget(QLabel("Automation Steps"))
        
        # Step List (for displaying the steps)
        self.steps_list = QListWidget()
        main_layout.addWidget(self.steps_list)

        # Controls for Steps
        step_control_layout = QHBoxLayout()
        self.add_step_button = QPushButton("Add Step")
        self.edit_step_button = QPushButton("Edit Step")
        self.remove_step_button = QPushButton("Remove Step")
        step_control_layout.addWidget(self.add_step_button)
        step_control_layout.addWidget(self.edit_step_button)
        step_control_layout.addWidget(self.remove_step_button)
        main_layout.addLayout(step_control_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("Save Sequence")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_sequence)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        main_layout.addLayout(button_box)
        
        # Connections
        self.add_step_button.clicked.connect(self.add_edit_step)
        self.edit_step_button.clicked.connect(lambda: self.add_edit_step(edit=True))
        self.remove_step_button.clicked.connect(self.remove_step)

    # Step Management Logic
    
    # Refreshes the list widget with the current steps
    def _update_steps_list(self):
        self.steps_list.clear()
        for i, step in enumerate(self.steps):
            #rule_count = len(step.rules)
            #mode = step.execution_mode.capitalize()
            #print (f"Step {step}")
            self.steps_list.addItem(f"Step {i+1} ({step['name']})")

    # Opens a sub-dialog to create or edit an AutomationStep.
    def add_edit_step(self, edit=False):
        current_step = None
        current_index = -1
        if edit:
            current_index = self.steps_list.currentRow()
            if current_index < 0:
                QMessageBox.warning(self, "Error", "Please select a step to edit.")
                return
            current_step = self.steps_data[current_index]

        # Use a sub-dialog (StepCreationDialog) for complexity of rule building
        dialog = AutomationStepDialog(self, self.num_locos_spinbox.value(), current_step)
        if dialog.exec() == QDialog.Accepted:
            new_step = dialog.get_step()
            if edit:
                self.steps_data[current_index] = new_step
            else:
                self.steps.append(new_step)
            self._update_steps_list()

    def remove_step(self):
        selected_row = self.steps_list.currentRow()
        if selected_row >= 0:
            del self.steps_data[selected_row]
            self._update_steps_list()
        else:
            QMessageBox.warning(self, "Error", "Please select a step to remove.")
            
    # --- Finalization Logic ---

    def save_sequence(self):
        """Finalizes the sequence creation and accepts the dialog."""
        title = self.title_input.text().strip()
        num_locos = self.num_locos_spinbox.value()

        if not title:
            QMessageBox.warning(self, "Error", "Please enter a sequence title.")
            return

        if not self.steps:
            QMessageBox.warning(self, "Error", "The sequence must contain at least one step.")
            return

        self.sequence = AutomationSequence(self.mainwindow, title, self.steps, {'num_locos': num_locos})
        super().accept()

    def get_sequence(self):
        return self.sequence