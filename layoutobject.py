# This is an abstract class - used for creating LayoutButton or LayoutLabel
# Layout Objects are anything on the layout that can display data and/or trigger events
# Typically labels or buttons, can be moved in relation to the layout

# position is relative to top left of the parent (QLabel)
# is be a percentage of the layout image size


import sys, math
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QBrush
from PySide6.QtCore import Qt, QPoint, QSize

class LayoutObject:
    def __init__ (self, parent, pos, id):
        self.parent = parent
        self.pos = pos # Pos is % of position of image
        self.id = id
        
    # Return position as pixels
    # Needs to consider that pixmap is different to label size
    # Only apply percentage to pixmap, but add in any offset due to label
    # Note that for pos (unlike size) then needs to be percentage of both
    # width and height
    # Normally leave argument to default - but if argument provided use that instead
    # useful if want to apply offset etc.
    def pixel_pos (self, pos=None):
        if pos == None:
            pos = self.pos
        label_size = self.parent.canvas_size
        image_size = self.parent.pixmap().size()
        # First calculate just on image size
        width = image_size.width() * pos[0] / 100
        height = image_size.height() * pos[1] / 100
        # width is left aligned, but need to add 1/2 of height offset
        height_diff = label_size.height() - image_size.height()
        if height_diff > 0:
            height += int(height_diff/2)
        return [width, height]

        
    # Get the mid-point of the object - useful for calc distance from click
    # All values as percentage
    def center_pos (self):
        return [
            self.pos[0] - (self.size[0] / 2),
            self.pos[1] - (self.size[1] / 2)
            ]
    
    # Calculate distance from click pos
    # both pos are percentage - returns scalar
    def distance (self, click_pos):
        center = self.center_pos()
        delta_x = click_pos[0] - center[0]
        delta_y = click_pos[1] - center[1]

        # Calculate the Euclidean distance
        return (math.sqrt(delta_x**2 + delta_y**2))
    
