# LayoutLabel
# displays a text label or similar
# Change does not depend on state - but clicking will often result in a toggle
# In settings
# click_type - "value", "toggle", "none"	# For button default = "value"
# click_value - only used if click_type = "value" - response to click (if not spplied set to index)

import sys
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QPen
from PySide6.QtCore import Qt, QPoint, QSize
from layoutobject import LayoutObject

# for type="text" then settings must include "text":"Text to display"
class LayoutLabel (LayoutObject):
    def __init__ (self, parent, pos, label_type, settings = {}):
        super().__init__(parent, pos)
        self.label_type = label_type
        ## get values from settings or set defaults
        self.settings = settings
        if 'click_type' in settings:
            self.click_type = settings['click_type']
        else:
            self.click_type = "toggle"
        if 'click_value' in settings:
            self.click_value = settings['click_value']
        else:
            # If click_value set to None then it will be looked up when first used by looking up index
            self.click_value = None
        self.min_size = 5 # min size for click area
        # default size is 5% width and 1:1
        # just set iniitially replaced with actual size later
        if ('size' in settings.keys()):
            self.size = settings['size']
        else:
            self.size = (5, 5)
        # set font size if not in settings
        # Gui settings just sets min, then max is calculated as *3
        if ('min_font_size' in settings.keys()):
            self.min_font_size = settings['min_font_size']
        else:
            self.min_font_size = 14
        if ('max_font_size' in settings.keys()):
            self.max_font_size = settings['max_font_size']
        else:
            # Default for max is 3 x min
            self.max_font_size = self.min_font_size * 3
        if ('font' in settings.keys()):
            self.font = settings['font']
        else:
            self.font = "LiberationSans-Bold"
        # set color
        if ('color' in settings.keys()):
            self.font_color = settings['color']
        else:
            self.font_color = "#000000"
        # Click enabled removed - use click_type = "none" to disable
            
        self.gui_node = None

    # Capitalize set to True to capitalize first letter (used for user friendly)
    def get_type_str (self, capitalize=False):
        if capitalize == True:
            return self.label_type.capitalize()
        return self.label_type

    # Returns a valid number - if not set then return 0
    def get_click_value (self):
        if self.click_value == None:
            return 0
        return self.click_value

    # Activate on a label is normally a toggle
    # activate sends to parent (guiobject)
    # This allows parent to set other objects as required
    # note that will call back to activate_value which get the value
    def activate (self):
        # If disabled then ignore
        #if self.click_enabled == False:
        #    return
        # Sends activate regardless - but if click_type=="none" will be effectively ignored
        index = self.get_index()
        self.parent.activate("LayoutLabel", index)

    # Create GUI node outside of constructor (consistant with layoutbutton)
    # Must be called after creating the object
    # Creates if not exist - either way returns gui_node
    def get_gui_node (self):
        if self.gui_node == None:
            self.gui_node = QStandardItem(f"Label {self.label_type} : {self.get_name()}")
        return self.gui_node
    
    # Returns as a nested dictionary ready to save
    def to_dict (self, guiobj):
        return {
            'object': "label",
            'guiobject': guiobj,
            'pos': self.pos,
            'label_type': self.label_type,
            'settings': self.settings
            }
    
    def get_name (self):
        if self.label_type == "text":
            return self.settings['text']
        else:
            return "Unknown"
        
    def get_long_name (self):
        return f"Label: {self.get_name()}"
            
    # What action does this have
    # Button is normally Activate, label is Toggle
    #def get_action_type (self):
    #    return "Toggle"
    
    # Get index position of the label
    # Normally add 1 if need user friendly name
    # See get_name
    def get_index (self):
        return self.parent.labels.index(self)
    
    def draw (self, painter):
        #print (f"Parent {self.parent} PP {self.layout_disp}")
        if self.label_type == "text":
            
            # In future could check for font override in settings
            # Liberation Sans Bold - common font on Raspberry Pi OS and other Linux
            painter.setFont(QFont(self.font, self.get_font_scale(self.min_font_size, self.max_font_size)))
            font_metrics = painter.fontMetrics()
            text_rect = font_metrics.boundingRect(self.settings['text'])
            # note that the standard drawText uses the baseline for y (ie. bottom of standar letters)
            # but to be consistant with the buttons need it to be top right - so translate
            #print (f"Text size {text_rect.width()} x {text_rect.height()}")
            # first get size as a percentage - rel=True needed for size or relative values
            self.size = self.layout_disp.pixel_to_percent([text_rect.width(), text_rect.height()], rel=True)
            # Ascent is like height but doesn't include below the baseline - eg g / q etc.)
            # convert it to percent, but only interested in the y value
            #print (f"Ascent actual {font_metrics.ascent()}")
            percent_null_ascent = self.layout_disp.pixel_to_percent([0, font_metrics.ascent()], rel=True)
            ascent = percent_null_ascent[1]
            #print (f"Pos y {self.pos[1]}, ascent {ascent}")
            # get a new y with offset (still percentage)
            draw_text_y = self.pos[1] + ascent
            # Set color
            pen = QPen (QColor(self.font_color))
            # Set the painter pen
            painter.setPen(pen)
            # Draw using normal x pos (still left) but shifted y pos
            painter.drawText(*self.pixel_pos([self.pos[0], draw_text_y], rel=False), self.settings['text'])
            
        
    # For label need to check for width and height as typically width significantly larger than height
    # return -1 if not a hit, or distance if it is
    # note that distance is still scalar distance from center - even if more to one side (distance from center)
    # click_pos is a percentage - same as dimensions of label
    def is_hit (self, click_pos):
        #print (f"Checking for click {click_pos}, Label {self.pos}, size {self.size}")
        # check for hit first
        if (
            click_pos[0] >= self.pos[0] and
            click_pos[0] <= self.pos[0] + self.size[0] and
            click_pos[1] >= self.pos[1] and
            click_pos[1] <= self.pos[1] + self.size[1]
            ):
            #print (f"Click {click_pos}, Label {self.pos}, size {self.size}")
            return self.distance (click_pos)
        else:
            return -1
        

    