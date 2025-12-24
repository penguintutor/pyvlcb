# Dialog for creating a new AutomationSequence.

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget, QFormLayout, QLineEdit, QSpinBox, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from automationrule import AutomationRule
from automationsequence import AutomationStep, AutomationSequence
from automationdialogrows import AutomationDialogRows
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

        # Used to track if loading a new dialog and whether type has changed
        # If current type equals new selected type then no need to reload combos
        self.current_type = "New"
        # same for current node (row 2)
        self.current_row2 = "New"
        # current event (row 3)
        self.current_row3 = "New"
        # current value (row 4)
        self.current_row4 = "New"
        # current value2 (row 5)
        self.current_row5 = "New"

        self.setLayout(QFormLayout())

        self.rows = AutomationDialogRows(self, self.layout())
        
        
        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_step)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        self.layout().addRow(button_box)
               
        # Update the rows
        self.update_rows ()
            

    def update_rows (self):
        # disable signals - prevents multiple calls during update
        self.rows.enable_combo_signals(False)

        # If initial open and step is not None then set current title and type
        if self.current_type == "New" and self.step != None:
            self.rows.set_lineedit_text(0, self.step.get('name'))
            self.rows.set_combo_text(1, self.step.get('type'))

        # Get form type and call appropriate method to set up the form
        form_type = self.rows.get_type_text()
        if form_type == None:
            self.form_selected_none()
        elif form_type == "VLCB":
            self.form_selected_vlcb()
        elif form_type == "Loco":
            self.form_selected_loco()
        elif form_type == "User Interface":
            self.form_selected_gui()
        elif form_type == "App":
            self.form_selected_app()
        else:
            self.form_selected_none()

        # enable signals
        self.rows.enable_combo_signals(True)

    def _hide_rows (self, row_index ):
        # Hide all rows from row_index to 5
        for i in range (row_index, 6):
            self.rows.show_hide_row(i, False) 

    def _reset_row_currents (self, from_row, type="VLCB"): 
        # used to reset current row trackers if prev combo has changed  
        if from_row <= 2:
            self.current_row2 = "Select Node"
        if from_row <= 3:
            if type == "Loco":
                self.current_row3 = "Select Loco"
            else:
                self.current_row3 = "Select Event"
        if from_row <= 4:
            if type == "Loco":
                self.current_row4 = "Select Action"
            else:
                self.current_row4 = "default"
        if from_row <= 5:
            self.current_row5 = "default"

    def _set_input_types (self, type="default", mode="default"):
        """Set the input types based on type."""
        # Type is the main type (VLCB, Loco, GUI, App)
        # Mode is if special setting (eg. Loco has "non-dccid" for loco no)
        # Used in single method so all updates can be made here and relected in the other types
        #if type == "Loco" and mode == "non-dccid":
        #    self.rows.set_field_type(3, "fieldlabel")  # Event is label
        #elif type == "Loco":
        #    self.rows.set_field_type(3, "lineedit")  # Event is lineedit for DCC ID
        # For loco manage within selection - for others set row 3 back to combo
        if type == "Loco":
            pass
        # Default for all others
        else:
            self.rows.set_field_type(3, "combo")  # Event is combobox

    def form_selected_none (self):
        self._hide_rows(2)

    def form_selected_vlcb (self):
        self._set_input_types(type="VLCB")
        self.rows.show_hide_row(2, True, "Node:")    # Show node row
        # Hide remaining rows (can re-enable later if required)
        self._hide_rows(3)    # Hide remaining rows (from event onwards)
        # if  current type has changed then generate node list
        if self.current_type != "VLCB":
            node_items = ["Select Node"] + device_model.get_nodes_names("VLCB", null_events=False)
            # if no nodes then just show NA
            if node_items == ["Select Node"]:
                node_items = ["NA"]
            self.rows.combo_add_items(2, node_items)
            if self.current_type == "New" and self.step != None:
                # Set based on loaded step
                self.rows.set_combo_text(2, device_model.key_to_name(self.step['data']['node_id'], "VLCB"))
            else:
                #  If VLCB is just selected and it's not loading existing step then set all other items to default
                self._reset_row_currents(2, type="VLCB")    # Reset from node onwards
                #self._hide_rows(3)    # Hide remaining rows (from event onwards)
                self.current_type = "VLCB"
                return
        # Reach here then VLCB was already selected or we have attempted to load from step
        self.current_type = "VLCB"
        # Node selection is already populated - check for a value
        selected_node = device_model.name_to_key(self.rows.get_combo_text(2), "VLCB")
        # If this was new and not loaded or moved back to "Select Node" then return here - need to select node first
        if selected_node == None:
            self.current_row2 = "Select Node"
            return
        #print (f"selected node {selected_node} curr {self.current_row2}")
        # Set Event to visible
        self.rows.show_hide_row(3, True, "Event:")
        if self.current_row2 == "New" or selected_node != self.current_row2:
            # node is different to current - so update event list
            event_items = ["Select Event"] + device_model.get_events(selected_node, "VLCB")    
            if event_items == ["Select Event"]:
                event_items = ["NA"]
            self.rows.combo_add_items(3, event_items)
            
            # Hide remaining - can re-enable later if selected
            self._hide_rows(4)    # Hide remaining rows (from value onwards)
            if self.current_row3 == "New" and self.step != None:
                # Set based on loaded step
                #print (f"Raw event {self.step['data']['event']}, as name {device_model.key_to_name(self.step['data']['event'], 'VLCB')}")
                self.rows.set_combo_text(3, device_model.key_to_name(self.step['data']['event'], "VLCB"))
            else:
                # If node is just selected and it's not loading existing step then set all other items to default
                self._reset_row_currents(3, type="VLCB")    # Reset from event onwards
                #self._hide_rows(4)    # Hide remaining rows (from value onwards)
                self.current_row2 = selected_node
                return
        self.current_row2 = selected_node
        # Reach here then event was already selected or we have attempted to load from step
        # Read in row 3 (event) and check for change
        selected_event = self.rows.get_combo_text(3)
        if selected_event == None or selected_event == "Select Event":
            self._hide_rows(4)    # Hide remaining rows (from value onwards)
            self.current_row3 = "Select Event"
            return
        # show value field
        self.rows.show_hide_row(4, True, "Value:")
        #print (f"selected event {selected_event} curr {self.current_row3}")
        if self.current_row3 == "New" or selected_event != self.current_row3:
            # event is different to current - so update value list
            # For vlcb then value is on / off depending on event (no select default to on)
            value_items = ["on", "off"]
            self.rows.combo_add_items(4, value_items)
            
            if self.current_row4 == "New" and self.step != None:
                # Set based on loaded step
                self.rows.set_combo_text(4, self.step['data']['value'])
            # value 2 not used - set defaults and hide value 2
            self._reset_row_currents(4, type="VLCB")    # Reset from value onwards
            #self._hide_rows(5)    # Hide remaining rows (from value2 onwards)
        self.current_row3 = selected_event
        # Don't need to check value as there are no fields below it
        

    def form_selected_loco (self):
        print (f"Loco selected action current row4 {self.current_row4}")
        self._set_input_types(type="Loco")
        self.rows.show_hide_row(2, True, "Loco No.:")    # Show loco row
        # Hide remaining rows (can re-enable later if required)
        self._hide_rows(3)    # Hide remaining rows (from DCC ID onwards)
        # if  current type has changed then generate node list
        if self.current_type != "Loco":
            #node_items = ["Select Loco"] + [f"ID {i}" for i in range(1, self.num_locos_req + 1)] + ["Use DCC ID"]
            node_items = ["Select Loco"] + [device_model.key_to_name(i, "Loco") for i in range(1, self.num_locos_req + 1)] + ["Use DCC ID"]
            self.rows.combo_add_items(2, node_items)
            if self.current_type == "New" and self.step != None:
                # Set based on loaded step
                locoid = self.step['data'].get('locoid')
                if locoid is not None:
                    self.rows.set_combo_text(2, device_model.key_to_name(locoid, "Loco"))
                # There should be only one of locoid and dccid if both then locoid takes precedence
                # If dccid then set to Use DCC ID which will load if appropriate
                elif self.step['data'].get('dccid') is not None:
                    self.rows.set_combo_text(2, "Use DCC ID")
            else:
                #  If Loco is just selected and it's not loading existing step then set all other items to default
                if self.current_type != "New":
                    self._reset_row_currents(2, type="Loco")    # Reset from node onwards if not new
                self.current_type = "Loco"
                return
        self.current_type = "Loco"
        # Reach here then Loco was already selected or we have attempted to load from step
        # or if DCC ID still need to attempt to load

        # Loco selection is already populated - check for a value
        selected_loco = self.rows.get_combo_text(2)
        if selected_loco == None or selected_loco == "Select Loco":
            self.current_row2 = "Select Loco"
            print ("Hiding rows from 3")
            self._hide_rows(3)    # Hide remaining rows (from DCC ID onwards)
            return
        # If DCC ID then attempt to load
        elif selected_loco == "Use DCC ID":
            self.rows.set_field_type(3, "lineedit")  # Event is lineedit for DCC ID
            self.rows.show_hide_row(3, True, "DCC ID:")
            # Set edit field (show label later)
            # If loading from step then set DCC ID if present
            if self.current_row2 == "New" and self.step != None:
                dccid = self.step['data'].get('dccid')
                if dccid is not None:
                    self.rows.set_lineedit_text(3, device_model.key_to_name(dccid, "Loco"))
            # Continue later regardless of value as only verify on save
        else:
            # A Loco ID is selected so show field label 
            # These says allocated at run time
            self.rows.show_hide_row(3, True, "DCC ID:")
            self.rows.set_field_type(3, "fieldlabel")  # Event is label
        self.current_row2 = selected_loco
        # note curent_row3 is not used as row2 has the same meaning
        
        # Don't need to check further rows as doesn't affect other fields
        #loco_id = device_model.name_to_key(self.rows.get_combo_text(2), "Loco")

        ## Now add Action field (row  as dccid is row 3)
        self.rows.show_hide_row(4, True, "Action:")
        print (f"Loco action current row4 {self.current_row4}")
        # Actions aren't dependent on loco so just add when new
        if self.current_row4 == "New":
            
            action_items = ["Select Action"] + LocoEvent.get_action_names()
            self.rows.combo_add_items(4, action_items)
            
            # Hide remaining - can re-enable later if selected
            self._hide_rows(5)    # Hide remaining rows (from value2 onwards)
            if self.current_row4 == "New" and self.step != None:
                self.rows.set_combo_text(4, self.step['data']['action'])
            else:
                # If node is just selected and it's not loading existing step then set all other items to default
                self._reset_row_currents(4, type="Loco")    # Reset from event onwards
                self._hide_rows(5)    # Hide remaining rows (from value onwards)
                self.current_row4 = "Select Action"
                return
        selected_action = self.rows.get_combo_text(4)
        
        if selected_action == None or selected_action == "Select Action":
            self.current_row4 = "Select Action"
            self._hide_rows(5)    # Hide remaining rows (from value2 onwards)
            return
        # show value field
        self.rows.show_hide_row(5, True, "Value:")

        if self.current_row5 == "New" or selected_action != self.current_row4:
            # action is different to current - so update value list
            # Options depends upon action - due to number of options
            # this is moved into AutomationDialogRows
            # if it's new then send the value to the setup
            if self.current_row5 == "New" and self.step != None:
                data = self.step.get('data')
                self.rows.loco_action_setup(selected_action, data)
            else:
                self.rows.loco_action_setup(selected_action)
            
        self.current_row4 = selected_action
        # row5 value doesn't matter as long as set to not New
        self.current_row5 = "Select Value"
        

    def form_selected_gui (self):
        pass

    def form_selected_app (self):
        pass 
        
    def old (self):
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
        elif form_type == "User Interface": # GUI Event
            self.node_combo.setVisible(True)
            self.node_label.setText("Node:")
            # Loco uses self.event_edit rather than combo - swap back here
            self.swap_field_widget(self.event_label, self.event_combo)
            self.event_label.setText("Action:")
            # value only shown if action is not toggle
            self.value_combo.setVisible(False)
            #self.value_label.setText("Value:")
            # Value (eg. speed)
            self.value2_combo.setVisible(False)
            #self.value2_label.setText("Value:")
        elif form_type == "App": # App Event eg wait
            self.node_combo.setVisible(True)
            self.node_label.setText("Command:")
            # Use self.event_edit rather than combo
            self.swap_field_widget(self.event_label, self.event_edit)
            self.event_label.setText("Arguments:")
            # value / value 2 not required
            self.value_combo.setVisible(False)
            #self.value_label.setText("Value:")
            # Value (eg. speed)
            self.value2_combo.setVisible(False)
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
            # If this type is one of the device_nodes then get from device_model
            if selected_type == "VLCB":
                nodes = device_model.get_nodes_names(selected_type, null_events=False)
            elif selected_type == "User Interface":
                nodes = device_model.get_nodes_names("Gui", null_events=False)
                #print (f"GUI Nodes {nodes}")
            elif selected_type == "Loco":
                # Loco does ont use "node" reference so create list of loco numbers
                # then add to GUI and return 
                nodes = ["Select Loco"]
                # Add available IDs if required
                if self.num_locos_req > 0:
                    nodes += [f"ID {i}" for i in range(1, self.num_locos_req + 1)]
                # Always offer option to use a DCC ID directly
                nodes.append("Use DCC ID")
            elif selected_type == "App":
                # For app then just hard code some options for now
                nodes = ["Select Command", "Wait", "Set Variable"]
                # Could add others in future
                # Eg. Log Message
                # Does not include label or jump (handled as separate types)

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
        #print (f"Updating event combo {index}")
        self.event_combo.clear()
        # Updates the event_combo based on the selected node.
        selected_node = self.node_combo.currentText()
        if selected_node == None or selected_node == "Select Node" or selected_node == "NA":
            events = ["NA"]
            self.show_hide_row(3, False)
            #print ("Hiding event row as no node selected")
            return
        elif selected_type == "VLCB":
            # convert to node_key
            node_key = device_model.name_to_key(selected_node, selected_type)
            #print (f"Type {selected_type} Node {selected_node} key {node_key}")
            events = device_model.get_events(node_key, selected_type)
            #print (f"Events {events}")
            if events == []:
                events = ["NA"]
            # Show the event field
            self.show_hide_row(3, True, "Event:") 
            # Also hide value 2 - not used for vlcb/gui
            self.show_hide_row(5, False) 
        elif selected_type == "User Interface":
            # convert to node_key
            node_key = device_model.name_to_key("Gui", selected_type)
            events = device_model.get_events(node_key, selected_type)
            # Shouldn't get a blank response - but check anyway
            if events == []:
                events = ["NA"]
            # Show the event field
            self.show_hide_row(3, True, "Action:") 
            # Also hide value 2 - not used for vlcb/gui
            self.show_hide_row(5, False) 
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
            # Hide value 2 (next field is action)
            self.show_hide_row(5, False)    # Hide value2 row
        elif selected_type == "App":
            # For App then event_edit is used for arguments
            # Event field (and optional value) depends upon value of node
            if selected_node == "Select Command":
                events = ["NA"]
                self.show_hide_row(3, False)    # Hide event row
            else:
                if selected_node == "Wait":
                    self.event_label.setText("Delay:")
                    # For wait then event is time in seconds (as text)
                    self.swap_field_widget(self.event_label, self.event_edit)
                elif selected_node == "Set Variable":
                    self.event_label.setText("Variable name:")
                    # For set variable then event is variable name from combo
                    self.swap_field_widget(self.event_label, self.event_combo)
                    variables = device_model.get_variable_names()
                    variables.append("New Variable")
                    self.event_combo.addItems(variables)
                    
            # Hide value 2 (not used)
            self.show_hide_row(5, False)    # Hide value2 row
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
        elif selected_type == "VLCB" or selected_type == "User Interface":
            # For this just check that there is an event
            # If it's not "" or "NA" then it should have an on or off status
            # Default to on events
            selected_event = self.event_combo.currentText()
            if selected_event == "NA" or selected_event == "" or selected_event == "Select Event" or selected_event== "Toggle":
                self.show_hide_row(4, False) 
                self.value_combo.addItem("NA")
            else:
                # May want to add other values for Gui type in future
                # eg. Set with a specific value
                self.show_hide_row(4, True, "Value:") 
                self.value_combo.addItem("on")
                self.value_combo.addItem("off")
        elif selected_type == "Loco":
            self.value_combo.addItem("Select Action")
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
                #print (f"Loco action is {loco_action}")
                if loco_action == None or loco_action == "NA" or loco_action == "Select Action":
                    self.show_hide_row(5, False) 
                    #return
                elif loco_action == "Set Speed":
                    self.show_hide_row(5, True, "Speed:") 
                    #self.value2_label.setText ("Speed:")
                    # change for spinbox
                    self.swap_field_widget(self.value2_label, self.value2_spinbox)
                elif loco_action == "Set Direction":
                    self.show_hide_row(5, True, "Direction:") 
                    self.swap_field_widget(self.value2_label, self.value2_combo)
                    self.value2_combo.addItems(["Forward", "Reverse", "Toggle"])
                    #self.value2_label.setText ("Direction:")
                elif loco_action == "Function":
                    self.show_hide_row(5, True, "Function setting:")
                    # Function replaces value with both a spinbox and a combo
                    self.swap_field_widget(self.value2_label, self.value2_inner_widget)
                    #self.value2_label.setText("Function setting:")
                # Others don't need another value - eg. Stop
                # So hide value2 - hide both spinbox and combo
                else:
                    self.show_hide_row(5, False) 
                    #self.value2_label.setText("")
                    #self.value2_combo.hide()
                    #self.value2_spinbox.hide()
                    #self.value2_inner_widget.hide()
            else:
                self.show_hide_row(5, False) 


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
        rule_type = self.rows.get_combo_text(1)
        if rule_type == None or rule_type == "Select Type":
            QMessageBox.warning(self, "Invalid Type", "Please select a valid rule type.")
            return
        # All steps needed a name - but if empty can be created automatically
        self.name = self.rows.get_linedit_text(0).strip()

        # Get additional data and place in a dict
        data_dict = {}        

        if rule_type == "VLCB":          
            # If it's vlcb then convert node to node_id
            node = self.rows.get_combo_text(2)
            if node == None or node == "Select Node" or node == "NA":
                QMessageBox.warning(self, "Invalid Node", "Please select a valid node.")
                return
            data_dict['node_id'] = device_model.name_to_key(node)
            event = self.rows.get_combo_text(3) 
            if event == None or event == "Select Event" or event == "NA":
                QMessageBox.warning(self, "Invalid Event", "Please select a valid event.")
                return
            data_dict['event'] = event
            # Value should not return an invalid value but check anyway
            value = self.rows.get_combo_text(4)
            if value == None or value == "NA":
                QMessageBox.warning(self, "Invalid Value", "Please select a valid value.")
                return
            data_dict['value'] = value
            
            # If no name given then can replace with a user friendly
            if self.name == "":
                self.name = f"{rule_type}, {data_dict['node_id']} - {data_dict['event']} - {data_dict['value']}"
            
            # Return as a dict - let Automation Sequence convert into an Automation Step
            self.step = {"type": rule_type, "name": self.name, "data" : data_dict}
        elif rule_type == "User Interface":
            
            node = self.node_combo.currentText()
            if node == None or node == "Select Node" or node == "NA":
                # todo replace with qmessage - also see other print messages
                print ("Invalid node")
                return
            data_dict['node_id'] = device_model.name_to_key(node, type="Gui")
            event = self.event_combo.currentText()
            if event == None or event == "Select Action" or event == "NA":
                print ("Invalid event")
                return
            data_dict['action'] = event

            if data_dict['action'] != "Toggle":

                # Value should not return an invalid value but check anyway
                value = self.value_combo.currentText()
                if value == None or value == "NA":
                    print ("Invalid value")
                    return
                data_dict['value'] = value
            else:
                value = ""            
            # If no name given then can replace with a user friendly
            if self.name == "":
                self.name = f"{rule_type}, {data_dict['node_id']} - {data_dict['action']}"
                if value != "":
                    self.name += f" - {value}"
            
            # Return as a dict - let Automation Sequence convert into an Automation Step
            self.step = {"type": "Gui", "name": self.name, "data" : data_dict}
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
                        if not (1 <= data_dict["dcc"] <= 9999):
                            print("DCC ID must be between 1 and 9999")
                            return
                    except ValueError:
                        print("DCC ID must be an integer")
                        return
            
            # Get the action and value
            action = self.value_combo.currentText()
            if action == None or action == "NA" or action == "Select Action":
                print ("Action, not selected")
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
                return
            
            # If no name given then can replace with a user friendly
            if self.name == "":
                self.name = f"Loco {loco_no} - {action}"
            
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

                


