# Dialog to display, add, edit, and run automation sequences

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget
)
from PySide6.QtCore import Qt
from automationseqdialog import AutomationSeqDialog
from automationmanager import AutomationManager


class AutomationManagerDialog(QDialog):
    
    def __init__(self, parent, manager: AutomationManager):
        super().__init__(parent)
        self.setWindowTitle("Automation Rule Manager")
        self.resize(500, 400)
        self.manager = manager
        
        
        self.mainwindow = parent

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
        self.edit_button.clicked.connect(self.edit_sequence)
        self.run_button.clicked.connect(self.run_selected_sequence)
        self.close_button.clicked.connect(self.accept)
        # Note: Edit/Delete connections would be similar to add, updating self.sequences and re-running _update_list

    def _update_list(self):
        """Refreshes the list widget with current sequences."""
        self.rule_list.clear()
        for seq_string in self.manager.get_sequence_strings():
            self.rule_list.addItem(seq_string)
        self.rule_list.setCurrentRow(0)

    def add_sequence(self):
        """Opens the rule creation dialog."""
        self.open_sequence_dialog(None)

    def edit_sequence(self):
        # Todo setup edit of sequence
        # Get the selected sequence
        # indexFromItem
        row_num = self.rule_list.currentRow()
        sequence = self.manager.get_sequence(row_num)
        dialog = AutomationSeqDialog(self, sequence)
        if dialog.exec() == QDialog.Accepted:
            new_sequence = dialog.get_sequence()
            self.manager.update_sequence(row_num, new_sequence)
            result = self.manager.save()
            if result == "Save successful":
                QMessageBox.information(self, "Success", f"Sequence '{new_sequence['title']}' updated.")
            else:
                QMessageBox.information(self, "Save Error", result)    
        self._update_list()
            
        # Todo setup edit of sequence
        # Get the selected sequence
        # indexFromItem
        row_num = self.rule_list.currentRow()
        sequence = self.manager.get_sequence(row_num)
        dialog = AutomationSeqDialog(self, sequence)
        if dialog.exec() == QDialog.Accepted:
            # todo Edit here
            pass
        pass
            
        row = self.rule_list.currentRow()
        self.open_sequence_dialog(row)

    def run_selected_sequence(self):
        """Triggers the run process in the main window."""
        selected_row = self.rule_list.currentRow()
        if selected_row >= 0:
            
            ## Here
            self.manager.run_sequence(selected_row)
            
            #selected_sequence = self.sequences[selected_row]
            # Pass to the main window for execution
            #self.mainwindow.run_automation_sequence(selected_sequence)
            self.accept() # Close manager after starting execution
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a rule sequence to run.")

    def open_sequence_dialog(self, row: int | None = None):
        """Open the AutomationSeqDialog for add (row=None) or edit (row=index)."""
        # If editing, validate selection
        if row is not None:
            if row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a sequence to edit.")
                return
            existing = self.manager.get_sequence(row)
            dialog = AutomationSeqDialog(self, existing)
        else:
            dialog = AutomationSeqDialog(self)

        if dialog.exec() == QDialog.Accepted:
            new_sequence = dialog.get_sequence()
            if row is None:
                self.manager.add_sequence(new_sequence)
                verb = "created"
            else:
                self.manager.update_sequence(row, new_sequence)
                verb = "updated"

            result = self.manager.save()
            if result == "Save successful":
                QMessageBox.information(self, "Success", f"Sequence '{new_sequence.get('title','')}' {verb}.")
            else:
                QMessageBox.information(self, "Save Error", result)

            self._update_list()


