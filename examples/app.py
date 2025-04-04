from multiprocessing import Lock, Process, Queue, current_process
import time
import queue # imported for using queue.Empty exception
from canusb import CanUSB4

port = '/dev/ttyACM0'

def run_server(requests, responses, commands, status):
    # Entire thread is in a loop which allows us to keep trying connection etc.
    while True:
        # Connect to USB
        usb = CanUSB4(port)
        try:
            usb.connect()
        except:
            print (f"Error connecting to {port}")
            time.sleep(0.5)
            continue
    
        while True:
            # First check if any commands to the server 
            try:
                command = commands.get_nowait()
            except queue.Empty:
                pass
            else:
                # Handle commands here
                if command == "quit" or command == "exit":
                    print ("Exiting")
                    return True
            
            # Check to see if we have any responses
            # Do this clear input queue before sending any new requests
            in_data = usb.read_data()
            
            if in_data[0] == "Data":
                responses.put(in_data)
                print (f"Received {in_data[1]}")
                # If got data then keep on reading more
                continue
            # Todo Handle errors
            
            # Do we have a request?
            # If so send it now
            try:
                request = requests.get_nowait()
            except queue.Empty:
                pass
            else:
                print(f"Sending {request}")
                usb.send_data(request)


def main():
    requests = Queue()
    responses = Queue()   # Typically these are responses to requests, but could be error / not connected
    commands = Queue()    # These are commands to the server - eg. shutdown / connect on new port
    status = Queue()      # Response to commands and/or error messages with CANUSB4

    # create processes
    vlcbserver = Process(target=run_server, args=(requests, responses, commands, status))
    vlcbserver.start()
    
    requests.put(b':SB780N0D;')
    time.sleep(10)
    commands.put("exit")

    vlcbserver.join()

    return True


if __name__ == '__main__':
    main()