# LayoutLabel
# displays a text label or similar


import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont
from PySide6.QtCore import Qt, QPoint, QSize
from layoutobject import LayoutObject

# for type="text" then settings must include "text":"Text to display"
class LayoutLabel (LayoutObject):
    def __init__ (self, parent, pos, label_id, label_type, settings = {}):
        super().__init__(parent, pos, label_id)
        self.label_type = label_type
        self.settings = settings
        self.min_size = 5 # min size for click area
        # default size is 5% width and 1:1
        # just set iniitially replaced with actual size later
        if ('size' in settings.keys()):
            self.size = settings['size']
        else:
            self.size = (5, 5)
        # set font size if not in settings
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

    
    # Returns as a nested dictionary ready to save
    def to_dict (self):
        return {
            'object': "label",
            'id': self.id,
            'pos': self.pos,
            'label_type': self.label_type,
            'settings': self.settings
            }
    
    def draw (self, painter):
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
            self.size = self.parent.pixel_to_percent([text_rect.width(), text_rect.height()], rel=True)
            # Ascent is like height but doesn't include below the baseline - eg g / q etc.)
            # convert it to percent, but only interested in the y value
            #print (f"Ascent actual {font_metrics.ascent()}")
            percent_null_ascent = self.parent.pixel_to_percent([0, font_metrics.ascent()], rel=True)
            ascent = percent_null_ascent[1]
            #print (f"Pos y {self.pos[1]}, ascent {ascent}")
            # get a new y with offset (still percentage)
            draw_text_y = self.pos[1] + ascent
            # Draw using normal x pos (still left) but shifted y pos
            painter.drawText(*self.pixel_pos([self.pos[0], draw_text_y], rel=False), self.settings['text'])
            
        
    # For label need to check for width and height as typically width significantly larger than height
    # return -1 if not a hit, or distance if it is
    # note that distance is still scalar distance from center - even if more to one side (distance from center)
    # click_pos is a percentage - same as dimensions of label
    def is_hit (self, click_pos):
        #print (f"Click {click_pos}, Label {self.pos}, size {self.size}")
        # check for hit first
        if (
            click_pos[0] >= self.pos[0] and
            click_pos[0] <= self.pos[0] + self.size[0] and
            click_pos[1] >= self.pos[1] and
            click_pos[1] <= self.pos[1] + self.size[1]
            ):        
            return self.distance (click_pos)
        else:
            return -1
        

    