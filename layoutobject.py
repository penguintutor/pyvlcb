# This is an abstract class - used for creating LayoutButton or LayoutLabel
# Layout Objects are anything on the layout that can display data and/or trigger events
# Typically labels or buttons, can be moved in relation to the layout

# position is relative to top left of the parent (QLabel)
# is be a percentage of the layout image size


import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QBrush
from PySide6.QtCore import Qt, QPoint, QSize

class LayoutObject:
    def __init__ (self, parent, pos):
        self.parent = parent
        self.pos = pos # Pos is % of position of image
        
    def get_object (self):
        pass
        
    # Return position as pixels
    # Needs to consider that pixmap is different to label size
    # Only apply percentage to pixmap, but add in any offset due to label
    # Note that for pos (unlike size) then needs to be percentage of both
    # width and height
    def pixel_pos (self):
        label_size = self.parent.canvas_size
        image_size = self.parent.pixmap().size()
        # First calculate just on image size
        width = image_size.width() * self.pos[0] / 100
        height = image_size.height() * self.pos[1] / 100
        # width is left aligned, but need to add 1/2 of height offset
        height_diff = label_size.height() - image_size.height()
        if height_diff > 0:
            height += int(height_diff/2)
        return [width, height]
    
    # return -1 if not a hit, or distance if it is
    def is_hit (self, click_pos):
        distance = self.distance (click_pos)
        #print (f"Click pos {click_pos}, obj pos {self.pos}, distance {distance}, size {self.scalar_size()}")
        if distance <= self.scalar_size():
            return distance
        else:
            return -1
    