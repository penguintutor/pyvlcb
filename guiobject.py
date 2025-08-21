# GuiObject - this is a collection of GUI elements (layoutobjects) that can be controlled together
# For example a point which has two buttons and a label
# Also maintains state of device (as received by events) and updates
# layout objects
class GuiObject:
    # object_type - eg. "point" (two buttons to select between), "toggle" (toggle can be used for lights etc. all buttons toggle)
    def __init__(self, object_type, name, data_dict):
        self.object_type = object_type
        self.name = name
        self.data = data_dict
        # state is used to track the state of the object
        # 0 is unknown
        # simple objects will typically have two states (+unknown)
        # eg. point will be 0 (unknown), 1 (pos 1), 2 (pos 2)
        # toggle will be 0 (unknown), 1 (on), 2 (off)
        # complex objects can have higher numbers and toggle counts down
        self.state_value = 0
        self.num_states = 2 # unknown plus 2 number states
        # if num_states is in the data_dict then overrides
        if 'num_states' in self.data:
            self.num_states = self.data['num_states']
            
        self.buttons = []
        self.labels = []
        
    def type (self):
        return object_type
        
    # Here pos is optional so it's moved to the end
    def add_label (self, label_id, label_type, settings, pos=(5,5)):
        self.labels.append (LayoutLabel(self, pos, label_id, label_type, settings))
        
    def add_button (self, button_id, button_type, settings, pos=(5,5)):
        self.labels.append (LayoutButton(self, pos, button_id, button_type, settings))
        
