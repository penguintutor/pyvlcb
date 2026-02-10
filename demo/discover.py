#!/usr/bin/env python3
""" Example code showing how to send commands using VLCB and CanUSB4
This example performs a discover looking for devices on the
CANBus. Example uses typical Raspberry Pi USB port used for CanUSB4.
"""

from pyvlcb import *
import time

# Typical USB port - change as required
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
    # 100 checks for data - arbitary figure to allow for reasonable delay
    for i in range (0, 100):
        # in_data is a list of data
        # first entry [0] is the number entries - if negative then error
        in_data = usb.read_data()
        
        # If no data then slight pause and try loop again
        if len(in_data) < 1:
            time.sleep(0.1)
            continue
            
        # If reach then at least 1 packet received
        for i in range(0, len(in_data)):
            this_input = in_data[i]
            # Parse the response
            try:
                response = vlcb.parse_input (this_input)
                print (f"Received {this_input} : {response}")
            except:
                print (f"Invalid response")
            
    
    
    print ("Finished")


if __name__ == "__main__":
    main()