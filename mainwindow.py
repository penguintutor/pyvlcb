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
from locolist import LocoList
from loco import Loco
from stealdialog import StealDialog

loader = QUiLoader()
basedir = os.path.dirname(__file__)

app_title = "VLCB App"
url = "http://127.0.0.1:8888/"

class MainWindowUI(QMainWindow):
    
    # Signal whenever data is loaded
    newdata_loaded_signal = Signal()
    # If nodes are updated then need to update elements
    node_updated_signal = Signal()
    steal_dialog_signal = Signal(int)
    
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
        self.last_packet = None
        #self.data_received = 0
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.poll_server)
        self.timer.start()
        
        # Keep alive timer - used for DCC keep alive
        # Create timer, but don't start until aquire locomotive
        self.kalive_timer = QTimer(self)
        self.kalive_timer.setInterval(4000)
        self.kalive_timer.timeout.connect(self.keep_alive)
        
        self.pc_can_id = 60      # CAN ID of CANUSB4
    
        # Layout is useful for giving real names to certain items
        self.layout = Layout()
        
        # VLCB and node creation
        self.vlcb = VLCB(self.pc_can_id)
        
        #Locos
        self.loco_list = LocoList()
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
        self.ui.locoComboBox.currentIndexChanged.connect(self.loco_change)
        self.ui.locoDial.valueChanged.connect(self.loco_change_speed)
        
        self.setCentralWidget(self.ui)
        self.ui.nodeTreeView.show()
        self.show()
        self.create_console()
        
        # Status of the http connection
        self.status = "Not connected"
    
        # Initial discover request
        self.discover()
        
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

        loco_id = self.loco_ids[index]
        loco_name = self.loco_list.loco_name(loco_id)

        self.ui.locoStatusLabel.setText(f"Aquiring {loco_name}")
        # Update with loco_id
        self.loco.loco_id = loco_id
        self.start_request(self.vlcb.allocate_loco(loco_id))
        # Don't check status - instead this will be picked up by the regular polling
        # This could result in a situation where it constantly says "Aquiring"
        # Perhaps consider a retry and/or timeout in future
        self.kalive_timer.start()
        
        
    def loco_change_speed (self, new_speed):
        self.loco.set_speed (new_speed)
        self.start_request(self.vlcb.loco_speeddir(self.loco.session, self.loco.get_speeddir()))
        self.update_lcd()
        
    def update_loco_list (self):
        self.ui.locoComboBox.clear()
        # Readd the default - none selected
        self.ui.locoComboBox.addItem("Loco Name / ID")
        self.loco_ids.append(0)
        # Returns the list of 
        for loco_id in self.loco_list.get_locos():
            self.loco_ids.append(loco_id)
            self.ui.locoComboBox.addItem(self.loco_list.loco_name(loco_id))
        
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
        #print (f"Incoming data {response}")
        # pass to console (unparsed)
        self.console_window.add_log(response)
        # strip date off (don't need except for the log)
        #print (f"Entry {response}")
        id_date_data = response.split(',',3)
        #print (f"ID Date Data {id_date_data}")
        if (len(id_date_data) < 4):
            print (f"Invalid entry - skipping {response}")
            return
        # Todo - id_date_data[2] is i / o - not yet implemented in console
        vlcb_entry = self.vlcb.parse_input(id_date_data[3])
        # If not a valid entry then ignore
        if vlcb_entry == False:
            return
        # Look for specific responses
        # todo - should we check timestamp first? If the entry is from before the first request then may not be
        # interested as it's an old node. Alternatively we could load anyway (max 100 past entries are stored)
        # or we could not retrieve any previous messages by first checking for -1 entries and using that for
        # the start value
        # For now we handle all responses including old ones - but check for whether there are any changes
        ret_opcode = vlcb_entry.opcode()    # Instead of calling method for each condition save it in a variable
        if ret_opcode == 'PNN':    # PNN (Response to query node)
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
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # Session,AddrHigh_AddrLow,SpeedDir,Fn1,Fn2,Fn3'
            loco_id = data_entry['AddrHigh_AddrLow'] & 0x3FFF
            if self.loco.loco_id != loco_id:
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
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            loco_id = data_entry['AddrHigh_AddrLow'] & 0x3FFF
            # Check error code relates to the current loco
            if self.loco.loco_id != loco_id:
                print (f"ERR ID {loco_id} does not match current Loco ID {self.loco.loco_id}")
                return
            if data_entry['ErrCode'] == 1:
                self.ui.locoStatusLabel.setText ("Error - no sessions available")
            # Todo - need to provide option to steal loco
            elif data_entry['ErrCode'] == 2:
                self.ui.locoStatusLabel.setText ("Error - address taken")
                self.steal_dialog_signal.emit(loco_id)

            
            
    # Initial discover of modules    
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
        #steal_dialog = loader.load("stealdialog.ui", None)
        #steal_dialog = loader.load(os.path.join(basedir, "stealwindow.ui"), None)
        steal_dialog = StealDialog(self)
        steal_dialog.open()
        #steal_dialog.exec_()
        
    # Update the LCD display based on the speed
    def update_lcd (self):
        self.ui.locoSpeedLcd.display(self.loco.speed)
        #self.ui.locoForwardRadio
        #self.ui.locoReverseRadio
        
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
        
class Worker (QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    @Slot() # Pyside6.QtCore.Slot
    def run(self):
        self.fn(*self.args, **self.kwargs)
