# This is an abstract class - used for creating LayoutButton or LayoutLabel
# Layout Objects are anything on the layout that can display data and/or trigger events
# Typically labels or buttons, can be moved in relation to the layout

# position is relative to top left of the parent (QLabel)
# is be a percentage of the layout image size

import sys, math
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QBrush
from PySide6.QtCore import Qt, QPoint, QSize

# Note the parent is the parent of the gui where it's displayed
# So not guiobjects which typically owns these, but typically LayoutDisplay
class LayoutObject:
    def __init__ (self, parent, pos):
        self.parent = parent
        # Layout display is the parent of the gui object
        # use this to make code cleaner and to be able
        # to get scaling details etc.
        self.layout_disp = parent.parent
        self.pos = pos # Pos is % of position of image
        # device_type exists over all types - inc Gui / VLCB etc.
        # all layout objects are device_type Gui
        self.device_type = "Gui"
        
    # What action does this have
    # Button is normally Value, label is Toggle
    def get_action_type (self):
        return self.click_type
        
    # Return position as pixels
    # Needs to consider that pixmap is different to label size
    # Only apply percentage to pixmap, but add in any offset due to label
    # Note that for pos (unlike size) then needs to be percentage of both
    # width and height
    # Normally leave argument to default - but if argument provided use that instead
    # useful if want to apply offset etc.
    # aka percent_to_pixel
    # rel is whether factor in height diff or not
    # If pos not defined then rel=None becomes False - as need to position within entire label
    # if pos is defined and rel=None then becomes True - as likely calc offset
    def pixel_pos (self, pos=None, rel=None):
        if pos == None:
            pos = self.pos
            if rel==None:
                rel = False
        elif rel==None:	# pos is supplied and rel=None - so set to true
            rel = True
        label_size = self.layout_disp.canvas_size
        image_size = self.layout_disp.pixmap().size()
        # First calculate just on image size
        width = image_size.width() * pos[0] / 100
        height = image_size.height() * pos[1] / 100
        # width is left aligned, but need to add 1/2 of height offset
        if rel == False:
            height_diff = label_size.height() - image_size.height()
            if height_diff > 0:
                height += int(height_diff/2)
        return [width, height]

    # Activates locally and sets value
    # not to be confused with activate which calls parent class on this object
    # perform required action (eg. set / toggle and return value)
    def activate_value (self, current_value, num_states):
        print (f"Value is {current_value, num_states}")
        if self.click_type == "none":
            return current_value
        elif self.click_type == "toggle":
            new_value = current_value + 1
            if new_value > num_states:
                new_value = 1
            return new_value
        elif self.click_type == "value":
            # If click value not set then get it
            if self.click_value == None:
                self.click_value = self.get_index() + 1
            return self.click_value
            
        # temp just return current - not yet handled
        return current_value

    # Get a string representing action
    # eg. "Value {}"
    def get_action_str (self):
        # capitalize first letter using the title method
        return_string = self.click_type.title()
        if self.click_type == "value":
            if self.click_value == None:
                self.click_value = self.get_index() + 1
            return_string += f" {self.click_value}"
        
        return return_string

    # Called when clicked and layout in control mode
    def controlButtonClick(self):
        self.activate()

    # If window scales then change font size accordingly
    # only approx - based on min and max font size
    # image W 500 = font min size (never go smaller than this)
    # image W 2000 = font max size (never go bigger than this)
    def get_font_scale (self, min_size, max_size):
        # First check max > min - otherwise just return min
        if max_size < min_size:
            return min_size
        # uses pixemap width for scaling only
        image_size = self.layout_disp.pixmap().size()
        # font scale is between 0 and 1 - where 0 is min size and 1 = max size
        # Max would only be reached on large screen (min HD) where the width of the image
        # is primary length - in reality more likely to be between min and 1/2 way
        # between min and max - eg. min 14, max 42 - typically 24 to 30
        font_scale = (image_size.width() - 500) / 1500
        if font_scale < 0:
            font_scale = 0
        if font_scale > 1:
            font_scale = 1
        # apply scaling factor to difference between min and max
        scale_up = (max_size - min_size) * font_scale
        #print (f"Min {min_size}, Max {max_size}, Scale {scale_up}")
        # return as int - effectively round down
        return int(min_size + scale_up)
        
    # Get the mid-point of the object - useful for calc distance from click
    # All values as percentage
    def center_pos (self):
        return [
            self.pos[0] + (self.size[0] / 2),
            self.pos[1] + (self.size[1] / 2)
            ]
    
    # Calculate distance from click pos
    # both pos are percentage - returns scalar
    def distance (self, click_pos):
        center = self.center_pos()
        delta_x = click_pos[0] - center[0]
        delta_y = click_pos[1] - center[1]

        # Calculate the Euclidean distance
        return (math.sqrt(delta_x**2 + delta_y**2))
    
    def get_offset (self, click_pos):
        offset_x = click_pos[0] - self.pos[0]
        offset_y = click_pos[1] - self.pos[1]
        return [offset_x, offset_y]