import os
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal, Slot, QThreadPool, QRunnable
from PySide6.QtWidgets import QMainWindow, QTextBrowser, QAbstractItemView, QTableWidgetItem
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader
import queue
import time
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from consolewindow import ConsoleWindowUI
import zmq

loader = QUiLoader()
basedir = os.path.dirname(__file__)

app_title = "VLCB App"

class MainWindowUI(QMainWindow):
    
    # Signal whenever data is loaded
    newdata_loaded_signal = Signal()
    # If nodes are updated then need to update elements
    node_updated_signal = Signal()
    
    def __init__(self):
        super().__init__()
        self.debug = False
        
        self.nodes = {} # dict of nodes indexed by NN
        
        self.threadpool = QThreadPool()
        self.update_in_progress = False
        
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")
        
        # Add request to be sent next time timer expires
        self.send_queue = []
        
        # Current position in server log entries and amount of data received
        self.last_packet = 0
        #self.data_received = 0
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.poll_server)
        self.timer.start()
        self.pc_can_id = 60      # CAN ID of CANUSB4
        
        # VLCB and node creation
        self.vlcb = VLCB(self.pc_can_id)
        
        self.ui = loader.load(os.path.join(basedir, "mainwindow.ui"), None)
        self.setWindowTitle(app_title)
        
        # Signals
        self.newdata_loaded_signal.connect (self.update_console)
        self.node_updated_signal.connect (self.update_nodes)
        
        # File Menu
        self.ui.actionExit.triggered.connect(self.quit_app)
        
        # Asset Menu
        self.ui.actionDiscover.triggered.connect(self.discover)
        
        # Tree view
        #self.ui.nodeTreeView.setColumnCount(3)
        #self.ui.setHeaderLabels(['Name', 'Number', 'Type'])
        self.node_model = QStandardItemModel()
        self.node_model.setHorizontalHeaderLabels(['Nodes'])
        #self.node_model.setHorizontalHeaderLabels(['Name', 'Number', 'Type'])
        self.ui.nodeTreeView.setModel(self.node_model)
        self.ui.nodeTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        #self.select_model = self.node_model.selectionModel()
        #self.select_model = self.ui.nodeTreeView.selectionModel()
        
        self.ui.nodeTreeView.clicked.connect(self.tree_clicked)
        #self.select_model.selectionChanged.connect(self.tree_clicked)
        #self.ui.nodeTreeView.selectionChanged.connect(self.tree_clicked)
        
        # Event buttons
        self.ui.evButtonOff.clicked.connect(self.ev_clicked_off)
        self.ui.evButtonOn.clicked.connect(self.ev_clicked_on)
        
        # Last Event that was selected - use for On/Off buttons
        # has (Node, EVid, EVNum) - num added to make it easier
        self.selected_ev = None
        
        self.setCentralWidget(self.ui)
        self.ui.nodeTreeView.show()
        self.show()
        self.create_console()
    
        # Initial discover request
        self.discover()
        
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
        #print ("Checking for zmq updates")
        # Only allow one check_responses thread to run at a time
        if self.update_in_progress == True:
            #print ("Still running - skipping")
            return
        
        worker = Worker(self.thread_getupdate, self.newdata_loaded_signal, self.node_updated_signal)
        self.threadpool.start(worker)
        #print ("thread started")
            # Pass the response to the gui console
            ###self.console_window.add_log(text_response)
            # Check if we need to handle this further
            ###self.handle_incoming (text_response)
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
        
        #self.ui.nodeTable.setItem(0,0, QTableWidgetItem("Test 0 0"))
        
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
    def handle_incoming_data (self, response):
        # pass to console (unparsed)
        self.console_window.add_log(response)
        # strip date off (don't need except for the log)
        print (f"Entry {response}")
        date_data = response.split(',',2)
        vlcb_entry = self.vlcb.parse_input(date_data[1])
        # If not a valid entry then ignore
        if vlcb_entry == False:
            return
        # Look for specific responses
        # todo - should we check timestamp first? If the entry is from before the first request then may not be
        # interested as it's an old node. Alternatively we could load anyway (max 100 past entries are stored)
        # or we could not retrieve any previous messages by first checking for -1 entries and using that for
        # the start value
        # For now we handle all responses including old ones - but check for whether there are any changes
        if vlcb_entry.opcode() == 'PNN':    # PNN (Response to query node)
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
                # Add to Tree View
                print ("Adding entry")
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
        elif vlcb_entry.opcode() == 'NUMEV':    # Number of configured events
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not data_entry['NN'] in self.nodes.keys():
                print (f"NUMV response from Unknown node {data_entry['NN']}")
                return
            # Update node with evnum value
            self.nodes[data_entry['NN']].set_numev(data_entry['NumEvents'])
        elif vlcb_entry.opcode() == 'EVNLF':    # Number of event space left in node
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not data_entry['NN'] in self.nodes.keys():
                print (f"EVNLF response from Unknown node {data_entry['NN']}")
                return
            # Update node with evnum value
            self.nodes[data_entry['NN']].set_evspc(data_entry['EVSPC'])
            # Add a query for the next discovery stage - get a list of all the events
            self.discover_nerd (data_entry['NN'])
        elif vlcb_entry.opcode() == 'ENRSP':
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not data_entry['NN'] in self.nodes.keys():
                print (f"ENRSP response from Unknown node {data_entry['NN']}")
                return
            # Add event to node
            print (f"Adding to {data_entry['NN']}, Ev {data_entry['EnIndex']}, Name {data_entry['En3_0']:#08x}")
            self.nodes[data_entry['NN']].add_ev(data_entry['EnIndex'], data_entry['En3_0'])
            
            
            
            
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
        if type != "":
            request = type + "," + request
            
        #print (f"Request is {request}")
        #print (f"Current queue {self.send_queue}")
            
        # Priority ignores list length and just inserts at front
        # pushes other priority items further down the list as well
        if priority:
            self.send_queue.insert(0, request)
        # only add to the list if <= 10 items alread
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
    # Query ZMQ - get data
    # If from USB notify newdata
    # If update to node / events then update nodes and
    # notify updatenode
    def thread_getupdate(self, nodes, newdata_emit=None, updatenode_emit=None):
        #print ("Thread getupdate")
        #Only allow one thread at a time
        self.update_in_progress = True
        
        # check there is no message waiting to receive first
        # Should not get this, but prevents being stuck in loop of failed sends
        #response = self.receive(retry=0)
        #if response != "":
        #    print (f"Unexpected message {response}")
        
        # see if there is a specific requst
        request = self.get_request()
        if request != False:
            #print (f"Sending request {request}")
            response = self.send_receive (request)
            # Todo handle response
            # clear send_request ready for next request
            
        
        # Send a normal pole request
        request = f'get,{self.last_packet}'
        #print (f"Requesting {request}")
        response = self.send_receive (request)
        # Check for an empty data first as we can ignore
        if response[0:8] == "data,0,0":
            # No new data received
            pass
        # Check response starts with "data,"
        elif response[0:5] == "data,":
            #print (f'received {response}')
            # get start and end values for data
            data_retrieved = response.split(',', 3)
            # need end to know what our last stored value is
            this_last_packet = int(data_retrieved[2])
            if self.last_packet < this_last_packet:
                self.last_packet = this_last_packet
            data_packets = data_retrieved[3].split('\n')
            for data_packet in data_packets:
                if len(data_packet) < 5:    # If data too short (perhaps \n)
                    continue
                #self.data_received += 1    # Count packets received (not needed instead trust last packet number)
                self.handle_incoming_data(data_packet)
            self.newdata_loaded_signal.emit()
        else:
            print (f"Unrecognised response {response}")
        
        self.update_in_progress = False
        
    def send_receive(self, request_string):
        request = request_string.encode('utf-8')
        # todo add error handing
        self.socket.send(request)
        #print ("message sent")
        return self.receive()
        
    # retry is the number of times to retry connection
    def receive (self, retry=100):
        if retry < 1:
            retry = 1
        for i in range (0, retry):
            try:
                message = self.socket.recv(flags=zmq.NOBLOCK)
                message = message.decode("utf-8")
            except zmq.Again as e:
                #print ("No data")
                #continue
                pass
            except Exception as e:
                print (f"Unknown receive error {e}")
                continue
            else:
                #print (f"Message is {message}")
                return message
            # Temp using time sleep 
            # todo time sleep could be replaced with new timer
            if retry > 1:
                time.sleep (0.1)
        return ""
        
        
class Worker (QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    @Slot() # Pyside6.QtCore.Slot
    def run(self):
        self.fn(*self.args, **self.kwargs)
