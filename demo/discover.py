#!/usr/bin/env python3

from pyvlcb import *
import time

port = '/dev/ttyACM0'


def main ():
    # Create vlcb object to query for strings
    vlcb = VLCB()
    # Connect to USB
    usb = CanUSB4(port)
    try:
        usb.connect()
    except:
        print (f"Error connecting to {port}")
        # At the moment stop - perhaps update in future
        return
    
    # Issue a discover packet
    discover_req = vlcb.discover()
    usb.send_data (discover_req)
    
    print ("Sending discover")
    print (f"Sent {discover_req}")
    
    # Print a header entry
    print ("Raw resp       : Priority : Can ID : OpCode (Hex) : Data / (dict)")
    
    # Read back data
    # 100 checks for data
    for i in range (0, 100):
        # in_data is a list of data
        # first entry [0] is the number entries - if negative then error
        in_data = usb.read_data()
        
        # If no data then slight pause and try loop again
        if in_data[0] == 0:
            time.sleep(0.1)
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
            # date, i(incoming rather than o), data_string
            #print (f"Raw data {this_input}")
            # format using parse_data
            print (f"{this_input} : {vlcb.parse_input (this_input)}")
    
    
    print ("Finished")


if __name__ == "__main__":
    main()