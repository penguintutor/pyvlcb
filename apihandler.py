from PySide6.QtCore import Qt, QTimer, QObject, QThreadPool, QRunnable
from worker import Worker
from eventbus import EventBus, event_bus
from devicemodel import DeviceModel, device_model
from pyvlcb import VLCB
from vlcbformat import VLCBopcode
from vlcbnode import VLCBNode
from vlcbclient import VLCBClient
from appevent import AppEvent


# Todo mw is used for layout - can this be decoupled
# same with mw.control_loco - should that be moved to device_model?

class ApiHandler(QObject):
    def __init__(self, mw, thread_pool: QThreadPool, url):
        super().__init__()
        self.threadpool = thread_pool
        self.mw = mw
        self.url = url
        # Subscribe to commands from the GUI/App logic
        #event_bus.set_device_power_command.connect(self._handle_set_power_command)
        
        # Keep alive timer must run on mainwindow and must be started / stopped using signals
        
        
        self.debug = False
        
        # Queue to hold commands as they are sent from the queue
        self.send_queue = []

        self.update_in_progress = False
        
        # The class is called client, but as it's used to communicate
        # with the server it's referred to in this as self.server
        self.server = VLCBClient(self.url)
        
        # Add request to be sent next time timer expires
        #self.send_queue = []
        self.pc_can_id = 60      # CAN ID of CANUSB4
        
        # Current position in server log entries and amount of data received
        # If -1 will try and get all including old entries
        # If None just get the last few packets received (effectively start from current instead of history)
        # None is -5 to ensure see the initial discover
        self.last_packet = None
        #self.data_received = None
        
        # VLCB and node creation
        self.vlcb = VLCB(self.pc_can_id)

        
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
    
    # Places request onwait list
    # type is what kind of command to prepend with - eg. send (for cbus) or server etc.
    # comma is added automatically
    # set to "" if already formatted
    # Adding priority pushes to front of queue
    def start_request (self, request, type="send", priority=False):
        # add type to request
        #print (f"Starting request {request}")
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

        
    # Use for sending multiple requests (needed for some messages)
    # Sent every 2 seconds (or change delay) - delay in seconds
    # Send num_send times
    def start_request_repeat (self, request, num_send = 1, delay = 2):
        self.start_request(request)
        num_send -= 1
        if num_send > 0:
            QTimer.singleShot(delay * 1000, lambda: self.start_request_repeat(request, num_send, delay))


    # Used for trigger commands where on is sent folloewd by off
    # Sends on followed by off (typically 4 seconds later)
    def start_request_onoff (self, request_on, request_off, delay = 4):
        # Turn on
        self.start_request(request_on)
        # Turn off after delay
        # Don't check for None returned as if it worked before should be no reason for it to fail now
        QTimer.singleShot(delay * 1000, lambda: self.start_request(request_off)) 


    # Run in thread
    # Query web - get data
    # If from web notify newdata
    # If update to node / events then update nodes and
    # notify updatenode
    def thread_getupdate(self):
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
            
        #print ("Reading response")
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
                self.handle_incoming_data(data_packet)
        else:
            print (f"Unrecognised response {response}")
        self.update_in_progress = False


    def poll_server(self):
        # Only allow one check_responses thread to run at a time
        if self.update_in_progress == True:
            #print ("Still running - skipping")
            return
        
        worker = Worker(self.thread_getupdate)
        self.threadpool.start(worker)
        return
    
    def handle_incoming_data (self, response):
        
        if self.debug:
            print (f"Incoming data {response}")
            
        # pass to console (unparsed)
        event_bus.publish(AppEvent("newdata", {"response":response}))
        
        # strip date off (don't need except for the log)
        id_date_data = response.split(',',3)
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
            if not device_model.node_exists(data_entry['NN']):
                device_model.add_node(VLCBNode(data_entry['NN'], mode, vlcb_entry.can_id, data_entry['ManufId'], data_entry['ModId'] ,data_entry['Flags']))
                #device_model.set_name(data_entry['NN'], self.mw.layout.node_name(data_entry['NN']))
                # Add to Tree View
                # todo review where / how node_model is updated
                self.mw.node_model.appendRow(device_model.get_gui_node(data_entry['NN']))
            else:
                # Update existing entry
                items_changed = device_model.update_node(data_entry['NN'], {'Mode': mode, 'ManfId': data_entry['ManufId'], 'ModId': data_entry['ModId'], 'Flags': data_entry['Flags']})
                # If no items changed then no need to check for further updates
                if items_changed == 0:
                    return
                # Node is updated as part of update_node - so next block of text not reqired
            # If this is new, or has changed then we can also get the number of events
            self.discover_evn (data_entry['NN'])
        elif ret_opcode == 'NUMEV':    # Number of configured events
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not device_model.node_exists(data_entry['NN']):
                print (f"NUMV response from Unknown node {data_entry['NN']}")
                return
            # Update node with evnum value
            device_model.set_numev(data_entry['NN'], data_entry['NumEvents'])
            #self.nodes[data_entry['NN']].set_numev(data_entry['NumEvents'])
        elif ret_opcode == 'EVNLF':    # Number of event space left in node
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not device_model.node_exists(data_entry['NN']):
                print (f"EVNLF response from Unknown node {data_entry['NN']}")
                return
            # Update node with evnum value
            device_model.set_evspc(data_entry['NN'], data_entry['EVSPC'])
            # Add a query for the next discovery stage - get a list of all the events
            self.discover_nerd (data_entry['NN'])
        elif ret_opcode == 'ENRSP':    # EV discovery
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # If we don't already have this node then didn't see a PNN response - so likely error
            if not device_model.node_exists(data_entry['NN']):
                # Most likely reason is connected to existing server with old entries
                # So ignore unless debug
                if self.debug:
                    print (f"ENRSP response from Unknown node {data_entry['NN']}")
                return
            # Add event to node
            device_model.add_ev(data_entry['NN'], data_entry['EnIndex'], data_entry['En3_0'])
            #device_model.update_ev(data_entry['NN'], data_entry['EnIndex'], "name", self.mw.layout.ev_name(data_entry['NN'], data_entry['EnIndex'], data_entry['En3_0']))
        # Indicates allocation of loco - need to verify this is expected
        elif ret_opcode == 'PLOC':
            # Must be in status 'rloc' or 'gloc' - otherwise ignore as we are not waiting on plooc
            if self.mw.control_loco.is_aquiring() == False:
                return
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            # Session,AddrHigh_AddrLow,SpeedDir,Fn1,Fn2,Fn3'
            loco_id = data_entry['AddrHigh_AddrLow'] & 0x3FFF
            if self.mw.control_loco.get_id() != loco_id:
                # If it doesn't match then perhaps this was for a different controller
                # Or could be we haven't allocated yet
                if self.debug:
                    print (f"PLOC ID {loco_id} does not match current Loco ID {self.mw.control_loco.get_id()}")
                return
            # Update loco with session, speed and direction
            self.mw.control_loco.set_session (data_entry['Session'])
            self.mw.control_loco.set_speeddir (data_entry['SpeedDir'])
            self.mw.control_loco.set_functions (data_entry['Fn1'], data_entry['Fn2'], data_entry['Fn3'])
            #self.mw.ui.locoStatusLabel.setText ("Ready")
            event_bus.publish(AppEvent("uitext", {'label': "locoStatusLabel", 'value': "Ready"}))
            # Set status to on last gives time to ensure all entries updated
            self.mw.control_loco.set_status ("on")
            # Todo update controller with new values
            self.mw.update_lcd ()
            # Start the keepalive timer
            #self.mw.update_kalive_signal.emit()
            event_bus.publish(AppEvent("keepalive", {}))
        # ERR is error from DCC controller - eg. problem aquiring loco
        elif ret_opcode == 'ERR':
            if self.debug:
                print ("Error message received")
            # Depending upon the error code the data may have different interpretations
            # Stored as Byte1, Byte2, ErrCode - where Byte1,Byte2 may eqal AddrHigh_AddrLow, or
            # may be Byte1 = Session ID, Byte 2 = 0
            # So only check after looking at the ErrCode
            data_entry = VLCBopcode.parse_data(vlcb_entry.data)
            #loco_id = data_entry['AddrHigh_AddrLow'] & 0x3FFF
            # Check error code relates to the current loco
            if data_entry['ErrCode'] == 1:
                # Only valid during aquiring status
                if self.mw.control_loco.is_aquiring() == False:
                    if self.debug:
                        print ("Not aquiring loco - ignoring error")
                    return
                loco_id = VLCB.bytes_to_addr(data_entry['Byte1'],data_entry['Byte2']) & 0x3FFF
                if self.mw.control_loco.get_id() != loco_id:
                    if self.debug:
                        print (f"ERR ID {loco_id} does not match current Loco ID {self.mw.control_loco.loco.loco_id}")
                    return
                #self.mw.ui.locoStatusLabel.setText ("Error - no sessions available")
                event_bus.publish(AppEvent("uitext", {'label': "locoStatusLabel", 'value': "Error - no sessions available"}))

            # Already taken - option to steal
            elif data_entry['ErrCode'] == 2:
                #Only for us if we haven't completed the session setup
                if self.mw.control_loco.get_status() == "on":
                    #print ("Not our session")
                    return
                elif self.mw.control_loco.is_aquiring() == False:
                    #print ("Not aquiring session")
                    return
                loco_id = VLCB.bytes_to_addr(data_entry['Byte1'],data_entry['Byte2']) & 0x3FFF
                if self.debug:
                    print ("Error code 2 - loco taken")
                if self.mw.control_loco.get_id() != loco_id:
                    if self.debug:
                        print (f"ERR ID {loco_id} does not match current Loco ID {self.control_loco.get_id()}")
                    return
                
                event_bus.publish(AppEvent("uitext", {'label': "locoStatusLabel", 'value': "Error - address taken"}))
                #self.mw.ui.locoStatusLabel.setText ("Error - address taken")
                event_bus.publish(AppEvent("stealdialog", {'loco_id': loco_id}))
                #self.mw.steal_dialog_signal.emit(loco_id)
            elif data_entry['ErrCode'] == 8:
                # If we are trying to aquire a session then this could be us resetting other node
                if self.mw.control_loco.is_aquiring():
                    return
                # byte 1 is now sessionid - byte2 is ignored - should be 00
                session_id = int(data_entry['Byte1'])
                # if not our current session_id then could be for a different controller so ignore
                if session_id != 0 and session_id == self.control_loco.get_session():
                    if self.debug:
                        print (f"Session cancelled {session_id}")
                    # This updates the loco and the GUI
                    self.reset_loco()
                else:
                    if self.debug:
                        print (f"Session not cancelled {session_id}, loco session {self.control_loco.get_session()}")


    
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
        
        # change value (if need to send multiple then set num_send to number of times
    # Sent every 2 seconds (or change delay) - delay in seconds
    def loco_func_change (self, func_index, value, num_send = 1, delay = 2):
        byte1_2 = self.mw.control_loco.set_function_dfun (func_index, value)
        # If None then cancel
        if byte1_2 == None:
            return
        request = self.vlcb.loco_set_dfun(self.mw.control_loco.get_session(), *byte1_2)
        self.start_request_repeat (request, num_send, delay)
    
    # Sends on followed by off (typically 4 seconds later)
    def loco_func_trigger (self, func_index, delay = 4):
        #print (f"Func trigger api {func_index}")
        # Turn on
        byte1_2 = self.mw.control_loco.set_function_dfun (func_index, 1)
        if byte1_2 == None:
            return
        request_on = self.vlcb.loco_set_dfun(self.mw.control_loco.get_session(), *byte1_2)
        # Turn off (update value immediately - even though not sent yet, but delay request using single shot timer
        byte1_2 = self.mw.control_loco.set_function_dfun (func_index, 0)
        request_off = self.vlcb.loco_set_dfun(self.mw.control_loco.get_session(), *byte1_2)
        
        self.start_request_onoff (request_on, request_off, delay)
        