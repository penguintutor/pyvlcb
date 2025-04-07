# Main App class - handles connection to canusb and creates automate process

from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception
from canusb import CanUSB4
from vlcbautomate import VLCBAutomate

port = '/dev/ttyACM0'

# Handle events passes data to/from CanUSB4 and the automate process
def handle_events(requests, responses, commands, status):
    # Entire thread is in a loop which allows us to keep trying connection etc.
    debug = True
    
    # Connect to USB
    usb = CanUSB4(port)
    try:
        usb.connect()
    except:
        if debug:
            print (f"Error connecting to {port}")
        return
        #time.sleep(0.5)
        #continue

    while True:
        #if debug:
        #    print ("App event loop")
        # First check if any commands to the server 
        try:
            command = commands.get_nowait()
        except queue.Empty:
            pass
        else:
            # Handle commands here
            if command == "quit" or command == "exit":
                if debug:
                    print ("Exiting")
                return True
        
        # Check to see if we have any responses
        # Do this clear input queue before sending any new requests
        in_data = usb.read_data()
        
        if in_data[0] == "Data":
            responses.put(in_data[1])
            if debug:
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
            if debug:
                print(f"Sending {request}")
            usb.send_data(request)

# Starts the automation process
def start_automation(requests, responses, commands, status):
    automate = VLCBAutomate(requests, responses, commands, status)
    automate.run()
    

def main():
    requests = Queue()
    responses = Queue()   # Typically these are responses to requests, but could be error / not connected
    commands = Queue()    # These are commands to the server - eg. shutdown / connect on new port
    status = Queue()      # Response to commands and/or error messages with CANUSB4

    # create processes
    # process for handling events
    event_process = Process(target=handle_events, args=(requests, responses, commands, status))
    # process for automation (which in turn creates the gui)
    automation = Process(target=start_automation, args=(requests, responses, commands, status))
    event_process.start()
    automation.start()
    print ("Automation started")
    
    #requests.put(b':SB780N0D;')
    #time.sleep(10)
    #commands.put("exit")

    event_process.join()
    automation.join()

    return True


if __name__ == '__main__':
    main()