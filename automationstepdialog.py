# Dialog for creating a new AutomationSequence.

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget, QFormLayout, QLineEdit, QSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from automationrule import AutomationRule
from automationsequence import AutomationStep, AutomationSequence

from devicemodel import device_model
from locoevent import LocoEvent


# Dialog for creating automation step (eg. rule)
class AutomationStepDialog(QDialog):
    def __init__(self, parent, num_locos, step: AutomationStep = None):
        super().__init__(parent)
        self.parent = parent
        self.mainwindow = self.parent.mainwindow
        self.setWindowTitle("Configure Rule")
        self.resize(350, 250)
        # Always show 1 more loco in case a new one is required
        self.num_locos_req = num_locos + 1
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
        self.rule_type_combo.addItems(["Select Type", "VLCB", "Loco", "App", "Gui"])
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
        # Add validator to accept only integers 1-9999
        self.event_edit.setValidator(QIntValidator(1, 9999, self.event_edit))
        # Add label if loco id selected
        self.event_alt_label = QLabel("Allocated when run")

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
        # Can sometimes swap out combo for spinbox - eg. loco speed
        self.value2_spinbox = QSpinBox()
        self.value2_spinbox.setRange(0,128)
        self.value2_spinbox.setValue(0)
        self.value2_label = QLabel("Value:")
        self.layout().addRow(self.value2_label, self.value2_combo)
        # Or swap for a dual spinbox & combo using a Horizontal Layout
        self.value2_inner_widget = QWidget()
        self.value2_inner_layout = QHBoxLayout(self.value2_inner_widget)
        # Set margins to 0 to make it look clean inside the QFormLayout row
        self.value2_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.value2_inner_spinbox = QSpinBox()
        self.value2_inner_spinbox.setRange(1, 18)
        self.value2_inner_spinbox.setValue(1)
        self.value2_inner_combo = QComboBox()
        self.value2_inner_combo.addItems(["On", "Off"])
        
        # 5. Add widgets to the QHBoxLayout
        self.value2_inner_layout.addWidget(self.value2_inner_spinbox)
        #self.value2_inner_layout.addWidget(QLabel("Units:")) # Adding a small label for context
        self.value2_inner_layout.addWidget(self.value2_inner_combo)

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

    def show_hide_row (self, row, show=True, label=None):
        """Set visibility for the widgets in the specified form row.

        Keeps the label visible at all times. When hiding a row we set the
        label's text to an empty string (but keep it visible to preserve
        spacing). When restoring if label is provided then that is used
        as the text.
        
        Handles both single widgets and nested layouts in the FieldRole.
        """
        #print (f"Show/hide row {row} show={show} label={label}")

        form_layout = self.layout()

        label_item = form_layout.itemAt(row, QFormLayout.LabelRole).widget()
        field_item = form_layout.itemAt(row, QFormLayout.FieldRole)

        if show == False:
            label_item.setText("")
        elif label is not None:
            label_item.setText(label)
        
        # Handle field_item: it could be a widget or a nested layout
        if field_item is None:
            return
        
        field_widget = field_item.widget()
        if field_widget is not None:
            # It's a single widget (e.g., QComboBox, QLineEdit)
            field_widget.setVisible(show)
        else:
            # It's a layout (e.g., QHBoxLayout)
            field_layout = field_item.layout()
            if field_layout is not None:
                # Hide/show all child widgets in the layout
                for idx in range(field_layout.count()):
                    child_item = field_layout.itemAt(idx)
                    if child_item is None:
                        continue
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.setVisible(show)
        
    # Updates the form, including the labels and input fields according to type
    # Does not set any values - just the form type and calls the generator of the combo if appropriate
    def set_form_type (self):
        #print ("Set form type")
        # Block signals whilst updating - then manually call update and then reenable signals
        self.node_combo.blockSignals(True)
        self.event_combo.blockSignals(True)
        self.value_combo.blockSignals(True)
        
        form_type = self.rule_type_combo.currentText()
        if form_type == "VLCB":
            #self.node_combo.setVisible(True)
            self.node_label.setText("Node:")
            # Loco uses self.event_edit rather than combo - swap back here
            self.swap_field_widget(self.event_label, self.event_combo)
            self.event_label.setText("Event:")
            self.value_label.setText("Value:")
            self.value2_label.setText("")
            # show / hide comes after updating fields
            self.show_hide_row(2, True)     # Show node row
            self.show_hide_row(3, False)    # Hide event row (show if node selected)
            self.show_hide_row(4, False)    # Hide value row
            self.show_hide_row(5, False)    # Hide value2 row
            
        elif form_type == "Loco":
            # Loco No is the dynamic locos (eg. 1 to 3 and option for DCC ID)
            self.node_combo.setVisible(True)
            self.node_label.setText("Loco No.:")
            # DCC ID is if tied to a specific loco (only if selected from above)
            self.swap_field_widget(self.event_label, self.event_edit)
            self.event_label.setText("DCC ID:")
            # Loco uses self.event_edit rather than combo
            # Action (uses value field)
            self.value_combo.setVisible(True)
            self.value_label.setText("Action:")
            # Value (eg. speed)
            self.value2_combo.setVisible(True)
            self.value2_label.setText("Value:")
        # If not recognised then set as non selected
        # This is default for a new step
        else:
            #print ("Not a valid type")
            self.node_label.setText("N/A")
            self.show_hide_row(2, False)    # Hide node row
            self.show_hide_row(3, False)    # Hide event row (show if node selected)
            self.show_hide_row(4, False)    # Hide value row
            self.show_hide_row(5, False)    # Hide value2 row
        # Update each of the combo with their values
        self.update_node_combo(update_form = False)
        self.update_event_combo()
        self.update_value_combo()
        self.update_value2_combo()
        # Reenable signals
        self.node_combo.blockSignals(False)
        self.event_combo.blockSignals(False)
        self.value_combo.blockSignals(False)
            

    def update_node_combo(self, update_form = True):
        #print ("Update node combo")
        # First set appropriate form widgets / labels
        # if update_form is set to false then don't call set_form_type
        # this is required if called from set_form_type to avoid recursive calls
        if update_form != False:
            self.set_form_type ()

        nodes = []
        
        self.node_combo.clear()
        # Updates the event_combo based on the selected type
        selected_type = self.rule_type_combo.currentText()
        #print (f"Selected type {selected_type}")
        if selected_type == None or selected_type == "Select Type":
            nodes = ["NA"]
            # Hide remaining rows - eg. if previously selected details but now node unselected
            self.show_hide_row(2, False)    # Hide node row
            self.show_hide_row(3, False)    # Hide event row (show if node selected)
            self.show_hide_row(4, False)    # Hide value row
            self.show_hide_row(5, False)    # Hide value2 row
        #    return
        else:
            # If User Interface - convert to Gui
            if selected_type == "User Interface":
                selected_type = "Gui"
            # If this type is one of the device_nodes then get from device_model
            if selected_type == "Gui" or selected_type == "VLCB":
                nodes = device_model.get_nodes_names(selected_type, null_events=False)
            elif selected_type == "Loco":
                # Loco does ont use "node" reference so create list of loco numbers
                # then add to GUI and return 
                nodes = ["Select Loco"]
                if self.num_locos_req > 0:
                    nodes = [f"ID {i}" for i in range (1, self.num_locos_req + 1)]
                else:
                    nodes = []
                nodes.append("Use DCC ID")
                self.node_combo.addItems(nodes)
                self.show_hide_row(2, True, "Loco:")    # Show node row (called loco)
                return    
            # If there are no devices of this type
            if nodes == []:
                nodes = ["NA"]
        # Don't say select if there are none to select
        if nodes != ["NA"]:
            self.node_combo.addItem("Select Node")
        self.node_combo.addItems(nodes)
        # show the node row
        self.show_hide_row(2, True, "Node:")    # Show node row


    def update_event_combo(self):
        #print ("Update event combo")
        # First get the type (so we can lookup the node)
        # The event combo sometimes gets swapped for a line edit
        # Swap is done on set_form_type - but here need to use appropriate
        selected_type = self.rule_type_combo.currentText()
        events = []
        # Should always have a type if this has an option, but check anyway
        if selected_type == None or selected_type == "Select Type":
            self.show_hide_row(2, False)
            return
        elif selected_type == "User Interface":
            selected_type = "Gui"
        #print (f"Updating event combo {index}")
        self.event_combo.clear()
        # Updates the event_combo based on the selected node.
        selected_node = self.node_combo.currentText()
        if selected_node == None or selected_node == "Select Node" or selected_node == "NA":
            events = ["NA"]
            self.show_hide_row(3, False)
            #print ("Hiding event row as no node selected")
            return
        elif selected_type == "Gui" or selected_type == "VLCB":
            # convert to node_key
            node_key = device_model.name_to_key(selected_node, selected_type)
            #print (f"Type {selected_type} Node {selected_node} key {node_key}")
            events = device_model.get_events(node_key, selected_type)
            #print (f"Events {events}")
            if events == []:
                events = ["NA"]
            # Show the event field
            self.show_hide_row(3, True, "Event:") 
        elif selected_type == "Loco":
            # For Loco then the event_combo has been replaced with event_edit
            # If the node is DCC ID then this is enabled (if not replace with label)
            self.event_label.setText("DCC ID:")
            if selected_node == "Use DCC ID":
                #self.event_edit.setReadOnly(False)
                #self.event_edit.show
                self.swap_field_widget(self.event_label, self.event_edit)
            else:
                # Clear previous entry if applicable
                self.event_edit.setText("")
                #self.event_edit.setReadOnly(True)
                # shows text that allocated on run
                self.swap_field_widget(self.event_label, self.event_alt_label)
                
        else:
            events = ["NA"]
            
        if events != ["NA"]:
            self.event_combo.addItem("Select Event")
        self.event_combo.addItems(events)
        
    
    def update_value_combo(self):
        #print ("update value combo")
        self.value_combo.clear()
        selected_type = self.rule_type_combo.currentText()
        if selected_type == None or selected_type == "Select Type":
            self.show_hide_row(4, False) 
            values = ["NA"]
        elif selected_type == "VLCB" or selected_type == "Gui":
            # For this just check that there is an event
            # If it's not "" or "NA" then it should have an on or off status
            # Default to on events
            selected_event = self.event_combo.currentText()
            if selected_event == "NA" or selected_event == "" or selected_event == "Select Event":
                self.show_hide_row(4, False) 
                self.value_combo.addItem("NA")
            else:
                self.show_hide_row(4, True, "Value:") 
                self.value_combo.addItem("on")
                self.value_combo.addItem("off")
        elif selected_type == "Loco":
            self.value_combo.addItems(LocoEvent.event_types)
            
        # For loco then uses LocoEvent.event_types list to create actions

    def update_value2_combo(self):
        #print ("Update value2 combo")
        selected_type = self.rule_type_combo.currentText()
        if selected_type == None or selected_type == "Select Type":
            self.show_hide_row(5, False) 
            nodes = ["NA"]
        else:
            self.value2_combo.clear()
            # If Loco then look at value1 (action) and set list here
            if selected_type == "Loco":
                # now look at action from value1
                loco_action = self.value_combo.currentText()
                if loco_action == "Set Speed":
                    self.value2_label.setText ("Speed:")
                    # change for spinbox
                    self.swap_field_widget(self.value2_label, self.value2_spinbox)
                elif loco_action == "Set Direction":
                    self.swap_field_widget(self.value2_label, self.value2_combo)
                    self.value2_combo.addItems(["Forward", "Reverse", "Toggle"])
                    self.value2_label.setText ("Direction:")
                elif loco_action == "Function":
                    # Function replaces value with both a spinbox and a combo
                    self.swap_field_widget(self.value2_label, self.value2_inner_widget)
                    self.value2_label.setText("Function setting:")
                # Others don't need another value - eg. Stop
                # So hide value2 - hide both spinbox and combo
                else:
                    self.value2_label.setText("")
                    self.value2_combo.hide()
                    self.value2_spinbox.hide()
                    self.value2_inner_widget.hide()
            else:
                self.show_hide_row(5, False) 
        # # For this just check that there is an event
        # # If it's not "" or "NA" then it should have an on or off status
        # # Default to on events
        # selected_event = self.event_combo.currentText()
        # if selected_event == "NA" or selected_event == "":
        #     self.show_hide_row(5, False) 
        #     self.value2_combo.addItem("NA")
        # else:
        #     self.show_hide_row(5, True, "Value:") 
        #     self.value2_combo.addItem("on")
        #     self.value2_combo.addItem("off")



    def _clear_layout(self, layout):
        """Helper to clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clear_layout(item.layout()) # Handle nested layouts


    # Gets data if valid and returns as a dict
    def save_step(self):
        rule_type = self.rule_type_combo.currentText()
        #loco_index = self.loco_combo.currentData()
        
        # All steps needed a name - but if empty can be created automatically
        self.name = self.name_lineedit.text()

        # Get additional data and place in a dict
        data_dict = {}        

        # If this matches the device model keys then it's an automation rule
        #if rule_type in device_model.event_map.keys():
        if rule_type == "VLCB" or rule_type == "Gui":
            
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
        elif rule_type == "Loco":
            # Loco step - so get loco number and DCC ID
            loco_no = self.node_combo.currentText()
            if loco_no == None or loco_no == "Select Node" or loco_no == "NA":
                print ("Invalid loco number")
                return
            else:
                data_dict["locoid"] = loco_no
                # If DCC ID then also get DCC ID value
                if loco_no == "Use DCC ID":        
                    dcc_id = self.event_edit.text()
                    try:
                        data_dict["dcc"] = int(dcc_id)
                        if not (1 <= dcc_id <= 9999):
                            print("DCC ID must be between 1 and 9999")
                            return
                    except ValueError:
                        print("DCC ID must be an integer")
                        return
            
            # Get the action and value
            action = self.value_combo.currentText()
            if action == None or action == "NA":
                print ("Invalid action")
                return
            else: 
                data_dict["action"] = action
            
            # If speed then use spinbox, else use combo
            if action == "Set Speed":
                speed = self.value2_spinbox.value()
                data_dict["speed"] = speed
            elif action == "Set Direction":
                data_dict["direction"] = self.value2_combo.currentText()
            elif action == "Function":
                data_dict["function"] = self.value2_inner_spinbox.value()
                data_dict["function_action"] = self.value2_inner_combo.currentText()
            else:
                # This shouldn't happen
                print ("Unknown command / value 2")
            
            # If no name given then can replace with a user friendly
            if self.name == "":
                self.name = f"Loco {loco_no} - {action}"
            
            # # Step parent, step_type, step_name, data={}
            # data_dict = {
            #     'loco_no': loco_no,
            #     'dcc_id': dcc_id,
            #     'action': action,
            #     'value': value
            #     }
            
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
    
    
    # Swaps the widget specified (eg. combobox with lineedit or spinbox)
    # Uses label_widget to find the row
    # New widget is the one to insert
    # defaults to hiding the old widget & showing the new
    def swap_field_widget(self, label_widget: QWidget, new_widget: QWidget, hide_old: bool = True):
        form_layout = self.layout()
        # Find the row and role of the label
        row, role = form_layout.getWidgetPosition(label_widget)
        if row == -1:
            raise ValueError("Label widget not found in the layout.")

        # Get the current field widget
        field_item = form_layout.itemAt(row, QFormLayout.FieldRole)
        if field_item is None:
            raise ValueError("No field widget found in the same row as the label.")

        old_widget = field_item.widget()
        
        # Set the new_widget visible
        new_widget.show()
        
        # Check if already set to the new_widget
        if old_widget == new_widget:
            return None	# No swap needed

        # Replace the widget
        form_layout.replaceWidget(old_widget, new_widget)

        # Optionally hide or delete the old widget
        if hide_old:
            old_widget.hide()


