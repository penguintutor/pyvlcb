# GuiObject - this is a collection of GUI elements (layoutobjects) that can be controlled together
# For example a point which has two buttons and a label
# Also maintains state of device (as received by events) and updates
# layout objects

from PySide6.QtGui import QStandardItemModel, QStandardItem
from layoutlabel import LayoutLabel
from layoutbutton import LayoutButton
from eventbus import event_bus
from guievent import GuiEvent

class GuiObject:
    # object_type - eg. "point" (two buttons to select between), "toggle" (toggle can be used for lights etc. all buttons toggle)
    def __init__(self, parent, object_type, name, data_dict):
        # parent is the gui object (Layout Display)
        # which is passed to LayoutObjects
        self.parent = parent
        self.object_type = object_type
        # device_type exists over all types - inc Gui / VLCB etc.
        self.device_type = "Gui"
        self.name = name 
        self.data = data_dict
        # state is used to track the state of the object
        # 0 is unknown
        # simple objects will typically have two states (+unknown)
        # eg. point will be 0 (unknown), 1 (pos 1), 2 (pos 2)
        # toggle will be 0 (unknown), 1 (on), 2 (off)
        # complex objects can have higher numbers and toggle counts up
        self.state_value = 0
        self.num_states = 2 # unknown plus on and off number states (don't count unknown)
        # if num_states is in the data_dict then overrides
        if 'num_states' in self.data:
            self.num_states = self.data['num_states']
            
        # Create a gui_node for displaying in QStandardItemModel
        # Read by device_model for inclusion in device tree
        self.gui_node = QStandardItem(f"GUI {self.object_type} : {self.name}")
            
        self.buttons = []
        self.labels = []
        
    # Set value from an event
    # Includes own events or triggers from elsewhere
    def set_value (self, value):
        self.state_value = value
        # Update elements
        for i in range (0, len(self.buttons)):
            # If unknown state then set to unknown
            if self.state_value == 0:
                self.buttons[i].value = 0
            # If this value then set to 1
            elif self.state_value == i + 1:
                self.buttons[i].value = 1
            # Otherwise set to off
            else:
                self.buttons[i].value = 2
        # Table is updated in mainwindow - based on GuiEvent
        # print (f"Value set to {self.state_value}")
        
        
    # Activate can be called from the GUI (eg node tree)
    # or from a child object
    # Update self and then send a GuiEvent
    def activate (self, click_type = "GuiObject", index=0 ):
        #print (f"Current {self.state_value} - Activating object {click_type} {index}")
        # If it's a gui and we have more than 2 states then 0 = prev, 1 = next
        if click_type == "GuiObject":
            if self.num_states > 2 and index == 0:
                self.state_value -= 1
                if self.state_value < 1:
                    self.state_value = 1
            elif self.num_states > 2 and index == 1:
                self.state_value += 1
                if self.state_value > self.num_states:
                    self.state_value = self.num_states
            # Otherwise it's a toggle
            else:
                # If state value unknown then set to 1
                if self.state_value == 0:
                    self.state_value = 1
                else:
                    # Toggle 1 to 2 and 2 to 1
                    self.state_value = 3 - self.state_value
        # Label (if enabled) is cyclic next button
        elif click_type == "LayoutLabel":
            self.state_value += 1
            if self.state_value > self.num_states:
                self.state_value = 1
        # Button - set value to button index + 1 (giving button1 / button2 etc.)
        elif click_type == "LayoutButton":
            self.state_value = index + 1
            
        #print (f"Now {self.state_value}")
 
        # Create and send GUI event
        event_bus.publish(GuiEvent({'name': self.name, 'value': self.state_value}))
        
    def get_ev_names (self):
        #print (f"Getting evs for {self.name}")
        list_names = []
        for label in self.labels:
            list_names.append(label.get_long_name())
        for button in self.buttons:
            list_names.append(button.get_long_name())
        #print (f"Returning {list_names}")
        return list_names
        
    def get_gui_node (self):
        return self.gui_node
    
    # Check if item is this node (or a child of this node)
    # Returns None (if not found)
    # Or object
    def check_item (self, item):
        # Is it this gui obj
        if self.gui_node == item:
            #print (f"This node {self.name}")
            return (self)
        # Is it a button
        for i in range (0, len(self.buttons)):
            if self.buttons[i].gui_node == item:
                return (self.buttons[i])
        # Is it a label
        for i in range (0, len(self.labels)):
            if self.labels[i].gui_node == item:
                return (self.labels[i])
        return None
        
    def type (self):
        return object_type
    
    def get_save_objects(self):
        data_list = [
                {
                    'object': "gui",
                    'type': self.object_type,
                    'name': self.name,
                    'settings': self.data
                }
            ]
        # Gather all objects into a data_list
        for button in self.buttons:
            data_list.append(button.to_dict(self.name))
        for label in self.labels:
            data_list.append(label.to_dict(self.name))
        return data_list
    
    def nearestToClick(self, click_pos, types="all"):
        nearest_object = None
        # set distance to a value far beyond any reasonable range (1000)
        # saves needing to test for a null value
        nearest_distance = 1000
        if types == "button" or types=="all":
            for button in self.buttons:
                hit_test = button.is_hit(click_pos)
                #print (f"Button {hit_test}")
                # Todo determine closest (ignore any < 0)
                if hit_test >=0 and hit_test < nearest_distance:
                    nearest_object = button
                    nearest_distance = hit_test
        if types == "label" or types=="all":
            for label in self.labels:
                hit_test = label.is_hit(click_pos)
                #print (f"Label {hit_test}")
                # Todo determine closest (ignore any < 0)
                if hit_test >=0 and hit_test < nearest_distance:
                    nearest_object = label
                    nearest_distance = hit_test
        if nearest_object == None:
            return None
        # get offset to the nearest object
        #offset_percentage = nearest_object.get_offset(click_pos)
        #self.click_offset = QPoint(*nearest_object.pixel_pos(offset_percentage))
        return nearest_object, nearest_distance
        
    # Here pos is optional so it's moved to the end
    def add_label (self, label_type, settings, pos=(5,5)):
        self.labels.append (LayoutLabel(self, pos, label_type, settings))
        self.gui_node.appendRow(self.labels[-1].get_gui_node())
        
    def add_button (self, button_type, settings, pos=(5,5)):
        self.buttons.append (LayoutButton(self, pos, button_type, settings))
        self.gui_node.appendRow(self.buttons[-1].get_gui_node ())
        
    # Paint (Draw) all objects on painter within layoutdisplay
    def paint (self, painter):
        for label in self.labels:
            label.draw(painter)
        
        for button in self.buttons:
            button.draw(painter)