# Dialog to display, add, edit, and run automation sequences

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget
)
from PySide6.QtCore import Qt
from automationadddialog import AutomationAddDialog


class AutomationManagerDialog(QDialog):
    
    def __init__(self, sequences: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Automation Rule Manager")
        self.sequences = sequences
        self.parent_window = parent

        self._setup_ui()
        self._update_list()

    def _setup_ui(self):
        self.setLayout(QVBoxLayout())
        
        # Rule List
        self.rule_list = QListWidget()
        self.layout().addWidget(self.rule_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Rule Sequence")
        self.run_button = QPushButton("Run Selected")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.close_button = QPushButton("Close")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.close_button)
        
        self.layout().addLayout(button_layout)

        # Connections
        self.add_button.clicked.connect(self.add_sequence)
        self.run_button.clicked.connect(self.run_selected_sequence)
        self.close_button.clicked.connect(self.accept)
        # Note: Edit/Delete connections would be similar to add, updating self.sequences and re-running _update_list

    def _update_list(self):
        """Refreshes the list widget with current sequences."""
        self.rule_list.clear()
        for seq in self.sequences:
            self.rule_list.addItem(f"{seq.title} ({seq.num_locos} Locos)")
        self.rule_list.setCurrentRow(0)

    def add_sequence(self):
        """Opens the rule creation dialog."""
        dialog = AutomationAddDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            new_sequence = dialog.get_sequence()
            self.sequences.append(new_sequence)
            self._update_list()
            QMessageBox.information(self, "Success", f"Sequence '{new_sequence.title}' created.")

    def run_selected_sequence(self):
        """Triggers the run process in the main window."""
        selected_row = self.rule_list.currentRow()
        if selected_row >= 0:
            selected_sequence = self.sequences[selected_row]
            # Pass to the main window for execution
            self.parent_window.run_automation_sequence(selected_sequence)
            self.accept() # Close manager after starting execution
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a rule sequence to run.")
