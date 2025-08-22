# Layout display handles the layout area of the screen - showing the layout image
# and then other buttons etc.
# This is a sbuclass of a QLabel class (which is used to house the image)

# The components that are placed on the layoutdisplay are based on guiobjects - which in turn are layoutobjects

# This is ui.layoutLabel

import sys
import json
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QPen, QBrush, QCursor
from PySide6.QtCore import Qt, QPoint, QSize
from layout import Layout
from layoutlabel import LayoutLabel
from layoutbutton import LayoutButton
from guiobject import GuiObject

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

        self.guiobjects = []
        # todo - move buttons and labels into guiobjects
        #self.buttons = []
        #self.labels = []
        
        # Mode is control or edit
        self.mode = "control"
        
        # Testing
        #self.guiobjects.append(GuiObject('point', 'Point 1', {}))
        
    def add_gui_device (self, device_type, device_name):
        self.guiobjects.append(GuiObject(self, device_type, device_name, {}))
        
    # Labels and buttons are added to guiobjects - so pass through to guiobects
    # Here pos is optional so it's moved to the end
    def add_label (self, gui_node_name, label_type, settings, pos=(5,5)):
        gui_node_id = self.gui_name_toid(gui_node_name)
        # check gui node is valid (no reason it shouldn't be)
        if gui_node_id < 0:
            print (f"Invalid gui name {gui_node_name}")
        self.guiobjects[gui_node_id].add_label (label_type, settings, pos)
        
    def add_button (self, gui_node_name, button_type, settings, pos=(5,5)):
        gui_node_id = self.gui_name_toid(gui_node_name)
        # check gui node is valid (no reason it shouldn't be)
        if gui_node_id < 0:
            print (f"Invalid gui name {gui_node_name}")
        self.guiobjects[gui_node_id].add_button (button_type, settings, pos)
        
    def gui_object_names (self):
        #print (f"GUI objects {self.guiobjects}")
        return_list = []
        for object in self.guiobjects:
            return_list.append(object.name)
        #print (f"List {return_list}")
        return return_list
    
    # From name get pos in list
    # used when adding buttons / labels etc.
    def gui_name_toid (self, gui_name):
        for i in range (0, len(self.guiobjects)):
            if self.guiobjects[i].name == gui_name:
                return i
        # Shouldn't return -1 as gui wouldn't show name that doesn't exist
        return -1
        
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
        
        for object in self.guiobjects:
            object.paint(painter)
             
        painter.end()
        self.update()


    # Save the objects (when finished editing layout)
    def save_layout_objects (self, filename):
        data_list = []
        
        for object in self.guiobjects:
            data_list.extend(object.get_save_objects())
        
        #print (f"Save list {data_list}")
            
        try:
            with open(filename, 'w') as f:
                json.dump(data_list, f, indent=4)
                #print(f"Objects successfully saved to '{filename}'")
                # Todo show this on the UI instead
        except IOError as e:
            print(f"Error saving file: {e}")
            
    def load_layout_objects (self, filename):
        try:
            with open(filename, 'r') as f:
                objects = json.load(f)
                #print (f"Objects {objects}")
        except IOError as e:
            print(f"Warning unable to loading file: {e}, possibly no assets defined")
            return
        # Create an object for each entry
        for entry in objects:
            if 'object' in entry.keys():
                if entry['object'] == 'gui':
                    self.guiobjects.append(GuiObject(self, entry['type'], entry['name'], {}))
                elif entry['object'] == 'button':
                    gui_node_id = self.gui_name_toid(entry['guiobject'])
                    self.guiobjects[gui_node_id].add_button(entry['button_type'], entry['settings'], entry['pos'])
                elif entry['object'] == 'label':
                    gui_node_id = self.gui_name_toid(entry['guiobject'])
                    self.guiobjects[gui_node_id].add_label(entry['label_type'], entry['settings'], entry['pos'])

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
        #self.buttons.append(LayoutButton(self, (25,25), "circle", button_settings))
        
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
        else:
            self.controlMousePress (event)
    
    # Mouse press whilst in control mode - if click on object then typically create an AppEvent
    def controlMousePress  (self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            mouse_pos = event.position().toPoint()
            click_pos = self.pixel_to_percent(mouse_pos)
            # Test all buttons for click, if multiple hit then use one closest
            self.selected = self.nearestToClick(click_pos)
            if self.selected == None:
                return
            #print (f"{self.selected}")
            self.selected.controlButtonClick()
            #print(f"Mouse Left Clicked at: {self.last_mouse_pos.x()}, {self.last_mouse_pos.y()}")
        elif event.button() == Qt.MouseButton.RightButton:
            #print(f"Mouse Right Clicked at: {event.position().x()}, {event.position().y()}")
            pass
    
    # Mouse press in edit mode
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
        # saves needing to test for a null value
        nearest_distance = 1000
        for guiobject in self.guiobjects:
            # result is None if no matches or (object, distance)
            result = guiobject.nearestToClick(click_pos, types)
            if result == None:
                continue
            if result[1] < nearest_distance:
                nearest_object = result[0]
                nearest_distance = result[1]
        if nearest_object == None:
            return None
        # get offset to the nearest object
        offset_percentage = nearest_object.get_offset(click_pos)
        self.click_offset = QPoint(*nearest_object.pixel_pos(offset_percentage))
        return nearest_object
                
#         nearest_object = None
#         # set distance to a value far beyond any reasonable range (1000)
#         # saves needing to test for a null value
#         nearest_distance = 1000
#         if types == "button" or types=="all":
#             for button in self.buttons:
#                 hit_test = button.is_hit(click_pos)
#                 #print (f"Button {hit_test}")
#                 # Todo determine closest (ignore any < 0)
#                 if hit_test >=0 and hit_test < nearest_distance:
#                     nearest_object = button
#                     nearest_distance = hit_test
#         if types == "label" or types=="all":
#             for label in self.labels:
#                 hit_test = label.is_hit(click_pos)
#                 #print (f"Label {hit_test}")
#                 # Todo determine closest (ignore any < 0)
#                 if hit_test >=0 and hit_test < nearest_distance:
#                     nearest_object = label
#                     nearest_distance = hit_test
#         if nearest_object != None:
#             # get offset to the nearest object
#             offset_percentage = nearest_object.get_offset(click_pos)
#             self.click_offset = QPoint(*nearest_object.pixel_pos(offset_percentage))
#         return nearest_object
    
                    
    def mouseMoveEvent(self, event: QMouseEvent):
        # Drag event
        if self.selected != None and self.mode == "edit" and event.buttons() & Qt.MouseButton.LeftButton:
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

