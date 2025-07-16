# Layout display handles the layout area of the screen - showing the layout image
# and then other buttons etc.
# This is a sbuclass of a QLabel class (which is used to house the image)

# This is ui.layoutLabel

import sys
import json
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QPen, QBrush, QCursor
from PySide6.QtCore import Qt, QPoint, QSize
from layout import Layout
from layoutlabel import LayoutLabel
from layoutbutton import LayoutButton

class LayoutDisplay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        # Main window is not known here (as parent is within .ui) - store when loading file
        self.mainwindow = None
        self.setMouseTracking(True)  # Enable mouse tracking even when no button is pressed
        #self.last_mouse_pos = QPoint()
        
        # Is an object selected (for dragging etc.)
        self.selected = None

        self.canvas = None

        self.cursor = QCursor()

        # whenever changing canvas / pixmap size - do it through this
        # so we use same size for pixmap and status images
        self.canvas_size = QSize(200, 200)

        self.buttons = []
        self.labels = []
        
        # Mode is control or edit
        self.mode = "control"
        
    # Here pos is optional so it's moved to the end
    def add_label (self, label_id, label_type, settings, pos=(5,5)):
        self.labels.append (LayoutLabel(self, pos, label_id, label_type, settings))
        
    def paintEvent (self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        #Set global rendering hints for smoother drawing
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(QColor("darkblue"))
        brush = QBrush()
        brush.setColor(QColor('darkblue'))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        
        for label in self.labels:
            label.draw(painter)
        
        for button in self.buttons:
            button.draw(painter)
             
        painter.end()
        self.update()


    # Save the objects (when finished editing layout)
    def save_layout_objects (self, filename):
        data_list = []
        # Gather all objects into a data_list
        for button in self.buttons:
            data_list.append(button.to_dict())
        for label in self.labels:
            data_list.append(label.to_dict())
            
        try:
            with open(filename, 'w') as f:
                json.dump(data_list, f, indent=4)
                #print(f"Objects successfully saved to '{filename}'")
                # Todo show this on the UI instead
        except IOError as e:
            print(f"Error saving file: {e}")
        

    def load_image (self, mainwindow):
        self.mainwindow = mainwindow
        image_file = self.mainwindow.railway.get_layout_image()
        self.canvas = QPixmap(image_file)
        
        # Initial pixmap size is incorrect - instead use approximation based on window size
        w = self.mainwindow.ui.size().width() - 330
        h = self.mainwindow.ui.size().height() - 60
        self.canvas_size = QSize(w, h)
        
        scaled_pixmap = self.canvas.scaled(self.canvas_size, Qt.KeepAspectRatio)
        self.setPixmap(scaled_pixmap)
        
        #print (f"Canvas {self.canvas_size}, Pixmap {self.pixmap().size()}")
        
        # Adjust Size updates the label so that querying the size gives correct values
        self.adjustSize()
        button_settings = {
            'size': (2,2),
            'color_on': '#00FF00', 'color_off': '#FF0000', 'color_unknown': '#555555'
            }
        self.buttons.append(LayoutButton(self, (25,25), "circle", button_settings))

        
        
#     def testObject (self):
#         # Optional: Draw some content on the dummy pixmap
#         print (f"Test {self}, {self.canvas}")
#         painter = QPainter(self.canvas)
#         painter.setPen(QColor("darkred"))
#         #painter.drawRect(50, 50, 700, 500)
#         #painter.setFont(painter.font().setPointSize(24))
#         font = QFont()
#         font.setFamily('Times')
#         font.setBold(True)
#         font.setPointSize(40)
#         painter.setFont(font)
#         painter.drawText(100, 100, "Click and Drag Me!")
#         painter.end()
        
    def resizeEvent(self, event=None):
        #self.canvas_size = self.ui.layoutLabel.size()
        self.canvas_size = self.size()
        scaled_pixmap = self.canvas.scaled(self.canvas_size, Qt.KeepAspectRatio)
        self.setPixmap(scaled_pixmap)
        # other objects are drawn through a paintEvent which is called
        # whenever the Pixmap is replaced


    def mousePressEvent(self, event: QMouseEvent):
        if self.mode == "edit":
            self.editMousePress (event)
        
    def editMousePress  (self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            mouse_pos = event.position().toPoint()
            click_pos = self.pixel_to_percent(mouse_pos)
            # Test all buttons for click, if multiple hit then use one closest
            self.selected = self.nearestToClick(click_pos)
            if self.selected == None:
                return
            #print (f"{self.selected}")
            #print(f"Mouse Left Clicked at: {self.last_mouse_pos.x()}, {self.last_mouse_pos.y()}")
        elif event.button() == Qt.MouseButton.RightButton:
            #print(f"Mouse Right Clicked at: {event.position().x()}, {event.position().y()}")
            pass
        
    # Find nearest object to click that is touched
    # separates two nearby objects
    # types can be "buttons", "labels" or "all"
    #click_pos is percentage
    def nearestToClick(self, click_pos, types="all"):
        nearest_object = None
        # set distance to a value far beyond any reasonable range (1000)
        nearest_distance = 1000
        if types == "button" or types=="all":
            for button in self.buttons:
                hit_test = button.is_hit(click_pos)
                #print (f"Button {hit_test}")
                # Todo determine closest (ignore any < 0)
                if hit_test >=0 and hit_test < nearest_distance:
                    nearest_object = button
                    nearest_distance = hit_test
        if types == "label" or types=="all":
            for label in self.labels:
                hit_test = label.is_hit(click_pos)
                #print (f"Label {hit_test}")
                # Todo determine closest (ignore any < 0)
                if hit_test >=0 and hit_test < nearest_distance:
                    nearest_object = label
                    nearest_distance = hit_test
        if nearest_object != None:
            # get offset to the nearest object
            offset_percentage = nearest_object.get_offset(click_pos)
            self.click_offset = QPoint(*nearest_object.pixel_pos(offset_percentage))
        return nearest_object
                    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.selected != None and event.buttons() & Qt.MouseButton.LeftButton:
            # Set move cursor
            self.cursor.setShape(Qt.DragMoveCursor)
            self.setCursor(self.cursor)
            current_pos = event.position().toPoint()
#            self.last_mouse_pos = self.last_mouse_pos + self.click_offset
            new_pos = self.pixel_to_percent(current_pos - self.click_offset)
            # if out of bounds then cancel the drag
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] + self.selected.size[0] >= 100 or new_pos[1] + self.selected.size[1] >= 100:
                # leave selected but don't move it until the cursor goes back into the area
                pass
            # otherwise update the object pos
            else:
                self.selected.pos = new_pos
        else:
            # You can also detect mouse movement without a button pressed (hovering)
            # if self.hasMouseTracking():
            #     print(f"Mouse Hovering at: {event.position().x()}, {event.position().y()}")
            pass # Or do something if you want to track mouse position without dragging

    def mouseReleaseEvent(self, event: QMouseEvent):
        # Set unselected (doesn't matter which mode we are in)
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected = None
            self.cursor.setShape(Qt.ArrowCursor)
            self.setCursor(self.cursor)
            #print(f"Mouse Left Released at: {event.position().x()}, {event.position().y()}")

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        pass
        #if event.button() == Qt.MouseButton.LeftButton:
        #    print(f"Mouse Left Double Clicked at: {event.position().x()}, {event.position().y()}")


    # Convert pixels to percentage
    # by default (rel=False) then calculates based on absolute position
    # factoring in the difference betwen label and image size
    # If rel=True then ignore that and calculate relative value
    def pixel_to_percent (self, position, rel=False):
        label_size = self.canvas_size
        image_size = self.pixmap().size()
        # allow position to be a a list/tuple or a QObject type
        if isinstance(position, (list, tuple)):
            x_val = position[0]
            y_val = position[1]
        else:
            x_val = position.x()
            y_val = position.y()
        
        # subtract height1/2 height difference if not relative 
        if rel==False:
            height_diff = label_size.height() - image_size.height()
            if height_diff > 0:
                y_val -= int(height_diff/2)
        # now have actual pos within the image pixmap (if not relative)
        # calculate as a percentage of image_size
        x_percent = (x_val / image_size.width()) * 100
        y_percent = (y_val / image_size.height()) * 100
        return [x_percent, y_percent]

