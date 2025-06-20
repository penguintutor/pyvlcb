# Layout Objects are anything on the layout that can display data and/or trigger events
# This is a button, which is a image that can be clicked (press and release)


import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont
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
        print (f"Parent {parent}, pos {pos}, type {button_type}, settings {settings}")
        super().__init__(parent, pos)
        self.button_type = button_type,
        # default size is 5% width and 1:1
        if ('size' in settings.keys()):
            self.size = size
        else:
            self.size = (5, 5)
            
    # returns size as pixels rather than ratio
    def pixel_size (self):
        parent_size = self.parent.canvas_size
        width = parent_size.width() * self.size[0] / 100
        height = parent_size.width() * self.size[1] / 100
        return [width, height]
    
    def resize (self):
        print (f"Resize")
        print (f"Parent size {self.parent.canvas_size}")
        print (f"Pixel size {self.pixel_size()}")
        
    def draw (self):
        print (f"parent {self.parent} canvas {self.parent.canvas}")
        painter = QPainter(self.parent.canvas)
        painter.setPen(QColor("darkblue"))
        painter.drawRect(500, 500, 170, 150)
        painter.end()