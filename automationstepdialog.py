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

from devicemodel import device_model


# Dialog for creating automation step (eg. rule)
class AutomationStepDialog(QDialog):
    def __init__(self, num_locos_req, step: AutomationStep = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Rule")
        self.num_locos_req = num_locos_req
        self.step = step
        self.params = {}

        self._setup_ui()
        
    def _setup_ui(self):
        self.setLayout(QFormLayout())

        # Request name of rule
        self.name_lineedit = QLineEdit()
        self.layout().addRow("Step Name:", self.name_lineedit)

        # Rule Type Selector
        self.rule_type_combo = QComboBox()
        #RuleType = [AutomationRule("Rule1", "loco", {}), AutomationRule("Rule2", "point", {}), AutomationRule("Rule3", "sensor", {})]
        self.rule_type_combo.addItems(["Select type", "VLCB", "Loco", "App", "Gui"])
        self.layout().addRow("Rule Type:", self.rule_type_combo)
        self.rule_type_combo.currentTextChanged.connect(self.update_node_combo)
        
        #Node, Event, Value

        # Node Selector
        self.node_combo = QComboBox()
        self.node_combo.addItem("NA", None)	# Change to Select Node if VLCB
        # Nodes to be added if VLCB selected
        self.layout().addRow("Node:", self.node_combo)
        self.node_combo.currentTextChanged.connect(self.update_event_combo)
        
        # Event Selector
        self.event_combo = QComboBox()
        self.event_combo.addItem("NA", None) # Change to Select Event if VLCB
        # Events to be added if VLCB selected
        self.layout().addRow("Event:", self.event_combo)
        self.event_combo.currentTextChanged.connect(self.update_value_combo)

        # Value Selector
        self.value_combo = QComboBox()
        self.value_combo.addItem("NA", None) # Change to value
        # Values to be added
        self.layout().addRow("Value:", self.value_combo)


        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_step)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        self.layout().addRow(button_box)
        
        # Initial call to set up the parameters based on the default selected rule
        #self._update_params_ui(self.rule_type_combo.currentText())
        self.step = None

    def update_node_combo(self, index):
        self.node_combo.clear()
        # Updates the event_combo based on the selected type
        selected_type = self.rule_type_combo.currentText()
        if selected_type == None or selected_type == "Select Type":
            nodes = ["NA"]
        else:
            #node_type = device_model.name_to_key(selected_type)
            # If User Interface - convert to Gui
            if selected_type == "User Interface":
                selected_type = "Gui"
            nodes = device_model.get_nodes_names(selected_type)
            # If there are no devices of this type
            if nodes == []:
                nodes = ["NA"]
        # Don't say select if there are none to select
        if nodes != ["NA"]:
            self.node_combo.addItem("Select Node")
        self.node_combo.addItems(nodes)


    def update_event_combo(self, index):
        # First get the type (so we can lookup the node)
        selected_type = self.rule_type_combo.currentText()
        # Should always have a type if this has an option, but check anyway
        if selected_type == None or selected_type == "Select Type":
            return
        else:
            #node_type = device_model.name_to_key(selected_type)
            # If User Interface - convert to Gui
            if selected_type == "User Interface":
                selected_type = "Gui"
        #print (f"Updating event combo {index}")
        self.event_combo.clear()
        # Updates the event_combo based on the selected node.
        selected_node = self.node_combo.currentText()
        if selected_node == None or selected_node == "Select Node" or selected_node == "NA":
            events = ["NA"]
        else:
            # convert to node_key
            node_key = device_model.name_to_key(selected_node, selected_type)
            #print (f"Type {selected_type} Node {selected_node} key {node_key}")
            events = device_model.get_events(node_key, selected_type)
            #print (f"Events {events}")
            if events == []:
                events = ["NA"]
        if events != ["NA"]:
            self.event_combo.addItem("Select Event")
        self.event_combo.addItems(events)
        
    
    def update_value_combo(self):
        self.value_combo.clear()
        # For this just check that there is an event
        # If it's not "" or "NA" then it should have an on or off status
        # Default to on events
        selected_event = self.event_combo.currentText()
        if selected_event == "NA" or selected_event == "":
            self.value_combo.addItem("NA")
        else:
            self.value_combo.addItem("on")
            self.value_combo.addItem("off")
     

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
        print ("Deprecated - see new methods")


    def save_step(self):
        """Gathers data and creates the AutomationRule object."""
        rule_type = self.rule_type_combo.currentText()
        #loco_index = self.loco_combo.currentData()
        
        # All steps needed a name - but if empty can be created automatically
        self.name = self.name_lineedit.text()
        
        # If this matches the device model keys then it's an automation rule
        if rule_type in device_model.event_map.keys():
            
            # Get additional data and place in a dict
            data_dict = {}
            
            # If it's vlcb then convert node to node_id
            node = self.node_combo.currentText()
            if node == None or node == "Select Node" or node == "NA":
                # todo replace with qmessage - also see other print messages
                print ("Invalid node")
                return
            data_dict['node_id'] = device_model.name_to_key(node)
            event = self.event_combo.currentText()
            if event == None or event == "Select Event" or event == "NA":
                print ("Invalid event")
                return
            data_dict['event'] = event
            # Value should not return an invalid value but check anyway
            value = self.value_combo.currentText()
            if value == None or value == "NA":
                print ("Invalid value")
                return
            data_dict['value'] = value
            
            # If no name given then can replace with a user friendly
            if self.name == "":
                self.name = f"{rule_type}, {data_dict['node_id']} - {data_dict['event']} - {data_dict['value']}"
            
            # Step parent, step_type, step_name, data={}
            self.step = AutomationStep(None, rule_type, self.name, data_dict)
            
            
        # Todo need to implement all rule types so this doesn't happen
        else:
            print (f"Unable to validate entries {rule_type}")
            return
        
        # here validate values before accepting
        super().accept()
        
    def get_step(self):
        return self.step
