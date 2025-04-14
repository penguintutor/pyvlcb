import os
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal, Slot, QThreadPool, QRunnable
from PySide6.QtWidgets import QMainWindow, QTextBrowser
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
        # Todo - remove this - temp for testing
        # This will slow startup
        #time.sleep(1)
        
        # VLCB and node creation
        self.vlcb = VLCB()
        
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
        
        self.setCentralWidget(self.ui)
        self.ui.nodeTreeView.show()
        self.show()
        self.create_console()
    
        # Initial discover request
        self.discover()
        
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
        if vlcb_entry.opcode() == 'PNN':    # PNN (Response to query node)
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # if we don't already have this device add it
            if not data_entry['NN'] in self.nodes.keys():
                self.nodes[data_entry['NN']] = VLCBNode(data_entry['NN'], data_entry['ManufId'], data_entry['ModId'] ,data_entry['Flags'])
                # Add to Tree View
                print ("Adding entry")
                node = QStandardItem(f"Unknown, {data_entry['NN']}, {vlcb_entry.can_id}")
                self.node_model.appendRow(node)
                
            else:
                # Update existing entry
                pass
            
    # Initial discover of modules    
    def discover (self):
        self.start_request(self.vlcb.discover())
        
    # 2nd phase in discovery RQEVN = 
    def discover_evn (self):
        pass
    
    # Places request onwait list
    # type is what kind of command to prepend with - eg. send (for cbus) or server etc.
    # comma is added automatically
    # set to "" if already formatted
    # Adding priority pushes to front of queue
    def start_request (self, request, type="send", priority=False):
        # add type to request
        if type != "":
            request = type + "," + request
            
        print (f"Request is {request}")
        print (f"Current queue {self.send_queue}")
            
        # Priority ignores list length and just inserts at front
        # pushes other priority items further down the list as well
        if priority:
            self.send_queue.insert(0, request)
        # only add to the list if <= 10 items alread
        if len(self.send_queue) > 10:
            return False
        self.send_queue.append(request)
        print (f"New queue {self.send_queue}")
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
            print (f"Sending request {request}")
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
            print (f'received {response}')
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
