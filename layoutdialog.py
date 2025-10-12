# Dialog for selecting existing / creating new layout
import os
import re
from pathlib import Path
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from settings import Settings
from layout import Layout
from layouts import Layouts


class LayoutDialog(QDialog):
    
    def __init__(self, parent, data_dir, layouts_dir, layouts_file, settings):
        super().__init__(parent)
        self.gui = parent
        # Data dir holds the layouts.json, whereas layouts_dir holds the actual layout
        self.data_dir = data_dir
        self.layouts_dir = layouts_dir
        self.layouts_file= layouts_file
        # settings is needed to get current, and set future
        # passed as class
        self.settings = settings
        
        self.resize(300, 220)
        
        self.setModal(True)
        loader = QUiLoader()
        basedir = os.path.dirname(__file__)
        self.ui = loader.load(os.path.join(basedir, "layoutdialog.ui"), None)
        self.setWindowTitle("Change Layout")
        self.setLayout(self.ui.layout())
        # This is where we store the selected - so that mainwindow can open it
        self.selected_layout = ""
        
        # Set the saveButton as default - it will prompt if not given a new name
        #self.ui.saveButton.setDefault(True)
        # Set message text to blank but  red
        #self.ui.messageLabel.setText("")
        #self.ui.messageLabel.setStyleSheet("color: red;")
        
        # Load the Layouts file to see what layouts are available
        layouts_file = os.path.join(self.data_dir, self.layouts_file)
        self.all_layouts = Layouts(self.data_dir, self.layouts_file)
        # else print (f"No layouts file '{layouts_file}', using default layout")
        
        # add the items to the menu
        # The title is what the user sees, but providing the filename as well allows that to be
        # retrieved from the combobox
        for filename, title in self.all_layouts.layouts.items():
            self.ui.layoutSelectBox.addItem(title, filename)
            
        # Set current layout
        if len(self.all_layouts.layouts) > 0:
            # Current layout is stored in settings
            current_layout_filename = self.settings.get_layout_filename()
            # Convert it to title for combobox
            current_layout_title = self.all_layouts.layouts[current_layout_filename]
            self.ui.layoutSelectBox.setCurrentText(current_layout_title)
        # If there were no layouts then set to the new tab
        else:
            self.switch_newtab ()
        
        # handle button clicks
        self.ui.cancelButton.clicked.connect (self.cancel)
        self.ui.layoutOpenButton.clicked.connect (self.existing)
        self.ui.newLayoutSaveButton.clicked.connect (self.save_new)
        
    def save_new (self):
        # If created a new layout save, updated selected and accept
        # Get title (check it's unique)
        new_title = self.ui.newLayoutTitleEdit.text()
        if (new_title == "" or new_title in self.all_layouts.layouts.values()):
            QMessageBox.warning(
                self, 
                "Input Error", # The title of the dialog
                "Title must be unique." # The message content
            )
            return
        # Filename is the title without spaces / special chars and lower case
        safe_filename = re.sub(r'[<>:"/\|?* (){}\[\]]', '_', new_title.lower())
        # As title is unique filename most likely is, but could be circumstance where only differ by capital or special character is stripped
        unique_filename = self.unique_filename (safe_filename+".json")
        # Create a layout (it will attempt to load but then fail)
        new_layout = Layout (self, self.layouts_dir, unique_filename)
        # Set the title which will save
        new_layout.set_title (new_title)
        # Selected layout is now filename
        self.selected_layout = unique_filename
        # Save as the new default
        self.settings.set_layout_filename(self.selected_layout)
        self.all_layouts.add_layout(self.selected_layout, new_title)
        self.accept()
        
    def existing (self):
        # Get the filename from the item data
        index = self.ui.layoutSelectBox.currentIndex()
        # set the filename to selected_layout (which mainwindow can then retrieve)
        self.selected_layout = self.ui.layoutSelectBox.itemData(index)
        # If none selected (ie. first run with no layouts then return)
        # Make the other tab active
        if self.selected_layout == "":
            self.switch_newtab()
            return
        # Also add to the setting
        self.settings.set_layout_filename(self.selected_layout)
        self.accept()
    
    # save with new name
    # first check that it's now a valid name (not already exist)
    # This is N/A - temp for info
    def save (self):
        # perform checks to see if the save should be accepted or not
        filename = self.ui.filenameEdit.text()
        if filename == "":
            self.ui.messageLabel.setText("New filename is required for save")
            return
        # also check that there are no path characters
        elif not self.is_just_filename (filename):
            self.ui.messageLabel.setText("Filename should not include path")
            return
        else:
            # Now check file doesn't exist
            new_path = os.path.join(self.locosdir, filename)
            if os.path.exists(new_path):
                self.ui.messageLabel.setText("File already exists use new filename")
                return
                
        # Reach here then passed above tests
        self.action = "save"
        self.accept()
        
    def cancel(self):
        self.reject()


    def unique_filename(self, given_filename):
        # Test using full path
        full_path = os.path.join (self.layouts_dir, given_filename)
        if not os.path.exists(full_path):
            return given_filename

        name, ext = os.path.splitext(given_filename)
        counter = 1

        # Need to have an upper limit to stop looping forever
        # although extremely unlikely we will exceed 99 with same filename
        while counter < 100:
            new_filename = f"{name}-{counter:02d}{ext}"
            full_path = os.path.join (self.layouts_dir, new_filename)
            if not os.path.exists(full_path):
                return new_filename
            counter += 1
        return None

    def switch_newtab (self):
        index_newtab = self.ui.tabWidget.indexOf(self.ui.newTab)
        if index_newtab != -1:
            self.ui.tabWidget.setCurrentIndex(index_newtab)