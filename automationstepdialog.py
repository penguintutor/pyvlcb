# Dialog for creating a new AutomationSequence.

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget, QFormLayout, QLineEdit, QSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt
from automationrule import AutomationRule
from automationsequence import AutomationStep, AutomationSequence

from devicemodel import device_model
from locoevent import LocoEvent


# Dialog for creating automation step (eg. rule)
class AutomationStepDialog(QDialog):
    def __init__(self, parent, num_locos_req, step: AutomationStep = None):
        super().__init__(parent)
        self.parent = parent
        self.mainwindow = self.parent.mainwindow
        self.setWindowTitle("Configure Rule")
        self.resize(350, 250)
        self.num_locos_req = num_locos_req
        self.step = step
        self.params = {}

        self._setup_ui()
        
    def _setup_ui(self):
        self.setLayout(QFormLayout())

        # Request name of rule
        self.name_lineedit = QLineEdit()
        self.name_label = QLabel("Step Name:")
        self.layout().addRow(self.name_label, self.name_lineedit)

        # Rule Type Selector
        self.rule_type_combo = QComboBox()
        #RuleType = [AutomationRule("Rule1", "loco", {}), AutomationRule("Rule2", "point", {}), AutomationRule("Rule3", "sensor", {})]
        self.rule_type_combo.addItems(["Select type", "VLCB", "Loco", "App", "Gui"])
        self.rule_type_label = QLabel("Step Type:")
        self.layout().addRow(self.rule_type_label, self.rule_type_combo)
        
        #Node, Event, Value
        # These are maintained even if the type of rule uses a different name
        # This avoids swapping out the combobox if it just needs different values

        # Node Selector
        # Note that the QComboBox may be replaced (eg. spinbox for Loco)
        # but the node_label reference must be maintained (even if not a node) to be able to identify the row
        # the text of node_label can of course be changed
        self.node_combo = QComboBox()
        self.node_combo.addItem("NA", None)	# Change to Select Node if VLCB
        # Nodes to be added if VLCB selected
        self.node_label = QLabel("Node:")
        self.layout().addRow(self.node_label, self.node_combo)
                
        # Event Selector
        self.event_combo = QComboBox()
        self.event_combo.addItem("NA", None) # Change to Select Event if VLCB
        # Events to be added if VLCB selected
        self.event_label = QLabel("Event:")
        self.layout().addRow(self.event_label, self.event_combo)
        # swap event_combo for lineedit if required
        self.event_edit = QLineEdit()

        # Value Selector
        self.value_combo = QComboBox()
        self.value_combo.addItem("NA", None) # Change to value
        # Values to be added
        self.value_label = QLabel("Value:")
        self.layout().addRow(self.value_label, self.value_combo)
        
        # Value 2 (used by certain options - eg. DCC)
        # Hide if not used
        self.value2_combo = QComboBox()
        self.value2_combo.addItem("NA", None)
        self.value2_label = QLabel("Value:")
        self.layout().addRow(self.value2_label, self.value2_combo)

        # Spacer
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(30) # Set a fixed height for the gap
        self.layout().addRow(spacer_widget)
        
        # Set a minimum height for all the widgets to ensure spacing if set to ""
        min_row_height = 30
        self.name_label.setMinimumSize(0, min_row_height)
        self.rule_type_label.setMinimumSize(0, min_row_height)
        self.node_label.setMinimumSize(0, min_row_height)
        self.event_label.setMinimumSize(0, min_row_height)
        self.value_label.setMinimumSize(0, min_row_height)
        self.value2_label.setMinimumSize(0, min_row_height)

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
        if self.step != None:
            #print (f"Step details {self.step}")
            # Check if the type is valid and if so then set it 
            index = self.rule_type_combo.findText(self.step['type'])

            if index >= 0:
                self.rule_type_combo.setCurrentIndex(index)
            else:
                print(f"Warning: '{self.step['type']}' not found in combo box options.")
                
        # Update the form type
        self.set_form_type ()
            
        
        # Don't connect to the change events until after initial setup
        self.rule_type_combo.currentTextChanged.connect(self.update_node_combo)
        self.node_combo.currentTextChanged.connect(self.update_event_combo)
        self.event_combo.currentTextChanged.connect(self.update_value_combo)
        self.value_combo.currentTextChanged.connect(self.update_value2_combo)
        
    # Updates the form, including the labels and input fields according to type
    # Does not set any values - just the form type and calls the generator of the combo if appropriate
    def set_form_type (self):
        # Block signals whilst updating - then manually call update and then reenable signals
        self.node_combo.blockSignals(True)
        self.event_combo.blockSignals(True)
        self.value_combo.blockSignals(True)
        
        form_type = self.rule_type_combo.currentText()
        if form_type == "VLCB":
            self.node_combo.setVisible(True)
            self.node_label.setText("Node:")
            # Loco uses self.event_edit rather than combo - swap back here
            #self.replace_edit_type(self.event_label, self.event_combo)
            self.event_edit.setVisible(False)
            self.event_combo.setVisible(True)
            result = self.layout().replaceWidget(self.event_edit, self.event_combo)
            self.event_combo.setVisible(True)
            self.event_label.setText("Event:")
            self.value_combo.setVisible(True)
            self.value_label.setText("Value:")
            self.value2_combo.setVisible(False)
            self.value2_label.setText("")
        elif form_type == "Loco":
            # Loco No is the dynamic locos (eg. 1 to 3 and option for DCC ID)
            self.node_combo.setVisible(True)
            self.node_label.setText("Loco No.:")
            # DCC ID is if tied to a specific loco (only if selected from above)
            self.event_edit.setVisible(True)
            self.event_combo.setVisible(False)
            self.layout().replaceWidget(self.event_combo, self.event_edit)
            self.event_edit.setVisible(True)
            self.event_label.setText("DCC ID:")
            # Loco uses self.event_edit rather than combo
            #self.replace_edit_type(self.event_label, self.event_edit)
            # Action (uses value field)
            self.value_combo.setVisible(True)
            self.value_label.setText("Action:")
            # Value (eg. speed)
            self.value2_combo.setVisible(True)
            self.value2_label.setText("Value:")
        # If not recognised then set as non selected
        else:
            print ("Not a valid type")
            self.node_label.setText("N/A")
        # Update each of the combo with their values
        self.update_node_combo(update_form = False)
        self.update_event_combo()
        self.update_value_combo()
        self.update_value2_combo()
        # Reenable signals
        self.node_combo.blockSignals(False)
        self.event_combo.blockSignals(False)
        self.value_combo.blockSignals(False)
            
    # Replace one row widget (eg QComboBox) with a different widget
    # whilst preserving row position and label
    # Label is how we find the row, new_widget replaces the widget
    # Does not update the text of the label, that should be done elsewhere
    def replace_edit_type(self, old_widget, new_widget):
        form_layout = self.layout()
        
        #self.layout().replaceWidget(old_widget, new_widget)
        
        # Get row 
        row_index = form_layout.indexOf(label)

        if row_index == -1:
            print("Error: Row not found")
            return
        
        # Remove the entire row (including the old QComboBox)
        form_layout.removeRow(row_index) 

        # Insert the new row at the exact same index
        # We use the existing self.node_label reference!
        form_layout.insertRow(row_index, label, new_widget)

        

    def update_node_combo(self, update_form = True):
        # First set appropriate form widgets / labels
        # if update_form is set to false then don't call set_form_type
        # this is required if called from set_form_type to avoid recursive calls
        if update_form != False:
            self.set_form_type ()
        
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
            # If this type is one of the device_nodes then get from device_model
            if selected_type == "Gui" or selected_type == "VLCB":
                nodes = device_model.get_nodes_names(selected_type, null_events=False)
            elif selected_type == "Loco":
                if self.num_locos_req > 0:
                    nodes = [f"ID {i}" for i in range (1, self.num_locos_req + 1)]
                else:
                    nodes = []
                nodes.append("Use DCC ID")
                    
            # If there are no devices of this type
            if nodes == []:
                nodes = ["NA"]
        # Don't say select if there are none to select
        if nodes != ["NA"]:
            self.node_combo.addItem("Select Node")
        self.node_combo.addItems(nodes)


    def update_event_combo(self):
        # First get the type (so we can lookup the node)
        # The event combo sometimes gets swapped for a line edit
        # Swap is done on set_form_type - but here need to use appropriate
        selected_type = self.rule_type_combo.currentText()
        events = []
        # Should always have a type if this has an option, but check anyway
        if selected_type == None or selected_type == "Select Type":
            return
        elif selected_type == "User Interface":
            selected_type = "Gui"
        #print (f"Updating event combo {index}")
        self.event_combo.clear()
        # Updates the event_combo based on the selected node.
        selected_node = self.node_combo.currentText()
        if selected_node == None or selected_node == "Select Node" or selected_node == "NA":
            events = ["NA"]
        elif selected_type == "Gui" or selected_type == "VLCB":
            # convert to node_key
            node_key = device_model.name_to_key(selected_node, selected_type)
            #print (f"Type {selected_type} Node {selected_node} key {node_key}")
            events = device_model.get_events(node_key, selected_type)
            #print (f"Events {events}")
            if events == []:
                events = ["NA"]
        elif selected_type == "Loco":
            # For Loco then the event_combo has been replaced with event_edit
            # If the node is DCC ID then this is enabled (if not it's NA)
            if selected_node == "Use DCC ID":
                self.event_edit.setReadOnly(False)
            else:
                self.event_edit.setText("")
                self.event_edit.setReadOnly(True)
                
        else:
            events = ["NA"]
            
        if events != ["NA"]:
            self.event_combo.addItem("Select Event")
        self.event_combo.addItems(events)
        
    
    def update_value_combo(self):
        self.value_combo.clear()
        selected_type = self.rule_type_combo.currentText()
        if selected_type == None or selected_type == "Select Type":
            values = ["NA"]
        elif selected_type == "VLCB" or selected_type == "Gui":
            # For this just check that there is an event
            # If it's not "" or "NA" then it should have an on or off status
            # Default to on events
            selected_event = self.event_combo.currentText()
            if selected_event == "NA" or selected_event == "":
                self.value_combo.addItem("NA")
            else:
                self.value_combo.addItem("on")
                self.value_combo.addItem("off")
        elif selected_type == "Loco":
            self.value_combo.addItems(LocoEvent.event_types)
            
        # For loco then uses LocoEvent.event_types list to create actions

    def update_value2_combo(self):
        selected_type = self.rule_type_combo.currentText()
        if selected_type == None or selected_type == "Select Type":
            nodes = ["NA"]
        else:
            self.value2_combo.clear()
            # If Loco then look at value1 (action) and set list here
            if selected_type == "Loco":
                # now look at action from value1
                loco_action = self.value_combo.currentText()
                if loco_action == "Set Speed":
                    # change for spinbox
                    pass
                elif loco_action == "Set Direction":
                    self.value2_combo.addItems(["Forward", "Reverse", "Toggle"])
                # Others don't need another value - eg. Stop
                else:
                    self.value2_combo.addItem("NA")
        
        # For this just check that there is an event
        # If it's not "" or "NA" then it should have an on or off status
        # Default to on events
        selected_event = self.event_combo.currentText()
        if selected_event == "NA" or selected_event == "":
            self.value2_combo.addItem("NA")
        else:
            self.value2_combo.addItem("on")
            self.value2_combo.addItem("off")



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
            
            # appvars should not longer be included in the step (added directly in AutomationSequence)
            # Step parent, step_type, step_name, data={}
            #data_dict["appvars"] = self.mainwindow.appvariables
            ####
            #self.step = AutomationStep(None, rule_type, self.name, data_dict)
            # Return as a dict - let Automation Sequence convert into an Automation Step
            self.step = {"type": rule_type, "name": self.name, "data" : data_dict}
            
            
        # Todo need to implement all rule types so this doesn't happen
        else:
            print (f"Unable to validate entries {rule_type}")
            return
        
        # here validate values before accepting
        super().accept()
        
    def get_step(self):
        return self.step
