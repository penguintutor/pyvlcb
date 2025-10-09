import os
import shutil
from PySide6.QtCore import QTimer, QCoreApplication, Signal, QThreadPool, Qt, QPoint, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QMenu, QLineEdit, QDialog, QColorDialog, QFileDialog
from PySide6.QtGui import QPixmap, QImage, QPalette, QColor, QFont, QResizeEvent
from PySide6.QtUiTools import QUiLoader
from consolewindow import ConsoleWindowUI
from layout import Layout
from layoutdisplay import LayoutDisplay
from stealdialog import StealDialog
from controlloco import ControlLoco
from apihandler import ApiHandler
from eventbus import event_bus
from appevent import AppEvent
from devicemodel import device_model
from locowindow import LocoWindow
from eventwindow import EventWindow
from adddevicedialog import AddDeviceDialog
from addlabeldialog import AddLabelDialog
from addbuttondialog import AddButtonDialog
from vlcbnode import VLCBNode
from vlcbev import VLCBEv
from guiobject import GuiObject
from layoutobject import LayoutObject
from layoutbutton import LayoutButton
from layoutlabel import LayoutLabel

# Layout Display is from the loader to interact use
# self.ui.layoutDisplayLabel

loader = QUiLoader()
loader.registerCustomWidget(LayoutDisplay)

# Setup file paths
basedir = os.path.dirname(__file__)

#pc_can_id = 60      # CAN ID of CANUSB4

app_title = "VLCB App"

url = "http://127.0.0.1:5000/"

read_rate = 200

