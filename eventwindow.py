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
from editeventdialog import EditEventDialog
# Load the GUI resources.
# These first need to be compiled from the .qrd file
# pyside6-rcc guiresources.qrc -o guiresources.py
import guiresources

loader = QUiLoader()
#loader.registerCustomWidget(LayoutDisplay)
basedir = os.path.dirname(__file__)


app_title = "Event Manager" 

class EventWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        
        self.parent = parent
        
        self.ui = loader.load(os.path.join(basedir, "eventwindow.ui"), None)
        self.ui.setWindowTitle(app_title)

        # create list from UI elements to allow reference by index
        self.event_elements = {"event":[], "action":[], "options":[], "delete":[]}
        for i in range (0, 10):
            exec ("self.event_elements[\"event\"].append("+f"self.ui.event_{i:02}_Label"+")")
            exec ("self.event_elements[\"action\"].append("+f"self.ui.action_{i:02}_Label"+")")
            exec ("self.event_elements[\"options\"].append("+f"self.ui.options_{i:02}_Label"+")")
            exec ("self.event_elements[\"delete\"].append("+f"self.ui.delButton_{i:02}"+")")
            
        self.ui.buttonBox.accepted.connect(self.accept)
        
        self.ui.newEventButton.pressed.connect(self.new_event)
        
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
        self.ui.show()

   
    def del_entry (self, entry_id):
        # Delete secondary, then primary
        #todo remove entry
        pass

    
    def new_event (self):
        dialog = EditEventDialog()
        if dialog.exec() == QDialog.Accepted:
            #print("Dialog Accepted!")
            selected_data = dialog.get_selected_values()
            print("Selected Values:")
            for key, value in selected_data.items():
                print(f"  {key}: {value}")
        #else:
        #    print("Dialog Rejected!")
        
        
        
#         dialog = EditEventDialog()
#         if dialog.exec():
#             node, event = dialog.get_selected_values()
#             print(f"Selected Node: {node}")
#             print(f"Selected Event: {event}")
        
    def clear (self):
        for i in range (0, 10):
            # set each of the values empty
            self.event_elements['event'][i].setText("")
            self.event_elements['action'][i].setText("")
            self.event_elements['options'][i].setText("")
            self.event_elements['delete'][i].hide()
        
    # Update list of events
    def update (self):
        # Hide all existing
        self.clear()
        
#         num_groups = 0
#         for group in groups:
#             wall1_wall = self.builder.walls[group.primary_wall].name
#             #wall1_edge = self.builder.walls[group.primary_wall].il[group.primary_il].edge
#             # + 1 more user friendly starting at 1 (consistant with edit)
#             wall1_edge = group.primary_il.edge +1
#             wall1_string = f"Primary: {wall1_wall}, edge {wall1_edge}"
#             # Get type from primary
#             il_type = f"{group.primary_il.il_type}, {group.primary_il.step}"
#             
#             self.il_elements['edge1'][num_groups].setText(wall1_string)
#             wall2_wall = self.builder.walls[group.secondary_wall].name
#             wall2_edge = group.secondary_il.edge +1
#             wall2_string = f"Secondary: {wall2_wall}, edge {wall2_edge}"
#             self.il_elements['edge2'][num_groups].setText(wall2_string)
#             
#             self.il_elements['type'][num_groups].setText(il_type)
#             self.il_elements['delete'][num_groups].show()
#             
#             num_groups += 1
#         if (parent):
#             self.parent.update_all_views()
            

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

