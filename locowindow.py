import sys, os
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QCheckBox, QDialog,
    QDialogButtonBox, QStyle, QComboBox, QMessageBox) 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from locoentry import LocoEntry
from locodialog import LocoDialog
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
        self.add_loco_button.clicked.connect(self.new_loco_dialog)
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
        #self.dialog = None
        # Watch if he dialog loses focus
        #self.parent.windowActivated.connect(self.raise_dialog)


    # Read in the selected filter and add the locos to the display
    def update (self):
        # First clear all existing (option may be to determine whether to keep any but keeping it simple)
        self.clear_loco_list ()
        # If this is "All" then show all locos
        selected = self.filter_selection_combo.currentText()
        if selected == "All locos":
            # for all then iterate directly from device_model
            #print (f"All locos {device_model.locos}"
            all_locos = device_model.get_all_locos()
            #print (f"All locos {all_locos}")
            for loco in all_locos:
                #print (f"Loco {loco.loco_name}")
                image_path = os.path.join(self.locos_dir, loco.get_image_filename())
                self.add_loco_entry(loco.loco_id, loco.get_display_name(), image_path, loco.filename)
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


    def add_loco_entry(self, loco_id, loco_name, loco_image_path, filename):
        loco_entry = LocoEntry(loco_id, loco_name, loco_image_path, filename, self)
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

    # new_loco_dialog - passes to open_loco_dialog
    # Called from button where first parameter is a bool - which is ignored
    def new_loco_dialog(self):
        self.open_loco_dialog()

    # If data supplied then this is edit instead of new
    # If filename provided then save as that. If no filename supplied but data is then this could be a copy
    def open_loco_dialog(self, data=None, filename=None):
        #print("Add new loco")
        loco_dialog = LocoDialog(self, self.locos_dir)
        if data != None:
            loco_dialog.from_dict(data)
        result = loco_dialog.exec()
        if result != 1:
            return
        
        data_dict = loco_dialog.to_dict()
        

        # If filename is none then this is a new entry so create file and add to the device_model / locos.json etc.
        if filename == None:
            # Create a filename loco_id followed by class_id and name or classification
            filename = str(loco_dialog.loco_id)
            if data_dict['class'] != "":
                filename += "-" + data_dict['class']
            if data_dict['name'] != "" :
                filename += "-" + data_dict['name']
            elif data_dict['classification'] != "":
                filename += "-" + data_dict['classification']
            # remove any non file save characters
            safe_filename = re.sub(r'[<>:"/\|?* ]', '_', filename.lower())
            safe_filename += ".json"
            
            # check filename unique
            unique_filename = self.unique_loco_filename (safe_filename)
            
            # Create the loco entry
            loco = device_model.add_loco(unique_filename, loco_dialog.loco_id)
            loco.update_loco(data_dict)
            result = loco.save_file()
            # save locos file afterwards in case of problem creating
            if result == True:
                device_model.save_locos()
            # Otherwise cleanup (but no need to remove any files)
            else:
                print (f"Error tying to save file {safe_filename}")
                device_model.remove_loco(safe_filename, delete=False)
        # If existing filename then just update exising file
        else:
            #Todo implement save existing
            # get the current loco object (from filename)
            loco = device_model.get_loco_from_filename(filename)
            # If don't get loco then error (has file been deleted during edit)
            if loco == None:
                print ("Error trying to retrieve / update loco {filename}")
            else:
                loco.update_loco(data_dict)
                result = loco.save_file()
                if result != True:
                    print ("Error trying to save loco changes {filename}")
        
        # Update the display to show the new loco
        self.update()
        
    # make sure that the filename is unique - if not then add a numeric suffix
    def unique_loco_filename(self, given_filename):
        # Test using full path
        full_path = os.path.join (self.locos_dir, given_filename)
        if not os.path.exists(full_path):
            return given_filename

        name, ext = os.path.splitext(given_filename)
        counter = 1

        # Need to have an upper limit to stop looping forever
        # although extremely unlikely we will exceed 99 with same filename
        while counter < 100:
            new_filename = f"{name}-{counter:02d}{ext}"
            full_path = os.path.join (self.locos_dir, new_filename)
            if not os.path.exists(full_path):
                return new_filename
            counter += 1
        return None

        
    # Launch loco edit dialog
    def loco_edit (self, clicked_entry: LocoEntry):
        # Filename within LocoEntry is full path
        filename = os.path.basename(clicked_entry.filename)
        # Use filename as a unique entry to lookup loco
        clicked_loco = device_model.get_loco_from_filename (filename)

        # Assuming valid then launch edit dialog
        if clicked_loco != None:
            self.open_loco_dialog (clicked_loco.to_dict(), filename)