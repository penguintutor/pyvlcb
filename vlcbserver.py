# Main App class - handles connection to canusb and creates zmq
# This is a very basic zmq server
# Receives data from usb and sends to higher when requested
# Receives request from zmq and sends to USB
# higher level needs to interpret the data

from multiprocessing import Lock, Process, Queue, current_process
from canusb import CanUSB4
import zmq


port = '/dev/ttyACM0'
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

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
        #if debug:
        #    print ("App event loop")
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
            print (f"Request received {message}")
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
                data.append(send_data.decode('utf-8'))
            #    print ("Returning : sent")
                socket.send(b"sent")
            # get,start_num (to end) (May be long)
            # get,start_num,num_packets (fixed range)
            # get,-num (last x packets)
            elif message[0:4] == "get,":
            #    print (f"Get request {message[4:]}")
                message_req = message[4:].split(',')
                data_string = "data,"
                num_entries_returned = 0    # Just used for testing, could be used for a checksum 
                if len(message_req) == 1:
                    for i in range (int(message_req[0])-data_index, len(data)):
                        num_entries_returned += 1
                        data_string += data[i]+"\n"
                    # If no data added
                    if data_string == "data,":
                        socket.send(b"nodata")
                        print ("No data to return")
                    else:
                        #print (f"Sending {num_entries_returned} entries")
                        socket.send(data_string.encode('utf-8'))

        
        # Check to see if we have any responses
        # Do this clear input queue before sending any new requests
        in_data = usb.read_data()
        
        if in_data[0] == "Data":
            data.append(in_data[1].decode('utf-8'))
            if debug:
                print (f"Received {in_data[1]}")
            # If got data then keep on reading more
            continue
        # Todo Handle errors
        
        # Do we have a request?
        # If so send it now
        #try:
        #    request = requests.get_nowait()
        #except queue.Empty:
        #    pass
        #else:
        #    if debug:
        #        print(f"Sending {request}")
        #    usb.send_data(request)

print ("Connection closed")