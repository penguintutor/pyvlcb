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
        self.send_request = ""
        
        # Current position in server log entries and amount of data received
        self.data_received = 0
        
        # Create a timer to periodically check for updates
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.poll_server)
        self.timer.start()
        # Todo - remove this - temp for testing
        # This will slow startup
        time.sleep(1)
        
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
        print ("Checking for zmq updates")
        # Only allow one check_responses thread to run at a time
        if self.update_in_progress == True:
            print ("Still running - skipping")
            return
        
        worker = Worker(self.thread_getupdate, self.newdata_loaded_signal, self.node_updated_signal)
        self.threadpool.start(worker)
            # Pass the response to the gui console
            ###self.console_window.add_log(text_response)
            # Check if we need to handle this further
            ###self.handle_incoming (text_response)
            
        # Todo Handle errors
        
    def update_console (self):
        pass
    
    def update_nodes (self):
        pass
        
    # This method is called whenever we get a valid response
    # Used to determine if further action is required (eg. discovery or update status)
    # Note this will see all cbus messages, including ones sent to/from other nodes
    def handle_incoming_data (self, response):
        # pass to console (unparsed)
        self.console_window.add_log(response)
        vlcb_entry = self.vlcb.parse_input(response)
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
            
        
    def discover (self):
        self.start_request("send,"+self.vlcb.discover())
    
    # Places request onwait list
    def start_request (self, request):
        #worker = Worker(self.thread_sendrequest, request)
        #self.threadpool.start(worker)
        # only add to the list if nothing else already waiting
        if self.send_request != "":
            return False
        self.send_request = request
        return True
        
        
    # Send exit to automate as well as closing app
    def quit_app(self):
        QCoreApplication.quit()
        
    # Run in thread
    # Query ZMQ - get data
    # If from USB notify newdata
    # If update to node / events then update nodes and
    # notify updatenode
    def thread_getupdate(self, nodes, newdata_emit=None, updatenode_emit=None):
        print ("Thread getupdate")
        #Only allow one thread at a time
        self.update_in_progress = True
        
        # check there is no message waiting to receive first
        # Should not get this, but prevents being stuck in loop of failed sends
        #response = self.receive(retry=0)
        #if response != "":
        #    print (f"Unexpected message {response}")
        
        # see if there is a specific requst
        if self.send_request != "":
            print (f"Sending request {self.send_request}")
            response = self.send_receive (self.send_request)
            # Todo handle response
            # clear send_request ready for next request
            # Testing - if we need a lot of entries for testing then comment this out
            self.send_request = ""
        
        request = f'get,{self.data_received}'
        print (f"Requesting {request}")
        response = self.send_receive (request)
        # Todo handle response
        # Check response starts with "data,"
        if response[0:5] == "data,":
            data_packets = response[5:].split('\n')
            for data_packet in data_packets:
                if len(data_packet) < 5:    # If data too short (perhaps \n)
                    continue
                self.data_received += 1    # Count packets received
                self.handle_incoming_data(data_packet)
        else:
            print (f"Unrecognised response {response}")
        
        self.update_in_progress = False
        
    def send_receive(self, request_string):
        request = request_string.encode('utf-8')
        # todo add error handing
        self.socket.send(request)
        print ("message sent")
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
                print (f"Message is {message}")
                return message
            # Temp using time sleep 
            # todo time sleep could be replaced with new timer
            if retry > 1:
                time.sleep (0.2)
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
