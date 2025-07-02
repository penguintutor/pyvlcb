from PySide6.QtCore import Qt, QTimer, QObject, QThreadPool, QRunnable
from worker import Worker
from vlcbclient import VLCBClient

url = "http://127.0.0.1:5000/"

class ApiHandler(QObject):
    def __init__(self, mw, thread_pool: QThreadPool):
        super().__init__()
        self.threadpool = thread_pool
        self.mw = mw
        # Subscribe to commands from the GUI/App logic
        #event_bus.set_device_power_command.connect(self._handle_set_power_command)
        
        # Queue to hold commands as they are sent from the queue
        self.send_queue = []

        self.update_in_progress = False
        
        # The class is called client, but as it's used to communicate
        # with the server it's referred to in this as self.server
        self.server = VLCBClient(url)
        
        # Add request to be sent next time timer expires
        #self.send_queue = []
        
        # Current position in server log entries and amount of data received
        # If -1 will try and get all including old entries
        # If None just get the last few packets received (effectively start from current instead of history)
        # None is -5 to ensure see the initial discover
        self.last_packet = None
        #self.data_received = None

        
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
                self.mw.handle_incoming_data(data_packet)
            self.mw.newdata_loaded_signal.emit()
        else:
            print (f"Unrecognised response {response}")
        
        self.update_in_progress = False


    def poll_server(self):
        # Only allow one check_responses thread to run at a time
        if self.update_in_progress == True:
            #print ("Still running - skipping")
            return
        
        worker = Worker(self.thread_getupdate, self.mw.newdata_loaded_signal, self.mw.node_updated_signal)
        self.threadpool.start(worker)
        return


#     def _handle_set_power_command(self, command: SetDevicePowerCommand):
#         print(f"API Handler: Received command to set power for {command.device_id} to {command.power_on}")
#         worker = DevicePowerSetter(command.device_id, command.power_on)
#         self.threadpool.start(worker) # Execute API call in a worker thread
# 
#     def shutdown(self):
#         self.device_a_feeder.stop()
#         # Wait for threads to finish if necessary (QThreadPool.waitForDone())
#         # but in many GUI apps, just stopping feeders is enough.
