from flask import Flask
import threading
from vlcbserver.canusb import CanUSB4
from datetime import datetime
import time
import vlcbserver
from vlcbserver import create_app
import vlcbserver.requests


port = '/dev/ttyACM0'

# maximum number of entries to cache in server
# Will exceed this, but this is the trim level
# ie if we exceed max_entries we will trim to this level
# on each event loop
max_entries = 100




def flaskThread():
    app.run(host='0.0.0.0', port=5000)
    
# Setup pixel strip and then start the updatePixels loop
def mainThread():
    while True:
        # Entire thread is in a loop which allows us to keep trying connection etc.
        debug = False
        
        # Connect to USB
        usb = CanUSB4(port)
        try:
            usb.connect()
        except:
            if debug:
                print (f"Error connecting to {port}")
            # At the moment stop - perhaps update in future
            break

        while True:
            # First part of loop - clear out any excessive entries
            # do now rather than each time we add something
            if (len(vlcbserver.data) > max_entries):
                num_pop = len(vlcbserver.data) - max_entries
                del vlcbserver.data[0:num_pop]
                vlcbserver.data_index += num_pop
            #print (f"Len data post {len(data)} index {data_index}")
                
            
            ### Check to see if we have any outgoing messages
            # prioritise sending
            while (len(vlcbserver.messages) > 0):
                this_message = vlcbserver.messages.pop(0)
                usb.send_data(this_message)
                # Add it to the data
                vlcbserver.data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ",o," + this_message)
                
            # in_data is a list of data
            # first entry [0] is the number entries - if negative then error
            in_data = usb.read_data()
            
            # If no data then slight pause and try loop again
            if in_data[0] == 0:
                time.sleep(0.1)
                #time.sleep (1)
            elif in_data[0] < 1:
                print (f"Error {in_data[1]}, {in_data[2]}")
            # Also check that the number of bytes is same as returned entry
            # Shouldn't get this, but additional check
            # Just warn then use the actual length of the error
            if (len(in_data) -1 != in_data[0]):
                print (f"Warning incorrect data returned, expected {in_data[0]}, received {len(in_data) - 1}")
            
            # If reach then at least 1 packet received
            for i in range(1, len(in_data)):
                this_input = in_data[i]
                #data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "," + this_input.decode('utf-8'))
                # date, i(incoming rather than o), data_string
                vlcbserver.data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ",i," + this_input)
                if debug:
                    print (f"Received {this_input}")
            # Todo Handle errors
            

app = create_app()
#pixels = Pixels(default_config_filename, custom_config_filename, custom_light_config_filename)

if __name__ == "__main__":
    # run as two threads - main thread and flask thread
    mt = threading.Thread(target=mainThread)
    ft = threading.Thread(target=flaskThread)
    mt.start()
    ft.start()