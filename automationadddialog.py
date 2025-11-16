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

class AutomationAddDialog(QDialog):
    def __init__(self, sequence=None, parent=None):
        super().__init__(parent)
        print ("Deprecated - replace with AutomationSeqDialog")
        self.setWindowTitle("Create Automation Sequence")
        self.sequence = sequence # For editing, if passed
        self.steps_data = [] # Stores list of AutomationStep objects
        
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
        self.num_locos_spinbox.setValue(1)
        title_layout.addRow("Sequence Title:", self.title_input)
        title_layout.addRow("Locos Required:", self.num_locos_spinbox)
        main_layout.addLayout(title_layout)

        main_layout.addWidget(QLabel("--- Automation Steps ---"))
        
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

    # --- Step Management Logic ---
    
    def _update_steps_list(self):
        """Refreshes the list widget with current steps."""
        self.steps_list.clear()
        for i, step in enumerate(self.steps_data):
            rule_count = len(step.rules)
            mode = step.execution_mode.capitalize()
            self.steps_list.addItem(f"Step {i+1} ({mode}, {rule_count} Rules)")

    def add_edit_step(self, edit=False):
        """Opens a sub-dialog to create or edit an AutomationStep."""
        current_step = None
        current_index = -1
        if edit:
            current_index = self.steps_list.currentRow()
            if current_index < 0:
                QMessageBox.warning(self, "Error", "Please select a step to edit.")
                return
            current_step = self.steps_data[current_index]

        # Use a sub-dialog (StepCreationDialog) for complexity of rule building
        dialog = StepCreationDialog(self.num_locos_spinbox.value(), current_step, self)
        if dialog.exec() == QDialog.Accepted:
            new_step = dialog.get_step()
            if edit:
                self.steps_data[current_index] = new_step
            else:
                self.steps_data.append(new_step)
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

        if not self.steps_data:
            QMessageBox.warning(self, "Error", "The sequence must contain at least one step.")
            return

        self.sequence = AutomationSequence(title, self.steps_data, {"num_locos": num_locos})
        super().accept()

    def get_sequence(self):
        return self.sequence
        
