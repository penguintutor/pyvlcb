import os, sys
from PySide6.QtWidgets import QMainWindow, QAbstractItemView
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
from PySide6.QtUiTools import QUiLoader
from devicemodel import device_model
from ruledialog import RuleDialog
from deviceevent import DeviceEvent
from locoevent import LocoEvent
from appevent import AppEvent
from guievent import GuiEvent
from timerevent import TimerEvent
from eventbus import event_bus


# Load the GUI resources.
# These first need to be compiled from the .qrd file
# pyside6-rcc guiresources.qrc -o guiresources.py
import guiresources

loader = QUiLoader()
#loader.registerCustomWidget(LayoutDisplay)
basedir = os.path.dirname(__file__)


app_title = "Rules Manager" 

class RulesWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        
        self.parent = parent
        
        self.ui = loader.load(os.path.join(basedir, "ruleswindow.ui"), None)
        self.ui.setWindowTitle(app_title)
        
        # Map to Classes
        self.event_map = {
            'VLCB': DeviceEvent,	# New replacement for "Device"
            'Device': DeviceEvent,
            'Loco': LocoEvent,
            'App': AppEvent,
            'Gui': GuiEvent,
            'Timer': TimerEvent
            }
        
        # Current page number
        self.page_number = 0

        # create list from UI elements to allow reference by index
        self.event_elements = {"event":[], "action":[], "options":[], "delete":[]}
        for i in range (0, 10):
            exec ("self.event_elements[\"event\"].append("+f"self.ui.rule_{i:02}_Label"+")")
            exec ("self.event_elements[\"action\"].append("+f"self.ui.action_{i:02}_Label"+")")
            exec ("self.event_elements[\"options\"].append("+f"self.ui.options_{i:02}_Label"+")")
            exec ("self.event_elements[\"delete\"].append("+f"self.ui.delButton_{i:02}"+")") 
            
        self.ui.buttonBox.accepted.connect(self.accept)
        
        self.ui.newEventButton.pressed.connect(self.new_event)
        
        # Connect the del buttons to the del_entry method
        self.ui.delButton_00.pressed.connect(lambda: self.del_entry(0))
        self.ui.delButton_01.pressed.connect(lambda: self.del_entry(1))
        self.ui.delButton_02.pressed.connect(lambda: self.del_entry(2))
        self.ui.delButton_03.pressed.connect(lambda: self.del_entry(3))
        self.ui.delButton_04.pressed.connect(lambda: self.del_entry(4))
        self.ui.delButton_05.pressed.connect(lambda: self.del_entry(5))
        self.ui.delButton_06.pressed.connect(lambda: self.del_entry(6))
        self.ui.delButton_07.pressed.connect(lambda: self.del_entry(7))
        self.ui.delButton_08.pressed.connect(lambda: self.del_entry(8))
        self.ui.delButton_09.pressed.connect(lambda: self.del_entry(9))
        
        self.update()
        
        # Hide page buttons
        self.show_hide_controls()
        
        self.ui.show()

    def del_entry(self, rule_id):
        event_bus.del_entry (rule_id)
        event_bus.save_rules()
        self.update()

    def update_list (self):
        num_rules = event_bus.num_rules()
        # Update all 10 entries - if we have enough entries on this page
        for i in range (0, 10):
            if i + (self.page_number * 10) >= num_rules:
                break
            this_entry = event_bus.event_rules[i + (self.page_number * 10)]
            self.event_elements['event'][i].setText(str(this_entry[0]))
            self.event_elements['action'][i].setText(str(this_entry[1]))
            self.event_elements['options'][i].setText("")
            self.event_elements['delete'][i].show()
        
    # Update entire display
    def update (self):
        
        # Hide all existing
        self.clear()
        
        # First check that we are on a valid page
        num_entries = event_bus.num_rules()
        if num_entries < 1:
            self.page_number = 0
        else:
            # num_pages is rounded down and is actually 1 less (index at 0)
            num_pages = int((num_entries - 1) / 10)
            if self.page_number > num_pages:
                self.page_number = num_pages
        self.show_hide_controls()
        # update the actual rules
        self.update_list()
   
    def new_event (self):
        dialog = RuleDialog()
        # Create dict with the details 
        event_dict = {}
        action_dict = {}
        if dialog.exec() == QDialog.Accepted:
            #print("Dialog Accepted!")
            selected_data = dialog.get_selected_values()
            event_details = selected_data['event']
            #event_type = device_model.get_type_node(event_details['node'])
            # For Device the node name / event name may be user friendly name - so instead get node_id and event_id
            if event_details['type'] == "VLCB":
                event_dict['node_id'] = device_model.name_to_key(event_details['node'])
#                 print (f"This {event_dict['node_id']}")
#                 print (f"Event dict {event_dict}")
#                 print (f"Event details {event_details}")
                event_dict['event_id'] = device_model.evname_to_evid(event_dict['node_id'], event_details['event'])
            # Add reset of details
            event_dict["node"] = event_details['node']
            event_dict["event"] = event_details['event']
            event_dict["value"] = event_details['value']
             
            # Action Details
            action_details = selected_data['action']
            #action_type = device_model.get_type_node(action_details['node'])
            if action_details['type'] == "VLCB":
                action_dict['node_id'] = device_model.name_to_key(action_details['node'])
                action_dict['event_id'] = device_model.evname_to_evid(action_dict['node_id'], action_details['event'])
            # Add reset of details
            action_dict["node"] = action_details['node']
            action_dict["event"] = action_details['event']
            action_dict["value"] = action_details['value']
            
#             print("Selected Values:")
#            for key, value in selected_data.items():
#                print(f"  {key}: {value}")
            # Convert response (dict in selected_data) into event objects
            event_instance = device_model.event_map[event_details['type']] (event_dict)
            action_instance = device_model.event_map[action_details['type']] (action_dict)
            #print (f"Adding {event_instance} : {action_instance}")
            # temp is there a problem with action_instance?
            event_bus.add_rule(event_instance, action_instance)
            event_bus.save_rules()
            
            # Update the GUI
            self.update()            
            
            
    # Show or hide controls based on whether more than 1 page
    # call this with event_bus.num_events() 
    def show_hide_controls (self):
        num_rules = event_bus.num_rules() 
        if num_rules > 10:
            self.ui.prevPageButton.show()
            self.ui.nextPageButton.show()
            self.ui.pageNumButton.show()
        else:
            self.ui.prevPageButton.hide()
            self.ui.nextPageButton.hide()
            self.ui.pageNumButton.hide()
        
    def clear (self):
        for i in range (0, 10):
            # set each of the values empty
            self.event_elements['event'][i].setText("")
            self.event_elements['action'][i].setText("")
            self.event_elements['options'][i].setText("")
            self.event_elements['delete'][i].hide()
        

    def display (self):
        self.ui.show()


    # hide entire windows
    def hide(self):
        self.ui.hide()

    
    # Accept button is pressed
    # If we don't have an existing texture then this is new
    # Otherwise we need to update the existing texture
    def accept(self):
        self.ui.hide()

