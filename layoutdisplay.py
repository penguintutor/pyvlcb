# Layout display handles the layout area of the screen - showing the layout image
# and then other buttons etc.
# This is a sbuclass of a QLabel class (which is used to house the image)

# This is ui.layoutLabel

import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QMouseEvent, QPixmap, QColor, QPainter, QFont, QPen, QBrush
from PySide6.QtCore import Qt, QPoint, QSize
from layout import Layout
from layoutbutton import LayoutButton

class LayoutDisplay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        # Main window is not known here (as parent is within .ui) - store when loading file
        self.mainwindow = None
        self.setMouseTracking(True)  # Enable mouse tracking even when no button is pressed
        self.last_mouse_pos = QPoint()
        self.dragging = False
        
        self.canvas = None
        
        # whenever changing canvas / pixmap size - do it through this
        # so we use same size for pixmap and status images
        self.canvas_size = QSize(200, 200)

        self.buttons = []
        self.labels = []
        
        # Mode is control or edit
        self.mode = "control"
        
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
         
        for button in self.buttons:
            button.draw(painter)
             
        painter.end()
        self.update()


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
