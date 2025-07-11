# LayoutLabel
# displays a text label or similar


import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont
from PySide6.QtCore import Qt, QPoint, QSize

class LayoutLabel:
    def __init__ (self, parent, pos, label_type, settings = {}):
        super().__init__(parent, pos)
        self.label_type = label_type
        self.settings = settings
        self.min_size = 5 # min size for click area
        # default size is 5% width and 1:1
        if ('size' in settings.keys()):
            self.size = settings['size']
        else:
            self.size = (5, 5)
    
    # Returns as a nested dictionary ready to save
    def to_dict (self):
        return {
            'object': "label",
            'pos': self.pos,
            'layout_type': self.layout_type,
            'settings': self.settings
            }