import os
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal, Slot, QThreadPool, QRunnable
from PySide6.QtWidgets import QMainWindow, QTextBrowser, QAbstractItemView, QTableWidgetItem
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader
import queue
import time
from consolewindow import ConsoleWindowUI
from layout import Layout
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from vlcbclient import VLCBClient
#from locolist import LocoList
from loco import Loco
from stealdialog import StealDialog

loader = QUiLoader()
basedir = os.path.dirname(__file__)

layout_file = "layout.json"

app_title = "VLCB App"
#url = "http://127.0.0.1:8888/"
url = "http://127.0.0.1:5000/"

read_rate = 200

class MainWindowUI(QMainWindow):
    
    # Signal whenever data is loaded
    newdata_loaded_signal = Signal()
    # If nodes are updated then need to update elements
    node_updated_signal = Signal()
    steal_dialog_signal = Signal(int)
    # Handle loco selection
    # reset loco to none selected (if aquire failed or loco stolen by another controller)
    reset_loco_signal = Signal()
    steal_loco_signal = Signal() # Attempt to steal loco
    share_loco_signal = Signal() # Attempt to share loco
    
    def __init__(self):
        super().__init__()
        self.debug = False
        
        self.nodes = {} # dict of nodes indexed by NN
        
        self.threadpool = QThreadPool()
        self.update_in_progress = False
        
        # The class is called client, but as it's used to communicate
        # with the server it's referred to in this as self.server
        self.server = VLCBClient(url)
        
        # Add request to be sent next time timer expires
        self.send_queue = []
        
        # Current position in server log entries and amount of data received
        # If -1 will try and get all including old entries
        # If None just get the last few packets received (effectively start from current instead of history)
        # None is -5 to ensure see the initial discover
        self.last_packet = None
        #self.data_received = None
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(read_rate)
        self.timer.timeout.connect(self.poll_server)
        self.timer.start()
        
        # Keep alive timer - used for DCC keep alive
        # Create timer, but don't start until aquire locomotive
        self.kalive_timer = QTimer(self)
        self.kalive_timer.setInterval(4000)
        self.kalive_timer.timeout.connect(self.keep_alive)
        
        self.pc_can_id = 60      # CAN ID of CANUSB4
    
        # Layout is useful for giving real names to certain items
        # Also provides list of valid locos
        self.layout = Layout(layout_file)
        
        # VLCB and node creation
        self.vlcb = VLCB(self.pc_can_id)
        
        #Locos
        #self.loco_list = LocoList()
        # This is the loco being controlled through the interface
        self.loco = Loco()
        # Store the loco ids in the same number as the list
        # Makes it easier to lookup from locoComboList
        self.loco_ids = []
        
        self.ui = loader.load(os.path.join(basedir, "mainwindow.ui"), None)
        self.setWindowTitle(app_title)
        
        # Signals
        self.newdata_loaded_signal.connect (self.update_console)
        self.node_updated_signal.connect (self.update_nodes)
        self.steal_dialog_signal.connect (self.steal_loco_dialog)
        self.reset_loco_signal.connect (self.reset_loco)
        self.steal_loco_signal.connect (self.steal_loco)
        self.share_loco_signal.connect (self.share_loco)
        
        # File Menu
        self.ui.actionExit.triggered.connect(self.quit_app)
        
        # Asset Menu
        self.ui.actionDiscover.triggered.connect(self.discover)
        
        # Tree view
        self.node_model = QStandardItemModel()
        self.node_model.setHorizontalHeaderLabels(['Nodes'])
        self.ui.nodeTreeView.setModel(self.node_model)
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
        
        # Update LCD - used to set '-' at start
        self.update_lcd()
        
        self.setCentralWidget(self.ui)
        self.ui.nodeTreeView.show()
        self.show()
        self.create_console()
        
        # Status of the http connection
        self.status = "Not connected"
    
        # Initial discover request
        self.discover()
        
    def steal_loco (self):
        # Check we have valid loco_id (if not reset)
        if (self.loco.loco_id == 0):
            self.reset_loco()
            return
        loco_id = self.loco.loco_id
        #loco_name = self.loco_list.loco_name(loco_id)
        loco_name = self.loco.loco_name
        self.ui.locoStatusLabel.setText(f"Stealing {loco_name}")
        self.loco.status = 'gloc'
        self.start_request(self.vlcb.steal_loco(loco_id))
    
    def share_loco (self):
        # Check we have valid loco_id (if not reset)
        if (self.loco.loco_id == 0):
            self.reset_loco()
            return
        loco_id = self.loco.loco_id
        #loco_name = self.loco_list.loco_name(loco_id)
        loco_name = self.loco.loco_name
        self.ui.locoStatusLabel.setText(f"Req sharing {loco_name}")
        self.start_request(self.vlcb.share_loco(loco_id))
        
    # Reset loco selection in GUI and remove references
    def reset_loco (self):
        # remove keep alive timer if active
        if self.kalive_timer.isActive():
                self.kalive_timer.stop()
        self.loco.reset()
        # Change combo after reset - that way the post change
        # will not send a release message
        self.ui.locoComboBox.setCurrentIndex(0)
        self.ui.locoStatusLabel.setText(f"None active") 
        
       
    # When loco change requested through combobox
    def loco_change (self, index):
        # Release old loco
        if self.loco.status == "on" and self.loco.session != 0:
            # Sends a release but doesn't check for a response
            self.start_request(self.vlcb.release_loco(self.loco.session))
            self.loco.released()
            # Normally would want to stop the keep alive but we are hoping to aquire a new session immediately after
            # So the keep alive will just ignore until aquired

        # Check for a valid loco chosen (ie if gone back to 0 then return)
        if index == 0:
            if self.kalive_timer.isActive():
                self.kalive_timer.stop()
            return

        # Update the self.loco entry once we start to aquire
        
        # Get the loc_filename and load
        # index is -1 to skip None selected
        filename = self.layout.get_loco_filename (index -1)
        self.loco.load_file (filename)
        loco_name = self.loco.loco_name

        self.ui.locoStatusLabel.setText(f"Aquiring {loco_name}")
        # Update with loco_id
        #self.loco.loco_id = loco_id
        self.start_request(self.vlcb.allocate_loco(self.loco.loco_id))
        self.loco.status = 'rloc'
        
        # Update the functions menu
        self.loco_change_functions(0)
        self.loco.function_reset()
        # Don't check status - instead this will be picked up by the regular polling
        # This could result in a situation where it constantly says "Aquiring"
        # Perhaps consider a retry and/or timeout in future
        self.kalive_timer.start()
        
    # Update function selected features
    # When combobox / tab selected
    def loco_function_selected (self):
        # get current index, need both tab and position in tab
        tab = self.ui.locoFuncTab.currentIndex()
        combo = self.ui.locoFuncCombo.currentIndex()
        #print (f"Tab {tab}, Combo {combo}")
        func_index = combo + (10 * tab)
        #print (f"Function {func_index}")
        # get [status, type]
        status = self.loco.get_function_status(func_index)
        # If we don't have a status then the function button doesn't exist
        if status == None:
            self.ui.locoFuncButton.setText(" - ")
            return
        # If trigger then button should be activate:
        if status[1] == "trigger":
            self.ui.locoFuncButton.setText("Activate")
        elif status[1] == "latch":
            # if on - button will turn off
            if status[0] == 1:
                self.ui.locoFuncButton.setText ("Turn Off")
            else:
                self.ui.locoFuncButton.setText ("Turn On")
        # Eg if status is none then not supported
        else:
            self.ui.locoFuncButton.setText (" -- ")
        
    # Button has been pressed
    def loco_function_pressed (self):
        # get current index, need both tab and position in tab
        tab = self.ui.locoFuncTab.currentIndex()
        combo = self.ui.locoFuncCombo.currentIndex()
        #print (f"Tab {tab}, Combo {combo}")
        func_index = combo + (10 * tab)
        #print (f"Function {func_index}")
        # get [status, type]
        status = self.loco.get_function_status(func_index)
        # If we don't have a status then the function doesn't exist
        if status == None:
            return
        
                # If trigger then button should be activate:
        if status[1] == "trigger":
            self.loco_func_trigger (func_index)
            # no need to update button as still say activate
        else:
            # if <= F12 then send multiple times (NRMA standard)
            if func_index <= 12:
                #print (f"Func {func_index}, current {status[0]}, new {1-status[0]}")
                self.loco_func_change (func_index, 1-status[0], 3)
            # otherwise send once
            else:
                self.loco_func_change (func_index, 1-status[0])
            # Update button
            self.loco_function_selected()
    
    # change value (if need to send multiple then set num_send to number of times
    # Sent every 2 seconds (or change delay) - delay in seconds
    def loco_func_change (self, func_index, value, num_send = 1, delay = 2):
        byte1_2 = self.loco.set_function_dfun (func_index, value)
        # If None then cancel
        if byte1_2 == None:
            return
        self.start_request(self.vlcb.loco_set_dfun(self.loco.session, *byte1_2))
        num_send -= 1
        if num_send > 0:
            QTimer.singleShot(delay * 1000, lambda: self.loco_func_change(func_index, value, num_send, delay)) 
    
    # Sends on followed by off (typically 4 seconds later)
    def loco_func_trigger (self, func_index, delay = 4):
        # Turn on
        byte1_2 = self.loco.set_function_dfun (func_index, 1)
        if byte1_2 == None:
            return
        self.start_request(self.vlcb.loco_set_dfun(self.loco.session, *byte1_2))
        # Turn off (update value immediately, but delay request using single shot timer
        byte1_2 = self.loco.set_function_dfun (func_index, 0)
        # Don't check for None returned as if it worked before should be no reason for it to fail now
        QTimer.singleShot(delay * 1000, lambda: self.start_request(self.vlcb.loco_set_dfun(self.loco.session, *byte1_2))) 
        
    
    # Update the functions list
    # If index is not provided then use current
    # otherrwise set to the index tab
    def loco_change_functions (self, index=None):
        functions = self.loco.get_functions()
        if index != None and index >=0 and index <=2:
            self.ui.locoFuncTab.setCurrentIndex(index)
        else:
            index = self.ui.locoFuncTab.currentIndex()

        # Clear current
        self.ui.locoFuncCombo.clear()

        # put functions based on the tabs
        # typically maximum of twenty something  (28 is the maximum officially supported) but some DCC controllers allow more
        # all rest are put on last tab
        #print (f"Current index {tab}")
        #print (f"Functions {functions}")
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
        # If not in a session then ignore
        if self.loco.is_active():
            # Special case if stop and 0 then reset stop
            if self.loco.status == "stop" and new_speed == 0:
                self.loco.status = "on"
                self.ui.locoStatusLabel.setText ("Ready")
            self.loco.set_speed (new_speed)
            self.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.update_lcd()
        
    def update_loco_list (self):
        self.ui.locoComboBox.clear()
        # Readd the default - none selected
        self.ui.locoComboBox.addItem("Select Locomotive")
        self.loco_ids.append(0)
        # Returns the list of 
        for loco_name in self.layout.get_loco_names():
            #self.loco_ids.append(loco_id)
            self.ui.locoComboBox.addItem(loco_name)
        
    def tree_clicked(self, item):
        node_item = self.node_model.itemFromIndex(item)
        for key, node in self.nodes.items():
            new_item = node.check_item (node_item)
            if new_item != None:
                # If this is a node then show that in table
                if new_item[1] == 0:
                    self.node_table_show_node(new_item)
                else:
                    self.node_table_show_ev(new_item)
        
        
    def create_console(self, show=True):
        self.console_window = ConsoleWindowUI(self)
        if show:
            self.console_window.show()    
    
    def poll_server(self):
        # Only allow one check_responses thread to run at a time
        if self.update_in_progress == True:
            #print ("Still running - skipping")
            return
        
        worker = Worker(self.thread_getupdate, self.newdata_loaded_signal, self.node_updated_signal)
        self.threadpool.start(worker)
        return
        
    def update_console (self):
        self.console_window.update_log()
    
    def update_nodes (self):
        pass
    
    def ev_clicked_off (self):
        # None selected (shouldn't normally be the case)
        if self.selected_ev == None:
            return
        self.start_request(self.vlcb.accessory_command(self.selected_ev[0], self.selected_ev[2], False))
        
    def ev_clicked_on (self):
        if self.selected_ev == None:
            return
        self.start_request(self.vlcb.accessory_command(self.selected_ev[0], self.selected_ev[2], True))

        
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
        item.setText(f"{self.nodes[nn].name}")
        item = self.ui.nodeTable.item(1,0)
        item.setText(self.nodes[nn].node_string())
        item = self.ui.nodeTable.item(2,0)
        item.setText(f"{self.nodes[nn].mode}")
        item = self.ui.nodeTable.item(3,0)
        item.setText(self.nodes[nn].manuf_string())
        item = self.ui.nodeTable.item(4,0)
        item.setText(self.nodes[nn].ev_num_string())
        
    # node_item = (nn, ev)
    def node_table_show_ev (self, node_item):
        nn = node_item[0]
        ev_id = node_item[1]
        self.selected_ev = node_item
        # Add the EvNum
        self.selected_ev.append(self.nodes[nn].ev[ev_id].en)
        
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
        item.setText(f"{self.nodes[nn].ev[ev_id].name}")
        item = self.ui.nodeTable.item(1,0)
        item.setText(f"{self.nodes[nn].node_id}")
        item = self.ui.nodeTable.item(2,0)
        item.setText(f"{ev_id}")
        item = self.ui.nodeTable.item(3,0)
        item.setText(f"{self.nodes[nn].ev[ev_id].en:#08x}")
        item = self.ui.nodeTable.item(4,0)
        item.setText(f"{self.nodes[nn].ev[ev_id].long_string()}")

        
    # This method is called whenever we get a valid response
    # Used to determine if further action is required (eg. discovery or update status)
    # Note this will see all cbus messages, including ones sent to/from other nodes
    # <id>,<timestamp>,<incoming>,<message>
    # Note incoming is either i (incoming) or o (outgoing)
    
    def handle_incoming_data (self, response):
        if self.debug:
            print (f"Incoming data {response}")
        # pass to console (unparsed)
        self.console_window.add_log(response)
        # strip date off (don't need except for the log)
        #print (f"Entry {response}")
        id_date_data = response.split(',',3)
        #print (f"ID Date Data {id_date_data}")
        if (len(id_date_data) < 4):
            print (f"Invalid entry - skipping {response}")
            return
        vlcb_entry = self.vlcb.parse_input(id_date_data[3])
        # If not a valid entry then ignore
        if vlcb_entry == False:
            if self.debug:
                print (f"Not a valid entry {id_date_data}")
            return
        # Look for specific responses
        # todo - should we check timestamp first? If the entry is from before the first request then may not be
        # interested as it's an old node. Alternatively we could load anyway (max 100 past entries are stored)
        # or we could not retrieve any previous messages by first checking for -1 entries and using that for
        # the start value
        # For now we handle all responses including old ones - but check for whether there are any changes
        ret_opcode = vlcb_entry.opcode()    # Instead of calling method for each condition save it in a variable
        if self.debug:
            print (f"Op code {ret_opcode}")
        if ret_opcode == 'ERSTOP':    # Emergency stop all
            # Emergency stop and stop all are the same
            # except for the message
            self.loco_stop ("STOP ALL!")
            
        elif ret_opcode == 'PNN':    # PNN (Response to query node)
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # Determine mode based on flags (bit 3)
            # Flags bit 0 = consumer, bit 1 = producer, bit 2= FliM, bit 3 = supports bootloading
            if data_entry['Flags'] & 0x4:
                mode = "FLiM"
            else:
                mode = "SLiM"
            # if we don't already have this device add it
            if not data_entry['NN'] in self.nodes.keys():
                self.nodes[data_entry['NN']] = VLCBNode(data_entry['NN'], mode, vlcb_entry.can_id, data_entry['ManufId'], data_entry['ModId'] ,data_entry['Flags'])
                self.nodes[data_entry['NN']].set_name(self.layout.node_name(data_entry['NN']))
                # Add to Tree View
                #print ("Adding entry")
                #node = QStandardItem(f"Unknown, {data_entry['NN']}, {vlcb_entry.can_id}")
                self.node_model.appendRow(self.nodes[data_entry['NN']].gui_node)
            else:
                # Update existing entry
                items_changed = self.nodes[data_entry['NN']].update_node({'Mode': mode, 'ManfId': data_entry['ManufId'], 'ModId': data_entry['ModId'], 'Flags': data_entry['Flags']})
                # If no items changed then no need to check for further updates
                if items_changed == 0:
                    return
                # Node is updated as part of update_node - so next block of text not reqired
                #node_string = f" {data_entry['NN']}"        # Includes a space as that's part of the string
                #for i in range (0, self.node_model.rowCount()):
                #    this_item = self.node_model.item(i).text()
                #    this_item_parts = this_item.split(',')
                #    if this_item_parts[1] == node_string:
                #        self.node_model.item(i).setText(f"Unknown, {data_entry['NN']}, {vlcb_entry.can_id}")
            # If this is new, or has changed then we can also get the number of events
            self.discover_evn (data_entry['NN'])
        elif ret_opcode == 'NUMEV':    # Number of configured events
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not data_entry['NN'] in self.nodes.keys():
                print (f"NUMV response from Unknown node {data_entry['NN']}")
                return
            # Update node with evnum value
            self.nodes[data_entry['NN']].set_numev(data_entry['NumEvents'])
        elif ret_opcode == 'EVNLF':    # Number of event space left in node
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not data_entry['NN'] in self.nodes.keys():
                print (f"EVNLF response from Unknown node {data_entry['NN']}")
                return
            # Update node with evnum value
            self.nodes[data_entry['NN']].set_evspc(data_entry['EVSPC'])
            # Add a query for the next discovery stage - get a list of all the events
            self.discover_nerd (data_entry['NN'])
        elif ret_opcode == 'ENRSP':    # EV discovery
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not data_entry['NN'] in self.nodes.keys():
                print (f"ENRSP response from Unknown node {data_entry['NN']}")
                return
            # Add event to node
            #print (f"Adding to {data_entry['NN']}, Ev {data_entry['EnIndex']}, Name {data_entry['En3_0']:#08x}")
            self.nodes[data_entry['NN']].add_ev(data_entry['EnIndex'], data_entry['En3_0'])
            self.nodes[data_entry['NN']].ev[data_entry['EnIndex']].set_name(self.layout.ev_name(data_entry['NN'], data_entry['EnIndex'], data_entry['En3_0']))
        # Indicates allocation of loco - need to verify this is expected
        elif ret_opcode == 'PLOC':
            # Must be in status 'rloc' or 'gloc' - otherwise ignore as we are not waiting on plooc
            if self.loco.is_aquiring() == False:
                return
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # Session,AddrHigh_AddrLow,SpeedDir,Fn1,Fn2,Fn3'
            loco_id = data_entry['AddrHigh_AddrLow'] & 0x3FFF
            if self.loco.loco_id != loco_id:
                # If it doesn't match then perhaps this was for a different controller
                print (f"PLOC ID {loco_id} does not match current Loco ID {self.loco.loco_id}")
                return
            # Update loco with session, speed and direction
            self.loco.session = data_entry['Session']
            self.loco.set_speeddir (data_entry['SpeedDir'])
            self.loco.set_functions (data_entry['Fn1'], data_entry['Fn2'], data_entry['Fn3'])
            self.ui.locoStatusLabel.setText ("Ready")
            # Set status to on last gives time to ensure all entries updated
            self.loco.status = "on"
            # Todo update controller with new values
            self.update_lcd ()
        # ERR is error from DCC controller - eg. problem aquiring loco
        elif ret_opcode == 'ERR':
            # Depending upon the error code the data may have different interpretations
            # Stored as Byte1, Byte2, ErrCode - where Byte1,Byte2 may eqal AddrHigh_AddrLow, or
            # may be Byte1 = Session ID, Byte 2 = 0
            # So only check after looking at the ErrCode
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            #loco_id = data_entry['AddrHigh_AddrLow'] & 0x3FFF
            # Check error code relates to the current loco
            if data_entry['ErrCode'] == 1:
                # Only valid during aquiring status
                if self.loco.is_aquiring() == False:
                    return
                loco_id = VLCB.bytes_to_addr(data_entry['Byte1'],data_entry['Byte2']) & 0x3FFF
                if self.loco.loco_id != loco_id:
                    if self.debug:
                        print (f"ERR ID {loco_id} does not match current Loco ID {self.loco.loco_id}")
                    return
                self.ui.locoStatusLabel.setText ("Error - no sessions available")
            # Already taken - option to steal
            elif data_entry['ErrCode'] == 2:
                #Only for us if we haven't completed the session setup
                #print (f"Session status {self.loco.status}")
                if self.loco.status == "on":
                    #print ("Not our session")
                    return
                elif self.loco.is_aquiring() == False:
                    #print ("Not aquiring session")
                    return
                loco_id = VLCB.bytes_to_addr(data_entry['Byte1'],data_entry['Byte2']) & 0x3FFF
                if self.debug:
                    print ("Error code 2 - loco taken")
                if self.loco.loco_id != loco_id:
                    if self.debug:
                        print (f"ERR ID {loco_id} does not match current Loco ID {self.loco.loco_id}")
                    return
                self.ui.locoStatusLabel.setText ("Error - address taken")
                self.steal_dialog_signal.emit(loco_id)
            elif data_entry['ErrCode'] == 8:
                # If we are trying to aquire a session then this could be us resetting other node
                if self.loco.is_aquiring():
                    return
                # byte 1 is now sessionid - byte2 is ignored - should be 00
                session_id = int(data_entry['Byte1'])
                # if not our current session_id then could be for a different controller so ignore
                if session_id != 0 and session_id == self.loco.session:
                    if self.debug:
                        print (f"Session cancelled {session_id}")
                    # This updates the loco and the GUI
                    self.reset_loco()
                else:
                    if self.debug:
                        print (f"Session not cancelled {session_id}, loco session {self.loco.session}")
            
    # Initial discovery of modules    
    def discover (self):
        self.start_request(self.vlcb.discover())
        
    # 2nd phase in discovery RQEVN to get number of events
    # and NNEVN - get number of events available
    def discover_evn (self, node_id):
        self.start_request(self.vlcb.discover_evn(node_id))
        self.start_request(self.vlcb.discover_nevn(node_id))
        
    # 3rd phase of discover Read back all stored events in a node (NERD)
    def discover_nerd (self, node_id):
        self.start_request(self.vlcb.discover_nerd(node_id))
    
    # Places request onwait list
    # type is what kind of command to prepend with - eg. send (for cbus) or server etc.
    # comma is added automatically
    # set to "" if already formatted
    # Adding priority pushes to front of queue
    def start_request (self, request, type="send", priority=False):
        # add type to request
            
        # Priority ignores list length and just inserts at front
        # pushes other priority items further down the list as well
        if priority:
            self.send_queue.insert(0, request)
        # only add to the list if <= 10 items already
        if len(self.send_queue) > 10:
            return False
        self.send_queue.append(request)
        #print (f"New queue {self.send_queue}")
        return True
        
    # Gets request off the queue
    # Returns false if no requests, otherwise returns request string
    # If remove = True (default) then remove entry from the queue
    def get_request (self, remove=True):
        # If no entries then return false
        if len(self.send_queue) < 1:
            return False
        # if no remove then just return value
        if remove == False:
            return self.send_queue[0]
        # Otherwise pop the entry
        return self.send_queue.pop(0)
        
        
    # Send exit to automate as well as closing app
    def quit_app(self):
        QCoreApplication.quit()
        
    # Run in thread
    # Query web - get data
    # If from web notify newdata
    # If update to node / events then update nodes and
    # notify updatenode
    def thread_getupdate(self, nodes, newdata_emit=None, updatenode_emit=None):
        #Only allow one thread at a time
        self.update_in_progress = True
               
        # see if there is a specific request
        request = self.get_request()
        if request != False:
            #print (f"Sending request {request}")
            response = self.server.send (request)
            if response == None:
                self.update_in_progress = False
                self.status = "Not connected"
                return
            else:
                self.status = "Connected"
            # Todo handle response
            # Just a True / false response
            # clear send_request ready for next request
            
        # Get updates since last_packet
        response = self.server.read (self.last_packet)
        # If response None then error getting update - skip for now and
        # try again next time we poll
        if response == None:
            self.update_in_progress = False
            self.status = "Not connected"
            return
        else:
            self.status = "Connected"
        
        #print (f"**** Response {response}")
        # First line is summary
        # Check for an empty data first as we can ignore
        if response[0:10] == "Read,0,0,0":
            # No new data received
            pass
        # Check response starts with "Read,"
        elif response[0:5] == "Read,":
            # split into status_line and data
            status_data = response.split('\n',1)
            #print (f"Status data {status_data}")

            # First line format is "Read,<start>,<end>,<numlines>"
            header = status_data[0].split(',', 3)
            
            #print (f"Header {header}")
            
            # check to see if field 3 is negative - if so then most likely that
            # the server has been restarted and we are ahead
            # Here just reset last_packet to 0 and then continue
            # If prefer could continue, or perhaps request a negative number
            # to just get a fixed number of entries
            packets_received = int (header[3])
            if packets_received < 0:
                #print (f"Out of step with server, {self.last_packet} {packets_received}")
                print ("Restarting after possible server restart")
                self.last_packet = None
                self.update_in_progress = False
                return
            
            # need end to know what our last stored value is
            this_last_packet = int(header[2])
            if self.last_packet == None or self.last_packet < this_last_packet:
                self.last_packet = this_last_packet
            #print (f"Status {status_data}")                
            data_packets = status_data[1].split('\n')
            #print (f"Data packets: {data_packets}")
            for data_packet in data_packets:
                # if data_packet is empty then skip completely - without any notice as most likely due to \n at end
                if data_packet == '':
                    continue
                
                #print (f"Handling packet {data_packet}")
                if len(data_packet) < 5:    # If data too short (perhaps empty line) - in reality this is much longer as includes date
                    print ("Skipping empty packet")
                    print (f"This packet {data_packet}")
                    print (f"Data packets {data_packets}")
                    continue
                #self.data_received += 1    # Count packets received (not needed instead trust last packet number)
                # passes entire line to 
                self.handle_incoming_data(data_packet)
            self.newdata_loaded_signal.emit()
        else:
            print (f"Unrecognised response {response}")
        
        self.update_in_progress = False
        
    def steal_loco_dialog (self):
        steal_dialog = StealDialog(self)
        steal_dialog.open()
        # Ignore the result of the dialog as it will emit own signals
        
    # Update the LCD display based on the speed
    def update_lcd (self):
        # If not in a session show --
        if self.loco.is_active() == False or self.loco.status == "stop" :
            self.ui.locoSpeedLcd.display("--")
        # If 0 then use string to ensure 0 displayed
        elif self.loco.speed_value() == 0:
            self.ui.locoSpeedLcd.display("0")
        else:
            self.ui.locoSpeedLcd.display(self.loco.speed_value())
        if self.loco.direction == 1:
            self.ui.locoForwardRadio.setChecked(True)
        elif self.loco.direction == 0:
            self.ui.locoReverseRadio.setChecked(True)
        
    # Keep alive - called every 4 secs
    # Add a keep alive to the send queue
    def keep_alive (self):
        # Check we have a session to send a keep alive (ie. not in process of trying
        # to aquire a new loco
        if self.loco.status == "on" and self.loco.session != 0:
            self.start_request(self.vlcb.keep_alive(self.loco.session))
            
            
    def steal_loco_check (self, num_loco):
        steal_dialog = QDialog(self)
        steal_dialog.exec_()
        
    def loco_forward (self):
        self.loco.set_direction (1)
        if self.loco.is_active():
            self.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.update_lcd()
        
    def loco_reverse (self):
        self.loco.set_direction (0)
        if self.loco.is_active():
            self.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.update_lcd()
        
        
    # Emergency stop - current loco
    # To reset need to set speed to 0 on the dial
    def loco_stop (self, msg="STOP!"):
        # If calling from a clicked then gives False rather than msg
        if msg == False:
            msg = "STOP!"
        self.loco.set_stop()
        if self.loco.session != 0:
            # check we have a session
            # don't check status as this is emergency stop so send regardless
            self.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.ui.locoStatusLabel.setText (msg)
        self.update_lcd()
        
    def loco_stop_all (self):
        self.start_request(self.vlcb.loco_stop_all())
        
class Worker (QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    @Slot() # Pyside6.QtCore.Slot
    def run(self):
        self.fn(*self.args, **self.kwargs)
