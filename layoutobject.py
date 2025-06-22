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
        #print (f"Object {parent} {pos}")
        self.parent = parent
        self.pos = pos	# Pos is % of position
        
    # Return position as percentage
    # Note that for pos (unlike size) then needs to be percentage of both
    # width and height
    def pixel_pos (self):
        parent_size = self.parent.canvas_size
        width = parent_size.width() * self.pos[0] / 100
        height = parent_size.height() * self.pos[1] / 100
        return [width, height]