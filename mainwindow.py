import os
from PySide6.QtCore import QTimer, QCoreApplication, Signal, QThreadPool
from PySide6.QtWidgets import QMainWindow, QAbstractItemView
from PySide6.QtGui import QPixmap
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

loader = QUiLoader()
loader.registerCustomWidget(LayoutDisplay)
basedir = os.path.dirname(__file__)

layout_file = "layout.json"

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
    
    def __init__(self):
        super().__init__()
        self.debug = False
        
        #self.nodes = {} # dict of nodes indexed by NN
        
        self.threadpool = QThreadPool()
        self.update_in_progress = False
        
        self.api = ApiHandler(self.threadpool, url)
        
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
        
        #self.pc_can_id = 60      # CAN ID of CANUSB4
    
        # Layout is useful for giving real names to certain items
        # Also provides list of valid locos
        # Variable is named railway to avoid potential conflict if named layout
        self.railway = Layout(layout_file)
        # pass the layout to the devicemodel
        device_model.set_layout(self.railway)
        
        self.ui = loader.load(os.path.join(basedir, "mainwindow.ui"), None)
        self.setWindowTitle(app_title)
        
        # Signals
        self.steal_dialog_signal.connect (self.steal_loco_dialog)
        self.reset_loco_signal.connect (self.reset_loco)
        self.steal_loco_signal.connect (self.steal_loco)
        self.share_loco_signal.connect (self.share_loco)
        self.update_kalive_signal.connect (self.update_kalive)
        
        # File Menu
        self.ui.actionExit.triggered.connect(self.quit_app)
        
        # Asset Menu
        self.ui.actionDiscover.triggered.connect(self.api.discover)
        
        # Tools Menu
        self.ui.actionShowConsole.triggered.connect(self.show_console)
        self.ui.actionLayoutEdit.triggered.connect(self.layout_edit)
        
        # Tree view
        #self.node_model = device_model.node_model
        #self.node_model.setHorizontalHeaderLabels(['Nodes'])
        self.ui.nodeTreeView.setModel(device_model.node_model)
        self.ui.nodeTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.ui.nodeTreeView.clicked.connect(self.tree_clicked)
        
        # Event buttons
        self.ui.evButtonOff.clicked.connect(self.ev_clicked_off)
        self.ui.evButtonOn.clicked.connect(self.ev_clicked_on)
        
        # Last Event that was selected - use for On/Off buttons
        # has (Node, EVid, EVNum) - num added to make it easier
        self.selected_ev = None
        
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
                
        # Load layout background image
        self.ui.layoutLabel.load_image(self)
        
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
        
        #print (f"LD {self.ui.layoutLabel}")
        #self.ui.layoutLabel.test ("new message")
        
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
    def layout_edit (self):
        # Change layoutdisplay mode
        if self.ui.layoutLabel.mode == "control":
            self.ui.layoutLabel.mode = "edit"
            self.ui.actionLayoutEdit.setText("Layout Control")
        else:
            self.ui.layoutLabel.mode = "control"
            self.ui.actionLayoutEdit.setText("Layout Edit")
    
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
        self.api.start_request(self.api.vlcb.release_loco(self.control_loco.get_session()))
        self.control_loco.release()

        # Check for a valid loco chosen (ie if gone back to 0 then return)
        if index == 0:
            if self.kalive_timer.isActive():
                self.kalive_timer.stop()
            return

        # Update the self.loco entry once we start to aquire
        
        # Get the loc_filename and load
        # index is -1 to skip None selected
        loco_index = self.control_loco.loco_index
        filename = self.railway.get_loco_filename (index -1)
        device_model.locos[loco_index].load_file (filename)
        loco_name = device_model.locos[loco_index].loco_name
        self.ui.locoStatusLabel.setText(f"Aquiring {loco_name}")
        device_model.locos[loco_index].status = 'rloc'
        # Add images and summary
        if "image" in device_model.locos[loco_index].loco_data:
            loco_image = QPixmap(os.path.join(self.railway.loco_dir, device_model.locos[loco_index].loco_data['image']))
            self.ui.locoImage.setPixmap(loco_image)
        else:
            self.ui.locoImage.setPixmap(QPixmap())
        if "summary" in device_model.locos[loco_index].loco_data:
            self.ui.locoInfoText.setText(device_model.locos[loco_index].loco_data['summary'])
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
        # get current index, need both tab and position in tab
        tab = self.ui.locoFuncTab.currentIndex()
        combo = self.ui.locoFuncCombo.currentIndex()
        #print (f"Tab {tab}, Combo {combo}")
        func_index = combo + (10 * tab)
        #self.control_loco.function_pressed(func_index)
        status = self.control_loco.get_function_status(func_index)
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
            
        
    def update_loco_list (self):
        self.ui.locoComboBox.clear()
        # Readd the default - none selected
        self.ui.locoComboBox.addItem("Select Locomotive")
        # Returns the list of locos
        for loco_name in self.railway.get_loco_names():
            self.ui.locoComboBox.addItem(loco_name)
        
    def tree_clicked(self, item):
        node_item = device_model.node_model.itemFromIndex(item)
        for key, node in device_model.nodes.items():
            new_item = node.check_item (node_item)
            if new_item != None:
                # If this is a node then show that in table
                if new_item[1] == 0:
                    self.node_table_show_node(new_item)
                else:
                    self.node_table_show_ev(new_item)
        
        
    def create_console(self, show=False):
        self.console_window = ConsoleWindowUI(self)
        if show:
            self.console_window.show()    
        
    
    def ev_clicked_off (self):
        # None selected (shouldn't normally be the case)
        if self.selected_ev == None:
            return
        self.api.start_request(self.api.vlcb.accessory_command(self.selected_ev[0], self.selected_ev[2], False))
        
    def ev_clicked_on (self):
        if self.selected_ev == None:
            return
        self.api.start_request(self.api.vlcb.accessory_command(self.selected_ev[0], self.selected_ev[2], True))

        
    # Have the node table show the node information
    # node_item = (nn, 0)
    def node_table_show_node (self, node_item):
        nn = node_item[0]
        
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
        item.setText(f"{device_model.nodes[nn].name}")
        item = self.ui.nodeTable.item(1,0)
        item.setText(device_model.nodes[nn].node_string())
        item = self.ui.nodeTable.item(2,0)
        item.setText(f"{device_model.nodes[nn].mode}")
        item = self.ui.nodeTable.item(3,0)
        item.setText(device_model.nodes[nn].manuf_string())
        item = self.ui.nodeTable.item(4,0)
        item.setText(device_model.nodes[nn].ev_num_string())
        
    # node_item = (nn, ev)
    def node_table_show_ev (self, node_item):
        nn = node_item[0]
        ev_id = node_item[1]
        self.selected_ev = node_item
        # Add the EvNum
        self.selected_ev.append(device_model.nodes[nn].ev[ev_id].en)
        
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
        item.setText(f"{device_model.nodes[nn].ev[ev_id].name}")
        item = self.ui.nodeTable.item(1,0)
        item.setText(f"{device_model.nodes[nn].node_id}")
        item = self.ui.nodeTable.item(2,0)
        item.setText(f"{ev_id}")
        item = self.ui.nodeTable.item(3,0)
        item.setText(f"{device_model.nodes[nn].ev[ev_id].en:#08x}")
        item = self.ui.nodeTable.item(4,0)
        item.setText(f"{device_model.nodes[nn].ev[ev_id].long_string()}")
        
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
        if self.control_loco.is_active() == False or self.control_loco.get_status() == "stop" :
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
        # set forward and check active
        if (self.control_loco.forward()):
            self.api.start_request(self.api.vlcb.loco_speeddir(self.control_loco.get_session(), self.control_loco.get_speeddir()))
            self.update_lcd()
        
    def loco_reverse (self):
        # set reverse and check active
        if (self.control_loco.reverse()):
            self.api.start_request(self.api.vlcb.loco_speeddir(self.control_loco.get_session(), self.control_loco.get_speeddir()))
            self.update_lcd()
        
        
    # Emergency stop - current loco
    # To reset need to set speed to 0 on the dial
    def loco_stop (self, msg="STOP!"):
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