# --- Step Creation Sub-Dialog (Essential for building rules) ---
class StepCreationDialog(QDialog):
    """Dialog to create or edit an AutomationStep (a list of rules)."""
    def __init__(self, num_locos_req, step: AutomationStep = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Automation Step")
        self.num_locos_req = num_locos_req
        self.rules_data = step.rules if step else []

        self._setup_ui(step)
        self._update_rules_list()

    def _setup_ui(self, step):
        main_layout = QVBoxLayout(self)

        # Execution Mode (Sequential/Parallel)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Execution Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Sequential")
        self.mode_combo.addItem("Parallel")
        if step and step.execution_mode == "parallel":
             self.mode_combo.setCurrentText("Parallel")
        mode_layout.addWidget(self.mode_combo)
        main_layout.addLayout(mode_layout)

        main_layout.addWidget(QLabel("Rules in this Step:"))

        # Rule List
        self.rules_list = QListWidget()
        main_layout.addWidget(self.rules_list)

        # Controls for Rules
        rule_control_layout = QHBoxLayout()
        self.add_rule_button = QPushButton("Add Rule")
        self.remove_rule_button = QPushButton("Remove Rule")
        rule_control_layout.addWidget(self.add_rule_button)
        rule_control_layout.addWidget(self.remove_rule_button)
        main_layout.addLayout(rule_control_layout)

        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        main_layout.addLayout(button_box)

        # Connections
        self.add_rule_button.clicked.connect(self.add_rule)
        self.remove_rule_button.clicked.connect(self.remove_rule)

    def _update_rules_list(self):
        """Refreshes the list widget with current rules."""
        self.rules_list.clear()
        for rule in self.rules_data:
            loco_info = f"Loco {rule.loco_index+1}" if rule.loco_index is not None else "N/A"
            self.rules_list.addItem(f"{rule.rule_type.name} ({loco_info}): {rule.params}")

    def add_rule(self):
        """Opens a sub-dialog to create an AutomationRule."""
        dialog = RuleEditorDialog(self.num_locos_req, parent=self)
        if dialog.exec() == QDialog.Accepted:
            new_rule = dialog.get_rule()
            self.rules_data.append(new_rule)
            self._update_rules_list()

    def remove_rule(self):
        selected_row = self.rules_list.currentRow()
        if selected_row >= 0:
            del self.rules_data[selected_row]
            self._update_rules_list()
        else:
            QMessageBox.warning(self, "Error", "Please select a rule to remove.")

    def get_step(self) -> AutomationStep:
        mode = self.mode_combo.currentText().lower()
        return AutomationStep(self.rules_data, mode)


# --- Rule Editor Sub-Dialog (For configuring single rules) ---
class RuleEditorDialog(QDialog):
    """Dialog for configuring a single AutomationRule."""
    def __init__(self, num_locos_req, rule: AutomationRule = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Rule")
        self.num_locos_req = num_locos_req
        self.rule = rule
        self.params = {}

        self._setup_ui()
        
    def _setup_ui(self):
        self.setLayout(QFormLayout())

        # Rule Type Selector
        self.rule_type_combo = QComboBox()
        RuleType = [AutomationRule("Rule1", "loco", {}), AutomationRule("Rule2", "point", {}), AutomationRule("Rule3", "sensor", {})]
        for rule_type in RuleType:
            self.rule_type_combo.addItem(rule_type.name, rule_type.type)
        self.layout().addRow("Rule Type:", self.rule_type_combo)
        self.rule_type_combo.currentTextChanged.connect(self._update_params_ui)

        # Loco Index Selector
        self.loco_combo = QComboBox()
        self.loco_combo.addItem("N/A", None)
        for i in range(self.num_locos_req):
            self.loco_combo.addItem(f"Loco {i+1} (Index {i})", i)
        self.layout().addRow("Assign Loco:", self.loco_combo)
        
        # Dynamic Parameters Widget
        self.params_widget = QWidget()
        self.params_layout = QFormLayout(self.params_widget)
        self.layout().addRow(self.params_widget)

        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_rule)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        self.layout().addRow(button_box)
        
        # Initial call to set up the parameters based on the default selected rule
        #self._update_params_ui(self.rule_type_combo.currentText())


    def _clear_layout(self, layout):
        """Helper to clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clear_layout(item.layout()) # Handle nested layouts

    def _update_params_ui(self, rule_name):
        """Dynamically adds input fields based on the selected RuleType."""
        self._clear_layout(self.params_layout)
        
        rule_type = AutomationRule(rule_name, "test", {})
        
        # Disable loco selection if rule doesn't involve a loco (like WAIT)
        #self.loco_combo.setEnabled(rule_type not in [RuleType.WAIT_TIME, RuleType.SWITCH_POINT])

        # Add specific parameter fields
        if rule_type == RuleType.SET_SPEED:
            self.speed_spinbox = QSpinBox()
            self.speed_spinbox.setRange(0, 100)
            self.params_layout.addRow("Speed (0-100):", self.speed_spinbox)
            self.params['speed'] = self.speed_spinbox

        elif rule_type == RuleType.WAIT_TIME:
            self.time_spinbox = QSpinBox()
            self.time_spinbox.setRange(1, 600)
            self.params_layout.addRow("Wait Time (seconds):", self.time_spinbox)
            self.params['seconds'] = self.time_spinbox

        elif rule_type == RuleType.SWITCH_POINT:
            self.point_combo = QComboBox()
            for pid in AVAILABLE_POINTS: self.point_combo.addItem(str(pid))
            self.state_combo = QComboBox()
            self.state_combo.addItems(["Straight", "Turnout"])
            
            self.params_layout.addRow("Point ID:", self.point_combo)
            self.params_layout.addRow("State:", self.state_combo)
            self.params['point_id'] = self.point_combo
            self.params['state'] = self.state_combo
            
        elif rule_type == RuleType.WAIT_FOR_SENSOR:
            self.sensor_combo = QComboBox()
            for sid in AVAILABLE_SENSORS: self.sensor_combo.addItem(str(sid))
            self.params_layout.addRow("Sensor ID:", self.sensor_combo)
            self.params['sensor_id'] = self.sensor_combo

        elif rule_type == RuleType.STOP_LOCO:
             # No extra parameters needed
             pass

    def save_rule(self):
        """Gathers data and creates the AutomationRule object."""
        rule_type = self.rule_type_combo.currentData()
        loco_index = self.loco_combo.currentData()
        
        rule_params = {}
        
        # todo implement this
        return
        
        try:
            # Collect dynamic parameters
            if rule_type == RuleType.SET_SPEED:
                rule_params['speed'] = self.params['speed'].value()
            elif rule_type == RuleType.WAIT_TIME:
                rule_params['seconds'] = self.params['seconds'].value()
            elif rule_type == RuleType.SWITCH_POINT:
                rule_params['point_id'] = int(self.params['point_id'].currentText())
                rule_params['state'] = self.params['state'].currentText()
            elif rule_type == RuleType.WAIT_FOR_SENSOR:
                rule_params['sensor_id'] = int(self.params['sensor_id'].currentText())
            # STOP_LOCO has no extra params
            
        except AttributeError:
            QMessageBox.critical(self, "Error", "A required parameter field is missing or invalid.")
            return

        # Validate loco assignment if required
        if rule_type not in [RuleType.WAIT_TIME, RuleType.SWITCH_POINT] and loco_index is None:
            QMessageBox.warning(self, "Error", "This rule requires a Loco Assignment.")
            return

        self.rule = AutomationRule(rule_type, loco_index, **rule_params)
        super().accept()

    def get_rule(self):
        return self.rule
