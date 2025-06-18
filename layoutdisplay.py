# Layout display handles the layout area of the screen - showing the layout image
# and then other buttons etc.
# This is a sbuclass of a QLabel class (which is used to house the image)

import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont
from PySide6.QtCore import Qt, QPoint, QSize
from layout import Layout
from layoutbutton import LayoutButton

class LayoutDisplay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        #print (f"Creating layout display {parent}")
        #self.mainwindow = self.window()
        # Main window is not known here (as parent is within .ui) - store when loading file
        self.mainwindow = None
        self.setMouseTracking(True)  # Enable mouse tracking even when no button is pressed
        self.last_mouse_pos = QPoint()
        self.dragging = False
        
        self.canvas = None
        
        # whenever changing canvas / pixmap size - do it through this
        # so we use same size for pixmap and status images
        self.canvas_size = QSize(200, 200)

        button_settings = {}

        self.buttons = [LayoutButton(self, (10,10), "circle", button_settings)]
        #self.buttons = []
        self.labels = []
        
        
    def draw_objects (self):
        for button in self.buttons:
            button.draw()


    def load_image (self, mainwindow):
        self.mainwindow = mainwindow
        image_file = self.mainwindow.layout.get_layout_image()
        self.canvas = QPixmap(image_file)
        # Adjust Size updates the label so that querying the size gives correct values
        #self.adjustSize()
        
        # Initial pixmap size is incorrect - instead use approximation based on window size
        w = self.mainwindow.ui.size().width() - 330
        h = self.mainwindow.ui.size().height() - 60
        self.canvas_size = QSize(w, h)
        
        #print (f"Size {self.ui.layoutLabel.size()}")
        scaled_pixmap = self.canvas.scaled(self.canvas_size, Qt.KeepAspectRatio)
        #self.ui.layoutLabel.setPixmap(scaled_pixmap)
        self.setPixmap(scaled_pixmap)
        self.adjustSize()
        #self.resizeEvent()
        #self.testObject()
        
        self.draw_objects()
        
        
    def testObject (self):
        # Optional: Draw some content on the dummy pixmap
        print (f"Test {self}, {self.canvas}")
        painter = QPainter(self.canvas)
        painter.setPen(QColor("darkred"))
        #painter.drawRect(50, 50, 700, 500)
        #painter.setFont(painter.font().setPointSize(24))
        font = QFont()
        font.setFamily('Times')
        font.setBold(True)
        font.setPointSize(40)
        painter.setFont(font)
        painter.drawText(100, 100, "Click and Drag Me!")
        painter.end()
        
    def resizeEvent(self, event=None):
        #self.canvas_size = self.ui.layoutLabel.size()
        self.canvas_size = self.size()
        scaled_pixmap = self.canvas.scaled(self.canvas_size, Qt.KeepAspectRatio)
        self.setPixmap(scaled_pixmap)
        for button in self.buttons:
            button.resize()
            button.draw()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position().toPoint()
            self.dragging = True
            #print(f"Mouse Left Clicked at: {self.last_mouse_pos.x()}, {self.last_mouse_pos.y()}")
        elif event.button() == Qt.MouseButton.RightButton:
            #print(f"Mouse Right Clicked at: {event.position().x()}, {event.position().y()}")
            pass

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.position().toPoint()
            delta_x = current_pos.x() - self.last_mouse_pos.x()
            delta_y = current_pos.y() - self.last_mouse_pos.y()
            self.last_mouse_pos = current_pos
            #print(f"Dragging: Delta X: {delta_x}, Delta Y: {delta_y} (Current: {current_pos.x()}, {current_pos.y()})")
            # Here you would typically update the image's position or a selection rectangle
            # For example, if you're implementing panning, you would move the image based on delta_x and delta_y.

        else:
            # You can also detect mouse movement without a button pressed (hovering)
            # if self.hasMouseTracking():
            #     print(f"Mouse Hovering at: {event.position().x()}, {event.position().y()}")
            pass # Or do something if you want to track mouse position without dragging

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            #print(f"Mouse Left Released at: {event.position().x()}, {event.position().y()}")

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"Mouse Left Double Clicked at: {event.position().x()}, {event.position().y()}")
