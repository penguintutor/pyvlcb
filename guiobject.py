# GuiObject - this is a collection of GUI elements that can be controlled together
# For example a point which has two buttons and a label
class GuiObject:
    # object_type - eg. "point" (two buttons to select between), "toggle" (toggle can be used for lights etc. all buttons toggle)
    def __init__(self, object_type, data_dict):
        self.object_type = event_type
        self.data = data_dict
        
    def type (self):
        return object_type