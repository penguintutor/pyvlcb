# This is an abstract class - used for creating LayoutButton or LayoutLabel
# Layout Objects are anything on the layout that can display data and/or trigger events
# Typically labels or buttons, can be moved in relation to the layout


import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont
from PySide6.QtCore import Qt, QPoint, QSize

class LayoutObject:
    def __init__ (self):
        pass
    