import sys, os
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle, QComboBox, QMessageBox) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from locoentry import LocoEntry
from addlocodialog import AddLocoDialog
from devicemodel import device_model 

# parent is required (although could be set to None it should normally be mainwindow)
# directory of filters and locos is required - but the filters and locos are loaded from device_model
class LocoWindow(QMainWindow):
    def __init__(self, parent, locos_dir):
        super().__init__(parent)
        self.parent = parent
        self.locos_dir = locos_dir

        self.setWindowTitle("Loco Manager")
        self.setFixedSize(750, 400)
        
        # List containing filenames holding the loco info
        # and whether it is enabled or not (filename, enabled
        self.loco_files = []

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft)

        header_label = QLabel("Manage Locos")
        header_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(header_label)

        # Spacer to push add button to the right
        header_layout.addStretch(1)
        
        # filter selection button
        self.filter_label = QLabel("Filter: ")
        header_layout.addWidget(self.filter_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        self.filter_selection_combo = QComboBox()
        self.filter_selection_combo.setMinimumWidth(100)
        self.filter_selection_combo.addItem("All locos")
        # Add filter options from settings?
        #self.filter_selection_combo.addItems(device_model.get_filter_list())
        header_layout.addWidget(self.filter_selection_combo, alignment=Qt.AlignTop | Qt.AlignLeft)
        # If selection combo changes (different filter) then call update to change the list
        self.filter_selection_combo.currentIndexChanged.connect(self.update)
        
        header_layout.addSpacing (60)

        # Add filter button (top right)
#         self.add_filter_button = QPushButton("Add filter")
#         self.add_filter_button.clicked.connect(self.open_add_filter_dialog)
#         header_layout.addWidget(self.add_filter_button, alignment=Qt.AlignTop | Qt.AlignRight)

        # Add Loco button (top right)
        self.add_loco_button = QPushButton("Add Loco")
        self.add_loco_button.clicked.connect(self.open_add_loco_dialog)
        header_layout.addWidget(self.add_loco_button, alignment=Qt.AlignTop | Qt.AlignRight)

        main_layout.addLayout(header_layout)

        # Scrollable area for loco rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.loco_list_widget = QWidget()
        self.loco_list_layout = QVBoxLayout(self.loco_list_widget)
        self.loco_list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.loco_list_widget)
        main_layout.addWidget(self.scroll_area)

        # Bottom bar with OK button
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.addStretch(1)
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(80, 30)
        self.ok_button.clicked.connect(self.close)
        bottom_bar_layout.addWidget(self.ok_button)

        main_layout.addLayout(bottom_bar_layout)
        
        # references to dialogs (so we can keep them on top)
        self.dialog = None
        # Watch if he dialog loses focus
        #self.parent.windowActivated.connect(self.raise_dialog)

#         # Examples
#         self.add_loco_entry("0001", "A3 Class", "Flying Scotsman", "loco_image.png")
#         self.add_loco_entry(2, "A4 Class", "Mallard", "loco_image.png")
#         self.add_loco_entry(3, "Coronation Class", "Duchess of Sutherland", "loco_image.png")
#         self.add_loco_entry(4, "A3 Class", "Flying Scotsman", "loco_image.png")
        # Update adds the entries to the display - already called from mw when window opened
        #self.update()

    # Read in the selected filter and add the locos to the display
    def update (self):
        # First clear all existing (option may be to determine whether to keep any but keeping it simple)
        self.clear_loco_list ()
        # If this is "All" then show all locos
        selected = self.filter_selection_combo.currentText()
        if selected == "All locos":
            # for all then iterate directly from device_model
            #print (f"All locos {device_model.locos}"
            for loco in device_model.get_all_locos():
                #print (f"Loco {loco.loco_name}")
                image_path = os.path.join(self.locos_dir, loco.get_image_filename())
                self.add_loco_entry(loco.loco_id, loco.loco_class, loco.loco_name, image_path)
        else:
            # load the current filter selection
            print (f"Selected {selected}")
            
    def clear_loco_list (self):
        layout = self.loco_list_layout
        while layout.count():
            # remove from layout
            item = layout.takeAt(0)
            
            #  Set to delete
            if item.widget() is not None:
                widget = item.widget()
                widget.hide()
                widget.deleteLater()
    
    def display (self):
        self.show()
    
    # Gets summary from file
    def load_file (self, filename):
        with open(filename, 'r') as data_file:
            loco_data = json.load(data_file)
        loco_id = self.loco_data["address"]
        loco_name = self.loco_data["display-name"]


    def add_loco_entry(self, loco_id, loco_class, loco_name, loco_image_path):
        loco_entry = LocoEntry(loco_id, loco_class, loco_name, loco_image_path)
        # Add listener to the connect
        loco_entry.clicked.connect(self.loco_edit)
        self.loco_list_layout.addWidget(loco_entry)
    
    # Converts a string of text into a valid filename.
    # Replaces spaces with underscores and removes or replaces characters
    # that are not allowed in most common file systems.
    def title_to_filename(self, text):
        # Replace spaces with underscores
        filename = text.replace(' ', '_')

        # Remove characters that are generally not allowed in filenames.
        # The regex pattern [^\w\s\-] matches any character that is NOT a word
        # character (alphanumeric and underscore), whitespace, or a hyphen.
        # The underscore replacement in the first step is why we want to keep
        # the underscore in the valid characters here.
        filename = re.sub(r'[^\w\.\-]', '', filename)
        filename = filename.lower() + ".json"
        return filename

    def open_add_loco_dialog(self):
        #print("Add new loco")
        add_dialog = AddLocoDialog(self, self.locos_dir)
        add_dialog.exec()
        
        # Create a dict of the values
        data_dict = {
            'displayname': add_dialog.ui.displayTextEdit.text(),
            'class': add_dialog.ui.classEdit.text(),
            'classname': add_dialog.ui.classNameEdit.text(),
            'name': add_dialog.ui.nameEdit.text(),
            'number': add_dialog.ui.numberEdit.text(),
            'locotype': add_dialog.ui.locoTypeCombo.currentText(),
            'origrailway': add_dialog.ui.origRailwayEdit.text(),
            'liveryrailway': add_dialog.ui.liveryRailwayEdit.text(),
            'originalyear': add_dialog.ui.originalYearEdit.text(),
            'liveryyear': add_dialog.ui.liveryYearEdit.text(),
            'wheels': add_dialog.ui.wheelsEdit.text(),
            'modelManuf': add_dialog.ui.modelManufEdit.text(),
            'decoder': add_dialog.ui.decoderEdit.text(),
            'image': add_dialog.image_filename,
            'summary': add_dialog.ui.summaryText.toPlainText()
            }
        
        # Create a filename loco_id followed by class_id and name or class_name
        filename = str(add_dialog.loco_id)
        if data_dict['name'] != "" :
            filename += "-" + data_dict['name']
        elif data_dict['classname'] != "":
            filename += "-" + data_dict['classname']
        # remove any non file save characters
        safe_filename = re.sub(r'[<>:"/\|?*]', '_', filename.lower())
        safe_filename += ".json"
            
        # Create the loco entry
        loco = device_model.add_loco(safe_filename, add_dialog.loco_id)
        loco.update_loco(data_dict)
        loco.save()
        
    # Launch loco edit dialog
    def loco_edit (self, clicked_entry: LocoEntry):
        # Todo implement this
        print (f"Loco edit triggered {clicked_entry.loco_id}")
        