class MainWindowUI(QMainWindow):
    
    
    steal_dialog_signal = Signal(int)
    # Handle loco selection
    # reset loco to none selected (if aquire failed or loco stolen by another controller)
    reset_loco_signal = Signal()
    steal_loco_signal = Signal() # Attempt to steal loco
    share_loco_signal = Signal() # Attempt to share loco
    
    # Keep alive timer must always be started and stopped on the GUI thread
    # this will start or stop as appropriate based on loco state
    update_kalive_signal = Signal()
    
    # If locos updated then refresh selection list
    updated_locos_signal = Signal()
    
    # Monitor for Window Activated to be able to manage the level of windows / dialog
    windowActivated = Signal()
    
    # files_dirs are passed from app - file structure is fixed
    # Are all relative to basedir
    # although some customisation of file names is allowed in configs
    # settings provides an option for command line arguments (not yet supported)
    def __init__(self, dirs, files, settings={}):
        super().__init__()
        self.debug = False
        
        # Command line arguments and directory settings
        self.cmd_settings = settings
        self.dirs = {} # dirs need to be updated with data_dir
        self.files = files
        
        # This will hold the QPixmap for the loco image
        self.loco_image = None
        
        # All data files are relative to this directory
        # Default this is basedir/data
        # Can be overridden by command line arguments
        if 'data_dir' in self.cmd_settings:
            # Already checked this is a directory
            self.data_dir = self.cmd_settings['data_dir']
        else:
            self.data_dir = os.path.join(basedir, "data/")
            
        # Update all the dirs to add data_dir
        for key, value in dirs.items():
            self.dirs[key] = os.path.join(self.data_dir, value)
        
        self.threadpool = QThreadPool()
        self.update_in_progress = False
        
        self.api = ApiHandler(self.threadpool, url)
        
        # Get the QFont object for the default font
        app = QApplication.instance()
        self.default_font = app.font()
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(read_rate)
        self.timer.timeout.connect(self.api.poll_server)
        self.timer.start()
        
        # Keep alive timer - used for DCC keep alive
        # Create timer, but don't start until aquire locomotive
        self.kalive_timer = QTimer(self)
        self.kalive_timer.setInterval(4000)
        self.kalive_timer.timeout.connect(self.keep_alive)
        
        # Load the Assets prior to setting up the GUI
        
        # Load the settings file here
        # Todo - adding settings - implement this class
        # Settings(os.path.join(basedir, "self.files["settings"]", self.cmd_settings)
        # else print ("No settings file, using defaults")
        
        # Load the Layouts file to see what layouts are available
        # Todo - add support for multiple layouts - implement this class
        # layouts_file = os.path.join(basedir, self.files["layouts"])
        # Layouts(layouts_file)
        # else print (f"No layouts file '{layouts_file}', using default layout")
        
        layout_name = "Default"
        layout_filename = "default.json"
        layouts_dir = os.path.join(self.data_dir, self.dirs['layouts'])
    
        # Layout provides background image and
        # is useful for giving real names to certain items
        # Variable is named railway to avoid potential conflict if named layout
        self.railway = Layout(layout_name, layouts_dir, layout_filename)
        # pass the layout to the devicemodel
        device_model.set_layout(self.railway)
        
        # active locos are the ones active for this session
        full_path_locos = os.path.join(self.data_dir, self.files['locos'])
        device_model.load_locos (self.dirs['locos'], full_path_locos)

        
        self.ui = loader.load(os.path.join(basedir, "mainwindow.ui"), None)
        self.setWindowTitle(app_title)
        self.loco_window = None
        self.event_window = None
        
        # Signals
        self.steal_dialog_signal.connect (self.steal_loco_dialog)
        self.reset_loco_signal.connect (self.reset_loco)
        self.steal_loco_signal.connect (self.steal_loco)
        self.share_loco_signal.connect (self.share_loco)
        self.update_kalive_signal.connect (self.update_kalive)
        # Other event related signals
        self.updated_locos_signal.connect (self.update_loco_list)
        # Gui signal
        event_bus.gui_event_signal.connect(self.gui_event)
        # Listen to device_model signal for treeview updates
        device_model.add_node_signal.connect (self.add_to_tree)
        
        # File Menu
        # (Import sub menu)
        self.ui.actionImportLoco.triggered.connect(self.import_file)
        self.ui.actionExit.triggered.connect(self.quit_app)
        
        # Asset Menu
        self.ui.actionDiscover.triggered.connect(self.api.discover)
        
        # Tools Menu        
        self.ui.actionLocoManager.triggered.connect(self.loco_manager)
        self.ui.actionEvents.triggered.connect(self.events_edit)
        self.ui.actionShowConsole.triggered.connect(self.show_console)
        self.ui.actionLayoutEdit.triggered.connect(self.layout_edit)
        self.ui.actionSettings.triggered.connect(self.settings)
        
        # EditLayout Menu - only show when in edit layout mode
        #self.ui.menuEditLayout.setVisible(False)
        self.ui.menuEditLayoutAction = self.ui.menuEditLayout.menuAction()
        self.ui.menuEditLayoutAction.setVisible(False)
        self.ui.actionAddDevice.triggered.connect(self.add_device_dialog)
        self.ui.actionAddLabel.triggered.connect(self.add_label_dialog)
        self.ui.actionAddButton.triggered.connect(self.add_button_dialog)
        
        # Tree view
        #self.node_model = device_model.node_model
        #self.node_model.setHorizontalHeaderLabels(['Nodes'])
        self.ui.nodeTreeView.setModel(device_model.node_model)
        self.ui.nodeTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Left click
        self.ui.nodeTreeView.clicked.connect(self.tree_clicked)
        # Right click - instead needs to use custom context policy
        self.ui.nodeTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.nodeTreeView.customContextMenuRequested.connect(self.tree_clicked_right)
        
        
        # Event buttons
        self.ui.evButtonOff.clicked.connect(self.ev_clicked_off)
        self.ui.evButtonOn.clicked.connect(self.ev_clicked_on)
        
        # Last Node / Event that was selected - use for On/Off buttons
        self.selected_node = None
        
        # Update other GUI components
        # Add locos to menu
        self.update_loco_list ()
        # Activated is based on user interaction (changing by code doesn't trigger)
        self.ui.locoComboBox.activated.connect(self.loco_change)
        self.ui.locoDial.valueChanged.connect(self.loco_change_speed)
        
        # With direction radio buttons just look for clicks (so can update without triggering)
        self.ui.locoForwardRadio.clicked.connect(self.loco_forward)
        self.ui.locoReverseRadio.clicked.connect(self.loco_reverse)
        self.ui.locoForwardButton.clicked.connect(self.loco_forward)
        self.ui.locoReverseButton.clicked.connect(self.loco_reverse)
        
        self.ui.locoStopButton.clicked.connect(self.loco_stop)
        self.ui.locoStopAllButton.clicked.connect(self.loco_stop_all)
        
        self.ui.locoFuncTab.tabBarClicked.connect(self.loco_change_functions)
        self.ui.locoFuncCombo.activated.connect(self.loco_function_selected)
        self.ui.locoFuncButton.clicked.connect(self.loco_function_pressed)
        
        # Used to generate codes for loco etc.
        self.control_loco = ControlLoco()
        event_bus.app_event_signal.connect(self.app_event)
        #event_bus.gui_event_signal.connect(self.gui_event)
        # automation_file
        # Todo
        # Need to determine which rules to load - this is default
        
        event_bus.load_rules(os.path.join(self.dirs['rules'], "default.json"))
        
        # Load layout background image
        self.ui.layoutDisplayLabel.load_image(self)
        # and UI objects
        self.ui.layoutDisplayLabel.load_layout_objects(self.railway.get_layout_objs_file())
        # Load close icon image (switch back to control mode)
        #close_image_file = os.path.join(basedir, "close-icon.png")
        #self.close_image = QImage (close_image_file)
        
        # Update LCD - used to set '-' at start
        self.update_lcd()
        
        self.setCentralWidget(self.ui)
        self.ui.nodeTreeView.show()
        self.show()
        self.create_console()
        
        # Status of the http connection
        self.status = "Not connected"
                          
        # Initial discover request
        self.api.discover()
        
    
    def gui_event (self, gui_event):
        #print ("Gui event receieved {gui_event}")
        gui_node = device_model.get_guiobject_name(gui_event.data['name'])
        if gui_node != None:
            gui_node.set_value(gui_event.data['value'])
        self.update_table()

    # Edit events associations between different objects
    def loco_manager (self):
        if self.loco_window == None:
            self.loco_window = LocoWindow(self, self.dirs['locos'])
        self.loco_window.update()
        self.loco_window.display()

    # Edit events associations between different objects
    def events_edit (self):
        if self.event_window == None:
            self.event_window = EventWindow(self)
        self.event_window.update()
        self.event_window.display()
    
    # Edit settings
    def settings (self):
        pass
    
    def add_device_dialog (self):
        dialog = AddDeviceDialog()
        if dialog.exec():
            # response = id, text
            response = dialog.get_selected_values()
            # The first "text" is that it's a text style label (allows flexibility for future)
            self.ui.layoutDisplayLabel.add_gui_device(response[0], response[1])
        
    def add_label_dialog (self):
        dialog = AddLabelDialog(self.ui.layoutDisplayLabel.gui_object_names())
        if dialog.exec():
            # response = id, text
            response = dialog.get_selected_values()
            #print(f"Selected value: {text}")
            # The first "text" is that it's a text style label (allows flexibility for future)
            self.ui.layoutDisplayLabel.add_label(response[0], "text", {"text":response[1]})
        
    def add_button_dialog (self):
        #print (f"Label {self.ui.layoutDisplayLabel}")
        #print (f"Obj names {self.ui.layoutDisplayLabel.gui_object_names()}")
        dialog = AddButtonDialog(self.ui.layoutDisplayLabel.gui_object_names())
        if dialog.exec():
            # response = id, button_type
            response = dialog.get_selected_values()
            self.ui.layoutDisplayLabel.add_button(response[0], response[1], {})
        
    def event_selection_dialog (self):
        dialog = EventDialog()
        if dialog.exec():
            node, event = dialog.get_selected_values()
            print(f"Selected Node: {node}")
            print(f"Selected Event: {event}")
        #else:
        #    print("Dialog cancelled.")

        
    # App event is used to send events from other parts of the app
    def app_event (self, app_event):
        # If there is a loco_index then only interested in loco 0 (gui controlled loco)
        # If no loco_index then assume it's for us
        # Otherwise event is most likely for automation
        if 'loco_index' in app_event.data and app_event.data['loco_index'] != 0:
            return
        if app_event.event_type == "uitext":
            if app_event.data['label'] == "locoStatusLabel":
                self.ui.locoStatusLabel.setText (app_event.data['value'])
        elif app_event.event_type == "lcd":
            self.update_lcd()
        elif app_event.event_type == "keepalive":
            self.update_kalive_signal.emit()
        # If locotaken then launch steal_dialog
        elif app_event.event_type == "locotaken":
            # Set status message - then launch dialog
            self.ui.locoStatusLabel.setText ('Error - address taken')
            self.steal_dialog_signal.emit(app_event.data['loco_id'])
        elif app_event.event_type == "resetloco":
            # Only reset gui parts - already reset in controlloco
            self.reset_loco_gui()
            
    # Toggles between layout edit and control mode
    # or provide mode to switch to that mode (control / edit)
    def layout_edit (self, mode="toggle"):
        #print (f"Changing {mode} - {self.ui.layoutDisplayLabel.mode}")
        # if set is not valid then defaults to control (not expected)
        # If called from menu then mode will be False
        if mode == "toggle" or mode == False:
            if self.ui.layoutDisplayLabel.mode == "control":
                self.ui.layoutDisplayLabel.mode = "edit"
            else:
                self.ui.layoutDisplayLabel.mode = "control"
        elif mode == "edit":
            self.ui.layoutDisplayLabel.mode = "edit"
        else:
            self.ui.layoutDisplayLabel.mode = "control"
        # Change layoutdisplay mode
        if self.ui.layoutDisplayLabel.mode == "edit":
            self.ui.actionLayoutEdit.setText("Layout Control")
            #self.ui.menuEditLayout.setVisible(True)
            self.ui.menuEditLayoutAction.setVisible(True)
        else:
            self.ui.actionLayoutEdit.setText("Layout Edit")
            #self.ui.menuEditLayout.setVisible(False)
            self.ui.menuEditLayoutAction.setVisible(False)
            # When switching back to control from edit then save config
            self.ui.layoutDisplayLabel.save_layout_objects(layout_objs_file)
    
    # Show console always calls show
    # If window already open then bring to front
    def show_console (self):
        # Send as an app event to decouple
        event_bus.publish(AppEvent("showconsole"))
        
    
    def steal_loco (self):
        self.api.start_request(self.api.vlcb.steal_loco(self.control_loco.get_id()))
        response = self.control_loco.steal_loco ()
        self.ui.locoStatusLabel.setText(response)
    
    def share_loco (self):
        self.api.start_request(self.api.vlcb.share_loco(self.control_loco.get_id()))
        response = self.control_loco.share_loco ()
        self.ui.locoStatusLabel.setText(response)
        
    # Reset loco selection in GUI and remove references
    def reset_loco (self):
        self.control_loco.reset_loco ()
        self.reset_loco_gui()
        
    # Extract GUI from reset_loco - so can be used from an app event
    def reset_loco_gui (self):
        self.update_kalive()
        # Change combo after reset - that way the post change
        # will not send a release message
        self.ui.locoComboBox.setCurrentIndex(0)
        self.ui.locoStatusLabel.setText("None active")
        
    # When loco change requested through combobox
    def loco_change (self, index):
        # Release old loco
        session = self.control_loco.get_session()
        # If not session then nothing to release
        if session != None:
            self.api.start_request(self.api.vlcb.release_loco(session))
            self.control_loco.release()

        # Check for a valid loco chosen (ie if gone back to 0 then return)
        if index == 0:
            if self.kalive_timer.isActive():
                self.kalive_timer.stop()
            return
        
        # Get the loco entry
        loco_name = self.ui.locoComboBox.currentText()
        
        # Get the loco entry
        loco = device_model.get_loco_from_name (loco_name)
            
        # If don't get a loco then close
        if loco == None:
            print ("No loco found with name {loco_name}")
            return
        
        
        self.control_loco.loco = loco
        
        self.ui.locoStatusLabel.setText(f"Aquiring {loco_name}")
        self.control_loco.loco.status = 'rloc'
        # Add images and summary
        if "image" in self.control_loco.loco.loco_data and self.control_loco.loco.loco_data['image'] != "":
            self.loco_image = QPixmap(os.path.join(self.dirs['locos'], self.control_loco.loco.loco_data['image']))
        else:
            self.loco_image = QPixmap(os.path.join(self.dirs['locos'], "default.png"))
        self.ui.locoImage.setPixmap(self.loco_image)
        # Scale the image to fit (include minimum size when first loading)
        self._scale_image_to_fit(QSize(280, 180))
        if "summary" in self.control_loco.loco.loco_data:
            self.ui.locoInfoText.setText(self.control_loco.loco.loco_data['summary'])
        else:
            self.ui.locoInfoText.setText("")
        
        self.api.start_request(self.api.vlcb.allocate_loco(self.control_loco.get_id()))
        self.control_loco.set_status('rloc')
        
        # Update the functions menu
        self.loco_change_functions(0)
        self.control_loco.function_reset()
                
    # Update function selected features
    # When combobox / tab selected
    def loco_function_selected (self):
        # get current index, need both tab and position in tab
        tab = self.ui.locoFuncTab.currentIndex()
        combo = self.ui.locoFuncCombo.currentIndex()
        #print (f"Tab {tab}, Combo {combo}")
        func_index = combo + (10 * tab)
        status_text = self.control_loco.function_selected(func_index)
        self.ui.locoFuncButton.setText (status_text)
        
    # Button has been pressed
    def loco_function_pressed (self):
        # Check that button is valid (ie. not "-")
        button_text = self.ui.locoFuncButton.text()
        if button_text == "" or button_text == "-" or button_text == " - ":
            return
        # get current index, need both tab and position in tab
        tab = self.ui.locoFuncTab.currentIndex()
        combo = self.ui.locoFuncCombo.currentIndex()
        #print (f"Tab {tab}, Combo {combo}")
        func_index = combo + (10 * tab)
        #self.control_loco.function_pressed(func_index)
        status = self.control_loco.get_function_status(func_index)
        # If no status then ignore
        if status == None:
            return
        # If trigger then button should be activate:
        if status[1] == "trigger":
            self.loco_func_trigger (func_index)
            # no need to update button as still says activate
        else:
            # if <= F12 then send multiple times (NRMA standard)
            if func_index <= 12:
                #print (f"Func {func_index}, current {status[0]}, new {1-status[0]}")
                #self.func_change (func_index, 1-status[0], 3)
                self.loco_func_change (func_index, 1-status[0], 3)
            # otherwise send once
            else:
                #self.func_change (func_index, 1-status[0])
                self.loco_func_change (func_index, 1-status[0])
            # Update button
            # perhaps separate functions to what is required
            self.loco_function_selected()
            

    # change value (if need to send multiple then set num_send to number of times
    # Sent every 2 seconds (or change delay) - delay in seconds
    def loco_func_change (self, func_index, value, num_send = 1, delay = 2):
        byte1_2 = self.control_loco.set_function_dfun (func_index, value)
        # If None then cancel
        if byte1_2 == None:
            return
        request = self.api.vlcb.loco_set_dfun(self.control_loco.get_session(), *byte1_2)
        self.api.start_request_repeat (request, num_send, delay)
    
    # Sends on followed by off (typically 4 seconds later)
    def loco_func_trigger (self, func_index, delay = 4):
        #print (f"Func trigger api {func_index}")
        # Turn on
        byte1_2 = self.control_loco.set_function_dfun (func_index, 1)
        if byte1_2 == None:
            return
        request_on = self.api.vlcb.loco_set_dfun(self.control_loco.get_session(), *byte1_2)
        # Turn off (update value immediately - even though not sent yet, but delay request using single shot timer
        byte1_2 = self.control_loco.set_function_dfun (func_index, 0)
        request_off = self.api.vlcb.loco_set_dfun(self.control_loco.get_session(), *byte1_2)
        
        self.api.start_request_onoff (request_on, request_off, delay)
    
    # Update the functions list
    # If index is not provided then use current
    # otherrwise set to the index tab
    def loco_change_functions (self, index=None):
        functions = self.control_loco.get_functions()
        if index != None and index >=0 and index <=2:
            self.ui.locoFuncTab.setCurrentIndex(index)
        else:
            index = self.ui.locoFuncTab.currentIndex()

        # Clear current
        self.ui.locoFuncCombo.clear()

        # put functions based on the tabs
        # typically maximum of twenty something  (28 is the maximum officially supported) but some DCC controllers allow more
        # all rest are put on last tab
        start = 0
        end = 10  # end is actually 1 after to fit in with range command
        if index == 1:
            start = 10
            end = 20
        elif index == 2:
            start = 20
            end = len(functions)
            
        if end > len(functions):
            end = len(functions)
            
        for i in range(start, end):
            self.ui.locoFuncCombo.addItem(functions[i])
            
        # Update function selected features
        self.loco_function_selected ()
        
        
    # This is used based on the dial
    def loco_change_speed (self, new_speed):
        # If returns false then loco not active so ignore
        if (self.control_loco.change_speed(new_speed)):
            self.api.start_request(self.api.vlcb.loco_speeddir(self.control_loco.get_session(), self.control_loco.get_speeddir()))
            self.ui.locoStatusLabel.setText ("Ready")
            self.update_lcd()
        else:
            self.ui.locoStatusLabel.setText ("Released")
            
    # Updates the list of locos (both initial and when locos added / removed)
    # Preserves list if already selected
    def update_loco_list (self):
        # save current entry name - set this active if
        current_index = self.ui.locoComboBox.currentIndex()
        current_loco_text = self.ui.locoComboBox.itemText(current_index) if current_index > 0 else None
        
        # Block signals whilst updating
        self.ui.locoComboBox.blockSignals(True)
        
        self.ui.locoComboBox.clear()
        # Readd the default - none selected
        self.ui.locoComboBox.addItem("Select Locomotive")
        # Add all the locos
        self.ui.locoComboBox.addItems(device_model.get_enabled_locos())
        
        # Set back to previous entry if still valid
        if current_loco_text:
            # Find the index of the previously selected loco in the new list
            new_index = self.ui.locoComboBox.findText(current_loco_text)
            
            if new_index != -1: # Loco was found
                self.ui.locoComboBox.setCurrentIndex(new_index)
                # no need to update
            else: # Loco was removed
                # Entry changed so call loco_change manually
                self.loco_change()
        # Enable the signal
        self.ui.locoComboBox.blockSignals(False)
                
        # Returns the list of locos - using get name
        #for loco_name in device_model.get_enabled_locos():
        #    self.ui.locoComboBox.addItem(loco_name)
        #for loco_name in self.railway.get_loco_names():
        #    self.ui.locoComboBox.addItem(loco_name)
        
            
    ## Setup Dialog for appropriate object type
    def edit_dialog_guiobject (self):
        # Current object - for easy ref
        gui_obj = self.selected_node
        # Load the dialog
        self.edit_gui_dialog = loader.load(os.path.join(basedir, "editguidialog.ui"), self)
        #print (f"Dialog {self.edit_gui_dialog} - {self.edit_gui_dialog.findChildren(QLineEdit)}")
        self.edit_gui_dialog.devNameEdit.setText (gui_obj.name)	# On other dialogs this is devNameText (cannot edit)
        # devTypeCombo is a combo box
        # Set text to current value will set selection default - use True to capitalize
        self.edit_gui_dialog.devTypeCombo.setCurrentText(gui_obj.get_type_str(True))
        self.edit_gui_dialog.numStatesBox.setValue(gui_obj.num_states)
        result = self.edit_gui_dialog.exec()
        
        if result == QDialog.Accepted:
            # check for each value
            gui_obj.set_name (self.edit_gui_dialog.devNameEdit.text())
            gui_obj.set_type_str ( self.edit_gui_dialog.devTypeCombo.currentText() )
            num_states = self.edit_gui_dialog.numStatesBox.value()
            # Num states must be a sensible number 2 to 100
            # The dialog should only allow that anyway
            if num_states > 1 and num_states <= 100:
                gui_obj.num_states = num_states

    
    def edit_dialog_layoutbutton (self):
        # Current object - for easy ref
        button = self.selected_node
        gui_obj = button.parent
        # Load the dialog
        self.edit_gui_dialog = loader.load(os.path.join(basedir, "editgbuttondialog.ui"), self)
        self.edit_gui_dialog.devNameText.setText (gui_obj.name)
        self.edit_gui_dialog.buttonNameText.setText (button.get_long_name())
        # buttonTypeCombo is a combo box
        # Set text to current value will set selection default - use True to capitalize
        self.edit_gui_dialog.buttonTypeCombo.setCurrentText(button.get_type_str(True))
        ## Set size
        self.edit_gui_dialog.buttonSizeXBox.setValue(button.size[0])
        self.edit_gui_dialog.buttonSizeYBox.setValue(button.size[1])
        # If it's a circle then only one dimension so hide Y
        if button.get_type_str(True) == "Circle":
            self.edit_gui_dialog.buttonSizeYBox.hide()
        else:
            self.edit_gui_dialog.buttonSizeYBox.show()
        self.edit_gui_dialog.valueBox.setValue(button.click_value)
        # Set colors
        color_palette = self.edit_gui_dialog.colorUnknownButton.palette()
        color_palette.setColor(QPalette.Button, QColor(button.button_colors[0]))
        self.edit_gui_dialog.colorUnknownButton.setPalette(color_palette)
        self.edit_gui_dialog.colorUnknownButton.setAutoFillBackground(True)
        # On
        color_palette = self.edit_gui_dialog.colorOnButton.palette()
        color_palette.setColor(QPalette.Button, QColor(button.button_colors[1]))
        self.edit_gui_dialog.colorOnButton.setPalette(color_palette)
        self.edit_gui_dialog.colorOnButton.setAutoFillBackground(True)
        # Off
        color_palette = self.edit_gui_dialog.colorOffButton.palette()
        color_palette.setColor(QPalette.Button, QColor(button.button_colors[2]))
        self.edit_gui_dialog.colorOffButton.setPalette(color_palette)
        self.edit_gui_dialog.colorOffButton.setAutoFillBackground(True)
        
        # Add a listener for change to typeComboBox
        self.edit_gui_dialog.buttonTypeCombo.currentIndexChanged.connect(self.button_type_change)
        # Listener for the color pickers
        self.edit_gui_dialog.colorUnknownButton.clicked.connect(self.color_picker_unknown)
        self.edit_gui_dialog.colorOnButton.clicked.connect(self.color_picker_on)
        self.edit_gui_dialog.colorOffButton.clicked.connect(self.color_picker_off)
        
        result = self.edit_gui_dialog.exec()
        
        if result == QDialog.Accepted:
            object_type = self.edit_gui_dialog.buttonTypeCombo.currentText()
            # check for each value
            button.set_type_str (object_type)
            
            size = [0,0]
            size[0] = self.edit_gui_dialog.buttonSizeXBox.value()
            if object_type == "Circle":
                size[1] = size[0]
            else:
                size[1] = self.edit_gui_dialog.buttonSizeYBox.value()
            
            value = self.edit_gui_dialog.valueBox.value()
            # Num states must be a sensible number 2 to 100
            # The dialog should only allow that anyway
            if value >= 0 and value <= 100:
                button.click_value = value
                
            # Get the colours
            # Get the button's current palette
            current_palette = self.edit_gui_dialog.colorUnknownButton.palette()
            # Get the color for the button role
            button_color = current_palette.color(QPalette.Button)
            # Convert the QColor object to a hex string
            button.button_colors[0] = button_color.name()
            # On button
            current_palette = self.edit_gui_dialog.colorOnButton.palette()
            # Get the color for the button role
            button_color = current_palette.color(QPalette.Button)
            # Convert the QColor object to a hex string
            button.button_colors[1] = button_color.name()
            # Off button
            current_palette = self.edit_gui_dialog.colorOffButton.palette()
            # Get the color for the button role
            button_color = current_palette.color(QPalette.Button)
            # Convert the QColor object to a hex string
            button.button_colors[2] = button_color.name()

    # If the button type combobox changes then change the visibility of the Y selector
    def button_type_change (self):
        if self.edit_gui_dialog.buttonTypeCombo.currentText() == "Circle":
            self.edit_gui_dialog.buttonSizeYBox.hide()
        else:
            self.edit_gui_dialog.buttonSizeYBox.show()
            
    def color_picker_unknown (self):
        self.color_picker_dialog ("unknown")
        
    def color_picker_on (self):
        self.color_picker_dialog ("on")
        
    def color_picker_off (self):
        self.color_picker_dialog ("off")
    
    # Only single colour for label so call directly
    # Still use same generic set_button_color to  update the color
    def color_picker_label (self):
        button = self.edit_gui_dialog.colorButton
        current_color = button.palette().color(QPalette.Button)
        #print (f"Current color {current_color}")
        # Open the color picker dialog and wait for user selection
        # Pass the current button color as the initial color
        #color = QColorDialog.getColor(current_color, self.edit_gui_dialog)
        # Using enhanced color picker (possible bug with the above simplified method)
        # possible bug in hsv val setting - so set manually to 255
        # dont know why bug here but not in the other color pickers
        hue, sat, val, alpha = current_color.getHsvF()
        current_color.setHsvF(hue, sat, 1, alpha)
        color_dialog = QColorDialog(current_color, self.edit_gui_dialog)
        #color_dialog.setOptions(QColorDialog.ShowAlphaChannel)
        if color_dialog.exec() == QDialog.Accepted:
            color = color_dialog.selectedColor()
            # Check if a valid color was selected (the user didn't cancel)
            if color.isValid():
                # Update the button's palette with the new color
                self.set_button_color(button, color)
    
    def color_picker_dialog(self, button_type):
        if button_type == "on":
            button = self.edit_gui_dialog.colorOnButton
        elif button_type == "off":
            button = self.edit_gui_dialog.colorOffButton
        else:
            button = self.edit_gui_dialog.colorUnknownButton
        # Get the current color of the button to use as the initial color
        current_color = button.palette().color(QPalette.Button)
        
        # Open the color picker dialog and wait for user selection
        # Pass the current button color as the initial color
        color = QColorDialog.getColor(current_color, self.edit_gui_dialog)
        
        # Check if a valid color was selected (the user didn't cancel)
        if color.isValid():
            # Update the button's palette with the new color
            self.set_button_color(button, color)

    def set_button_color(self, button, color):
        # Get the button's current palette
        palette = button.palette()
        
        # Set the button background color
        palette.setColor(QPalette.Button, color)
        
        # If the background is dark, set the text color to white for contrast
        if color.lightnessF() < 0.5:
            palette.setColor(QPalette.ButtonText, QColor("white"))
        else:
            palette.setColor(QPalette.ButtonText, QColor("black"))
            
        # Apply the updated palette to the button
        button.setPalette(palette)
        # Ensure the background auto-fills to show the palette change
        button.setAutoFillBackground(True)
    
    def edit_dialog_layoutlabel (self):
        # Current object - for easy ref
        label = self.selected_node
        gui_obj = label.parent
        # Load the dialog
        self.edit_gui_dialog = loader.load(os.path.join(basedir, "editglabeldialog.ui"), self)
        self.edit_gui_dialog.devNameText.setText (gui_obj.name)
        self.edit_gui_dialog.labelNameText.setText (label.get_long_name())
        # buttonTypeCombo is a combo box
        # Set text to current value will set selection default - use True to capitalize
        self.edit_gui_dialog.clickTypeCombo.setCurrentText(label.get_type_str(True))
        ## Set size
        self.edit_gui_dialog.labelClickValueBox.setValue(label.get_click_value())
        # Set font
        self.edit_gui_dialog.fontCombo.setCurrentText(label.font)
        self.edit_gui_dialog.fontSizeBox.setValue(label.min_font_size)
        # Set color
        color_palette = self.edit_gui_dialog.colorButton.palette()
        color_palette.setColor(QPalette.Button, QColor(label.font_color))
        self.edit_gui_dialog.colorButton.setPalette(color_palette)
        self.edit_gui_dialog.colorButton.setAutoFillBackground(True)

        # Listener for the color picker
        self.edit_gui_dialog.colorButton.clicked.connect(self.color_picker_label)
        
        result = self.edit_gui_dialog.exec()
        
        if result == QDialog.Accepted:
            click_type = self.edit_gui_dialog.clickTypeCombo.currentText()
            # check for each value
            label.set_type_str (click_type)
            
            label.click_value = self.edit_gui_dialog.labelClickValueBox.value()
            
            # If set through here then max is 3 x min_font_size
            # Could set outside of this
            label.min_font_size = self.edit_gui_dialog.fontSizeBox.value()
            label.max_font_size = 3 * label.min_font_size
            
            # Do not use the Qfont object directly, instead get the font family name
            label.font = self.edit_gui_dialog.fontCombo.currentFont().family()
                
            # Get the colour
            # Get the button current palette
            current_palette = self.edit_gui_dialog.colorButton.palette()
            # Get the color for the button role
            button_color = current_palette.color(QPalette.Button)
            # Convert the QColor object to a hex string
            label.font_color = button_color.name()

            
    # Handle right click - need to get item from position
    def tree_clicked_right(self, position: QPoint):
        item = self.ui.nodeTreeView.indexAt(position)
        # Ignore if no item clicked
        if not item.isValid():
            return
        #print (f"Item {item} - Data {item.data()}")
        # Update the node table view
        node_item = device_model.node_model.itemFromIndex(item)
        self.update_tree_selected (node_item)
        
        # Create a context Menu
        menu = QMenu()
        # different menu depending upon node type
        #print (f"Node {node_item.text()}")
        #print (f"Selected {self.selected_node}")
        if self.selected_node.device_type == "Gui":
            edit_action = menu.addAction("Edit")
        else:
            edit_action = None
        
        selected_action = menu.exec(self.ui.nodeTreeView.viewport().mapToGlobal(position))
        if selected_action == edit_action:
            # Which type of node is this?
            #print (f"Selected node is {type(self.selected_node)}")
            if type(self.selected_node) is GuiObject:
                self.edit_dialog_guiobject()
            elif type(self.selected_node) is LayoutButton:
                self.edit_dialog_layoutbutton()
            elif type(self.selected_node) is LayoutLabel:
                self.edit_dialog_layoutlabel()
            
        
    def tree_clicked(self, item):
        node_item = device_model.node_model.itemFromIndex(item)
        self.update_tree_selected (node_item)
        
    # Updates tree based on current selected_node (if any)
    def update_table (self):
        # If none selected then do nothing
        if self.selected_node == None:
            return
        # If gui / layout object
        if self.selected_node.device_type == "Gui":
            if type(self.selected_node) == GuiObject:
                #self.selected_node = gui_node
                self.node_table_show_gui_node(self.selected_node)
                # If num states < 2 then no button
                if self.selected_node.num_states < 2:
                    self.update_node_buttons (None, None)
                # If exactly 2 then toggle button
                elif self.selected_node.num_states == 2:
                    self.update_node_buttons ("Toggle", None)
                # If more than 2 then up / down
                else:
                    self.update_node_buttons ("Prev", "Next")
            # Otherwise it's a layoutobject (button / label)
            else:
                # new item for child is [parent, type, pos]
                self.node_table_show_gui_child(self.selected_node)
                # Typically GUI children will say Toggle (for a label), or value for a button
                self.update_node_buttons (self.selected_node.get_action_type(), None)
        elif self.selected_node.device_type == "VLCB":
            if type(self.selected_node) is VLCBNode:
                self.node_table_show_node(self.selected_node)
                self.update_node_buttons (None, None)
            # or if it's a ev
            else:
                self.node_table_show_ev(self.selected_node)
                self.update_node_buttons ("On", "Off")

        
    # Update the node table (whether right or left click)
    def update_tree_selected (self, node_item):
        # Reset selected_node to None - then update if selected node
        self.selected_node = None
        # Need to identify what type of node has been clicked
        # Create two values top_string (= parent for children / self text for top level)
        # node_string = text of this node
        # First check is this a top level (doesn't have a parent)
        if (node_item.parent() == None):
            #print (f"Parent node clicked {node_item.text()}")
            node_string = node_item.text()
            top_string = node_string	# For top level then same as name
        # Otherwise use parent to determine type of node
        else:
            #print (f"Node clicked {node_item.text()} - parent {node_item.parent().text()}")
            node_string = node_item.text()
            top_string = node_item.parent().text()
        # Check for structured devices (eg. Gui object always begins with GUI)
        if top_string[0:3] == "GUI":
            #print (f"GUI {node_string}")
            # Temp call On / Off - need to set based on type of GUI object
            #self.update_node_buttons ("On?", "Off?")
            for gui_node in device_model.other_nodes['Gui']:
                new_item = gui_node.check_item(node_item)
                if new_item != None:
                    self.selected_node = new_item
                

        # If not structure name then most likely a normal node which can have any name
        else:
            # Special case - if CANCAM 65535 or CANCMD 65534 then hide buttons
            if node_string[0:6] == "CANCAB" or node_string[0:6] == 'CANCMD':
                self.update_node_buttons (None, None)
            else:
                # Set buttons to normal
                self.update_node_buttons ("On", "Off")
                
            # Check device_model for the node
            for key, node in device_model.nodes.items():
                new_item = node.check_item (node_item)
                if new_item != None:
                    self.selected_node = new_item
                    # If this is a node then show that in table

                        
        self.update_table()

    # Updates the two node buttons at the bottom of the table
    # These are known as evButtonOff & evButtonOn, but may also be used by
    # GUI elements, be hidden etc.
    # Provide text for the On & Off buttons, or set to None to disable
    def update_node_buttons (self, on_text, off_text):
        # Check for None (in which case hide)
        if on_text == None:
            self.ui.evButtonOn.hide()
        else :
            # if "value" set text to "Activate"
            if on_text == "value" or on_text == "Value":
                on_text = "Activate"
            self.ui.evButtonOn.setText(on_text)
            self.ui.evButtonOn.show()
        if off_text == None:
            self.ui.evButtonOff.hide()
        else :
            if off_text == "value" or off_text == "Value":
                off_text = "Activate"
            self.ui.evButtonOff.setText(off_text)
            self.ui.evButtonOff.show()
        
        
    def create_console(self, show=False):
        self.console_window = ConsoleWindowUI(self)
        if show:
            self.console_window.show()    
        
    # Ev clicked off button - also used for "next" when guiobject has multiple
    def ev_clicked_off (self):
        # None selected (shouldn't normally be the case as buttons disabled)
        if self.selected_node == None:
            return
        #print (f"Selected {self.selected_node}")
        if type(self.selected_node) is VLCBEv:
            self.api.start_request(self.api.vlcb.accessory_command(self.selected_node.node.node_id, self.selected_node.ev_id, False))
        elif type(self.selected_node) is GuiObject:
            self.selected_node.activate("GuiObject", 1)
        else:
            self.selected_node.activate()
        
    # Ev clicked on button - also used for "prev" / activate / toggle for other objects
    def ev_clicked_on (self):
        if self.selected_node == None:
            return
        #print (f"Selected {self.selected_node}")
        if type(self.selected_node) is VLCBEv:
            self.api.start_request(self.api.vlcb.accessory_command(self.selected_node.node.node_id, self.selected_node.ev_id, True))
        elif type(self.selected_node) is GuiObject:
            self.selected_node.activate("GuiObject", 0)
        else:
            self.selected_node.activate()

    # Update table for GUI node
    def node_table_show_gui_node (self, node_item):
        self.ui.tableLabel.setText("GUI Node:")
        item = self.ui.nodeTable.verticalHeaderItem(0)
        item.setText("Name:")
        item = self.ui.nodeTable.verticalHeaderItem(1)
        item.setText("Type:")
        item = self.ui.nodeTable.verticalHeaderItem(2)
        item.setText("Num states:")
        item = self.ui.nodeTable.verticalHeaderItem(3)
        item.setText("Current state:")
        item = self.ui.nodeTable.verticalHeaderItem(4)
        item.setText("Comments:")
        
        item = self.ui.nodeTable.item(0,0)
        item.setText(node_item.name)
        item = self.ui.nodeTable.item(1,0)
        item.setText(node_item.object_type)
        item = self.ui.nodeTable.item(2,0)
        item.setText(str(node_item.num_states))
        item = self.ui.nodeTable.item(3,0)
        item.setText(f"{node_item.state_value}")
        item = self.ui.nodeTable.item(4,0)
        item.setText("")
    
    # Update table for gui child
    def node_table_show_gui_child (self, node_item):
        self.ui.tableLabel.setText("GUI Node Object:")
        item = self.ui.nodeTable.verticalHeaderItem(0)
        item.setText("GUI Node:")
        item = self.ui.nodeTable.verticalHeaderItem(1)
        item.setText("Type:")
        item = self.ui.nodeTable.verticalHeaderItem(2)
        item.setText("ID:")
        item = self.ui.nodeTable.verticalHeaderItem(3)
        item.setText("Current state:")
        item = self.ui.nodeTable.verticalHeaderItem(4)
        item.setText("Click action:")
        
        item = self.ui.nodeTable.item(0,0)
        item.setText(node_item.parent.name)
        item = self.ui.nodeTable.item(1,0)
        item.setText(node_item.get_type_str())
        item = self.ui.nodeTable.item(2,0)
        item.setText(str(node_item.get_index()))
        item = self.ui.nodeTable.item(3,0)
        item.setText(f"{node_item.parent.state_value}")
        item = self.ui.nodeTable.item(4,0)
        item.setText(node_item.get_action_str())
        
    # Have the node table show the node information
    def node_table_show_node (self, node_item):
        self.ui.tableLabel.setText("Node:")
        item = self.ui.nodeTable.verticalHeaderItem(1)
        item.setText("Node ID / CAN ID:")
        item = self.ui.nodeTable.verticalHeaderItem(2)
        item.setText("Mode:")
        item = self.ui.nodeTable.verticalHeaderItem(3)
        item.setText("Manuf / Mod:")
        item = self.ui.nodeTable.verticalHeaderItem(4)
        item.setText("Events / Space:")
        
        item = self.ui.nodeTable.item(0,0)
        item.setText(f"{node_item.name}")
        item = self.ui.nodeTable.item(1,0)
        item.setText(node_item.node_string())
        item = self.ui.nodeTable.item(2,0)
        item.setText(f"{node_item.mode}")
        item = self.ui.nodeTable.item(3,0)
        item.setText(node_item.manuf_string())
        item = self.ui.nodeTable.item(4,0)
        item.setText(node_item.ev_num_string())
        
    # node_item = (VLCBEv)
    def node_table_show_ev (self, node_item):
        self.ui.tableLabel.setText("Event:")
        item = self.ui.nodeTable.verticalHeaderItem(1)
        item.setText("Node ID:")
        item = self.ui.nodeTable.verticalHeaderItem(2)
        item.setText("Event ID:")
        item = self.ui.nodeTable.verticalHeaderItem(3)
        item.setText("Value")
        item = self.ui.nodeTable.verticalHeaderItem(4)
        item.setText("Long / short:")
        
        item = self.ui.nodeTable.item(0,0)
        item.setText(f"{node_item.name}")
        item = self.ui.nodeTable.item(1,0)
        item.setText(f"{node_item.node.node_id}")
        item = self.ui.nodeTable.item(2,0)
        item.setText(f"{node_item.ev_id}")
        item = self.ui.nodeTable.item(3,0)
        item.setText(f"{node_item.en:#08x}")
        item = self.ui.nodeTable.item(4,0)
        item.setText(f"{node_item.long_string()}")
        
    # Send exit to automate as well as closing app
    def quit_app(self):
        QCoreApplication.quit()
        
        
    def steal_loco_dialog (self):
        steal_dialog = StealDialog(self)
        steal_dialog.open()
        # Ignore the result of the dialog as it will emit own signals
        
    # Update the LCD display based on the speed
    def update_lcd (self):
        # If not in a session show --
        active = self.control_loco.is_active()
        if active == None or active == False or self.control_loco.get_status() == "stop" :
            self.ui.locoSpeedLcd.display("--")
        # If 0 then use string to ensure 0 displayed
        elif self.control_loco.speed_value() == 0:
            self.ui.locoSpeedLcd.display("0")
        else:
            self.ui.locoSpeedLcd.display(self.control_loco.speed_value())
        if self.control_loco.get_direction() == 1:
            self.ui.locoForwardRadio.setChecked(True)
        elif self.control_loco.get_direction() == 0:
            self.ui.locoReverseRadio.setChecked(True)
    
    # Signal to indicate kalive needs to be checked
    # start / stop as appropriate
    def update_kalive (self):
        if self.control_loco.is_active():
            if not self.kalive_timer.isActive():
                self.kalive_timer.start()
        elif self.kalive_timer.isActive():
            self.kalive_timer.stop()
    
    # Keep alive - called every 4 secs
    # Add a keep alive to the send queue
    def keep_alive (self):
        # Check we have a session to send a keep alive (ie. not in process of trying
        # to aquire a new loco
        if self.control_loco.is_active():
            self.api.start_request(self.api.vlcb.keep_alive(self.control_loco.get_session()))
            
    def steal_loco_check (self):
        steal_dialog = QDialog(self)
        steal_dialog.exec_()
        
    def loco_forward (self):
        # disable button if not active
        if self.control_loco.is_active():
            # set forward and check active
            if (self.control_loco.forward()):
                self.api.start_request(self.api.vlcb.loco_speeddir(self.control_loco.get_session(), self.control_loco.get_speeddir()))
                self.update_lcd()
        
    def loco_reverse (self):
        if self.control_loco.is_active():
            # set reverse and check active
            if (self.control_loco.reverse()):
                self.api.start_request(self.api.vlcb.loco_speeddir(self.control_loco.get_session(), self.control_loco.get_speeddir()))
                self.update_lcd()
        
        
    # Emergency stop - current loco
    # To reset need to set speed to 0 on the dial
    def loco_stop (self, msg="STOP!"):
        # If not active then ignore
        if not self.control_loco.is_active():
            return
        # If calling from a clicked then gives False rather than msg
        if msg == False:
            msg = "STOP!"
        # Need to check we have a valid session (although issue stop regardless of speed)
        if (self.control_loco.stop(msg)):
            self.api.start_request(self.api.vlcb.loco_speeddir(self.control_loco.get_session(), self.control_loco.get_speeddir()))
        self.ui.locoStatusLabel.setText (msg)
        self.update_lcd()
        
    # Emergency stop all
    def loco_stop_all (self):
        #self.control_loco.stop_all()
        self.api.start_request(self.api.vlcb.loco_stop_all())
        self.ui.locoStatusLabel.setText ("Stop All!")
        self.update_lcd()


    # Used to add a device to the TreeView
    # Needed to ensure this is run on the GUI thread
    # First create QStandardItem on the api thread, then send signal
    # to GUI thread with the parent and the child details
    def add_to_tree (self, parent, child):
        parent.appendRow(child)
        
    # Override reiszeEvent
    def resizeEvent(self, event: QResizeEvent):
        self._scale_image_to_fit()
        super().resizeEvent(event) # Call the base class implementation

    # Scale the image
    # If min_size is specified then that is used instead of the QLabel Size
    def _scale_image_to_fit(self, min_size=None):
        if self.loco_image == None:
            return

        # Get the current size of the QLabel where the image will be displayed
        image_size = self.ui.locoImage.size()
        
        # compare against min_size and if neccessary replace image_size
        if (min_size != None):
            if (image_size.width() < min_size.width() or
                image_size.height() < min_size.height()):
                image_size = min_size

        # Scale the original pixmap to fit the label's dimensions.
        # Qt.KeepAspectRatio ensures the image ratio isn't distorted.
        # Qt.SmoothTransformation uses a high-quality scaling algorithm.
        scaled_pixmap = self.loco_image.scaled(
            image_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Set the newly scaled pixmap to the QLabel
        self.ui.locoImage.setPixmap(scaled_pixmap)
        
    # check if a filepath is in dir (default to datadir, otherwise specify the dir to compare against)
    def is_datadir(self, filepath, dir=None):
        if dir==None:
            check_dir = os.path.dirname(self.data_dir)
        else:
            check_dir = os.path.dirname(self.dirs[dir])
        try:
            filedir = os.path.dirname(filepath)
            #print (f"Checking {filedir}, {check_dir}")
            return filedir == check_dir
        except Exception as e:
            print(f"Error checking path: {e}")
            return False
        
    # Import clicked on the menu - import assets (eg. loco file)
    def import_file(self):
        file_dialog = QFileDialog(self,
                        caption="Select Loco file",
                        directory=self.dirs['locos'],
                        filter="Data (*.json)",
                        fileMode=QFileDialog.FileMode.ExistingFile
                        )

        # Get filename
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]

            filename = os.path.basename(selected_file)
            # Check it doesn't already exist
            if (device_model.check_loco_filename(filename) == True):
                QMessageBox.warning(
                    self, 
                    "File exists", # The title of the dialog
                    f"Filename {filename} already exists. Please rename the file first." # The message content
                )
                return
            
            # Todo - is it a valid loco file - try loading as json and ensure it has loco_id as minimum
            
            # Is the file in the locosdir
            if self.is_datadir(selected_file, 'locos'):
                #print (f"{filename} in data directory")
                new_path = selected_file
            # if not and then copy (not it will overwrite existing, but already established it's not being loaded)
            else:
                # New path - includes filename
                new_path = os.path.join(self.dirs['locos'], filename)
                print (f"Copying {selected_file} to {new_path}")
                shutil.copyfile (selected_file, new_path)
                # Todo wrap above in try clause
                #loco_filename = filename
            
            # Now load and add to the file
            #print (f"Loading file {new_path}")
            device_model.import_loco(filename)
            device_model.save_locos()
            self.updated_locos_signal.emit()