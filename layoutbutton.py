# Layout Objects are anything on the layout that can display data and/or trigger events
# This is a button, which is a image that can be clicked (press and release)

import sys
import math
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QBrush
from PySide6.QtCore import Qt, QPoint, QSize
from layoutobject import LayoutObject

# button_type - eg. circle / square / diamond / image
# additional settings are passed as a dict (eg. color_on, color_off, color_unknown - image_file (if applicable))
# size where provided should be a percentage fo the image size

# position is relative to top left of the parent (QLabel)
# is be a percentage of the layout image size

# size if supplied is x,y
# all dimensions are in relation to width - not height
# so that if say 5,5 then it will be 1:1 - even for landscape image


class LayoutButton (LayoutObject):
    def __init__ (self, parent, pos, button_type, settings = {}):
        #print (f"Button Parent {parent}, pos {pos}, type {button_type}, settings {settings}")
        super().__init__(parent, pos)
        self.button_type = button_type
        # Colours unknown, on, off
        self.button_colors = ["#444444", "#00FF00", "#FF4444"]
        self.settings = settings
        self.min_size = 5 # min size for click area (actual size can be smaller - this is just for clicks)
        # default size is 5% width and 1:1
        if ('size' in settings.keys()):
            self.size = settings['size']
        else:
            self.size = (4, 4)
        # Create gui_node through get_gui_node
        # Initially set to None so know it doesn't exist
        self.gui_node = None
        # value is 0 (not known), 1 = on, 2 = off
        if ('value' in settings.keys()):
            self.value = settings['value']
        else:
            self.value = 0
        
    def activate (self):
        index = self.get_index()
        self.parent.activate("LayoutButton", index)
        
    # What action does this have
    # Button is normally Activate, label is Toggle
    def get_action_type (self):
        return "Activate"
        
    def get_type_str (self):
        return self.button_type
        
    # Create GUI node outside of constructor as it needs to find it's index
    # Must be called after creating the object
    # Creates if not exist - either way returns gui_node
    def get_gui_node (self):
        if self.gui_node == None:
            self.gui_node = QStandardItem(f"Button {self.button_type} : {self.get_name()}")
        return self.gui_node

    
    # Get name based on index number of button (starts at 1)
    # Is 1 higher than the list position which starts at 0
    def get_name (self):
        return (self.get_index()+1)
    
    # Get index position of the button
    # Normally add 1 if need user friendly name
    # See get_name
    def get_index (self):
        return self.parent.buttons.index(self)

    # Returns as a nested dictionary ready to save
    def to_dict (self, guiobj):
        return {
            'object': "button",
            'guiobject': guiobj,
            'pos': self.pos,
            'button_type': self.button_type,
            'settings': self.settings
            }
            
    # return -1 if not a hit, or distance if it is
    def is_hit (self, click_pos):
        distance = self.distance (click_pos)
        #print (f"Click pos {click_pos}, obj pos {self.pos}, distance {distance}, size {self.scalar_size()}")
        if distance <= self.scalar_size():
            return distance
        else:
            return -1
            
    # scalar size is an effective size which is clickable
    # this is a circular area such as used in a touch screen
    # may be strange if clicking with accurate mouse click, but
    # not a particular concern
    # must be at least min size
    def scalar_size (self):
        largest_size = 0
        # in this case uses largest of width / height
        if self.size[0] > self.size[1]:
            largest_size = self.size[0]
        else:
            largest_size = self.size[1]
        if largest_size < self.min_size:
            largest_size = self.min_size
        return largest_size
            
    # returns size as pixels rather than ratio
    def pixel_size (self):
        #label_size = self.parent.canvas_size
        image_size = self.layout_disp.pixmap().size()
        width = image_size.width() * self.size[0] / 100
        height = image_size.width() * self.size[1] / 100
        return [width, height]
           
    def draw (self, painter):
        painter.setBrush(QColor(self.button_colors[self.value]))
        
        if self.button_type == "rect":
            painter.drawRect(*self.pixel_pos(), *self.pixel_size())
        elif self.button_type == "circle":
            painter.drawEllipse(*self.pixel_pos(), *self.pixel_size())
