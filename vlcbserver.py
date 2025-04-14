# Main App class - handles connection to canusb and creates zmq
# This is a very basic zmq server
# Receives data from usb and sends to higher when requested
# Receives request from zmq and sends to USB
# higher level needs to interpret the data

from multiprocessing import Lock, Process, Queue, current_process
from canusb import CanUSB4
from datetime import datetime
import zmq


port = '/dev/ttyACM0'
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# maximum number of entries to cache in server
# Will exceed this, but this is the trim level
# ie if we exceed max_entries we will trim to this level
# on each event loop
max_entries = 100

# List containing data received
data = []
data_index = 0 # index number for first entry in array
# eg. if 10 entries removed from start then this will be increased to 10 and
# new entries will be relative to that

print ("Starting server")

while True:
    # Entire thread is in a loop which allows us to keep trying connection etc.
    debug = True
    
    # Connect to USB
    usb = CanUSB4(port)
    try:
        usb.connect()
    except:
        if debug:
            print (f"Error connecting to {port}")
        # At the moment stop - perhaps update in future
        break
        #time.sleep(0.5)
        #continue

    while True:
        
        #print (f"Len data pre {len(data)} index {data_index}")
        # First part of loop - clear out any excessive entries
        # do now rather than each time we add something
        if (len(data) > max_entries):
            num_pop = len(data) - max_entries
            del data[0:num_pop]
            data_index += num_pop
        #print (f"Len data post {len(data)} index {data_index}")
            
        
        # First check if any commands to the server 
        try:
            message = socket.recv(flags=zmq.NOBLOCK)
            #print (f"Raw message {message}")
            if (message != b''):
                message = message.decode("utf-8")
            else:
                message = ""
            
        except zmq.Again as e:
            #print ("Nothing received")
            # Nothing received
            pass
        except Exception as e:
            print (f"Unknown error {e}")
        else:
            #print (f"Request received {message}")
            # If empty request
            if message == "":
                #print ("Sending emptyrequest")
                socket.send(b'status,emptyrequest')
            # Handle commands here
            elif message[0:7] == "server,":
                print ("Server message")
                #if message[7:] == "quit"
                #    socket.send(b"server,quit")
                #    if debug:
                #        print ("Exiting")
                #    break
                # Status responsds with status,firstdata,numdata
                if message[7:] == "status":
                    status_msg = f"status,{data_index},{len(data)}"
                    #print (f"Status sending {status_msg}")
                    socket.send(status_msg.encode("utf-8"))
                else:
                    print ("Unknown server request")
                    socket.send(b'status,unknownserverreq')
            # send,<data> - send to usb
            elif message[0:5] == "send,":
                send_data = message[5:].encode('utf-8')
                print (f"send request is {message[5:]}") 
                usb.send_data(send_data)
                data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "," + send_data.decode('utf-8'))
            #    print ("Returning : sent")
                socket.send(b"sent")
            # get,start_num (to end) (May be long)
            # get,start_num,num_packets (fixed range)
            # get,-num (last x packets)
            elif message[0:4] == "get,":
                #print (f"Get request {message[4:]}")
                message_req = message[4:].split(',')
                data_string = "data,"
                num_entries_returned = 0    # Just used for testing, could be used for a checksum
                ## todo - add handling of other types of entry
                if len(message_req) >= 1:
                    start_pos = int(message_req[0])
                    # If forward
                    if start_pos >= 0:
                        # Subtract data_index from start_pos
                        start_pos -= data_index
                        # If start is before start of log (eg. request all, but already removed some entries)
                        if start_pos < 0:
                            start_pos = 0
                        # Assuming forward we now now our start_pos
                        # If only one value then go to end
                        if len(message_req) < 2:
                            end_pos = len(data)
                        # otherwise set end to appropriate value
                        # note that the num entries always starts at start_pos - so if start_pos is moved to higher value
                        # then it's relative to that - most likely this is what is required (ie. num_entries is to limit
                        # number of packets received) - if for other reason then client needs to check start and end of what is returned
                        else:
                            end_pos = int(message_req[1]) + start_pos + 1
                            # check we aren't going beyond the end - if so limit to end
                            if end_pos > len(data):
                                end_pos = len(data)

                    # if start negative (backwards)
                    else:
                        # Note add because start_pos is negative
                        start_pos = len(data) + start_pos -1
                        # Negative start - always goes to end
                        
                    #print (f"Start {start_pos}, end {end_pos}, index {data_index}, len {len(data)}")
                    
                    # Add start and end positions to the response so that the caller knows what these
                    # refer to. Particularly important when requesting from before
                    # typically the client will be more concerned about the second value
                    # end does not need -1 as it's total packets received
                    data_string += f"{start_pos+data_index},{end_pos+data_index},"
                    for i in range (start_pos, end_pos):
                        num_entries_returned += 1
                        data_string += data[i]+"\n"
                    # If no data added
                    # replace with a nodata response
                    if num_entries_returned < 1:
                        socket.send(b"data,0,0")
                        #print ("No data to return")
                    else:
                        #print (f"Sending {num_entries_returned} entries")
                        #print (f"Sending {data_string.encode('utf-8')}")
                        socket.send(data_string.encode('utf-8'))

        
        # Check to see if we have any responses
        # Do this clear input queue before sending any new requests
        in_data = usb.read_data()
        
        if in_data[0] == "Data":
            data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "," + in_data[1].decode('utf-8'))
            if debug:
                print (f"Received {in_data[1]}")
            # If got data then keep on reading more
            continue
        # Todo Handle errors
        


print ("Connection closed")