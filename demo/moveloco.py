#!/usr/bin/env python3

""" Example code to move a loco for a short period of time
then stop it again.
Uses a typical port and loco ID 3 (often used for new locos)
Update as required for your own layout.
If loco has sound then it turns sound on (F1), triggers sound F3
(typically a whistle or horn) then moves loco before
turning sound off again.

For simplicity of understanding this is written as
sequential commands triggered using a state machine.
Due to the nature of different devices on the bus, and need for
keep alives (at least every 4 seconds) threading may be a better solution,
particularly if using a GUI application.
"""

from pyvlcb import *
import time

# Typical port for Raspberry Pi USB with CanUSB4
port = '/dev/ttyACM0'

# Set appropriate loco id
loco_id = 5754

def main ():
    
    # Use simple state machine to determine what commands to send
    state = "start"
    
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

    state = "allocating"

    # Allocate loco
    print (f"Attemping to allocate loco {loco_id}")
    command = vlcb.allocate_loco(loco_id)
    usb.send_data (command)
    print (f"Sent {command}")
    
    session = None # loco session_id (when allocated)
    functions = [] # Track functions set
    counter = 0    # Use when waiting (allows keep alive to continue) divide by 2 to get seconds
       
    # Read back data
    # 100 checks for data
    for i in range (0, 100):
        # If there is a session allocated then need to send a keep alive
        # otherwise the loco will expire. This should be every 4 seconds
        # So ideally any commands should have processing limit below
        # 3 seconds
        if session != None:
            #print ("Sending keep alive")
            command = vlcb.keep_alive(session)
            usb.send_data(command)
        
        
        # in_data is a list of data
        in_data = usb.read_data()
        
        # If no data then slight pause and try loop again
        #if len(in_data) < 1:
        #    time.sleep(0.1)
        #    continue
            
        # If reach here then at least 1 packet received
        # Iterate over the returned entries
        for i in range(0, len(in_data)):
            this_input = in_data[i]
            
            # Parse the response
            response = vlcb.parse_input (this_input)
            print (f"Received {this_input} : {response}")
            
            # Perform checks against specific packets
            # related to Loco - any others are ignored
            # Do we receive a PLOC
            if response.opcode() == "PLOC":
                # Check it's for our loco
                if response.get_loco_id() == loco_id:
                    print (f"Response data {response.data}")
                    data = response.get_data()
                    session = data.get("Session")
                    print (f"Loco session allocated {session}")
                    functions = response.get_function_list()
                    state = "allocated"
                else:
                    print (f"PLOC response for different loco - possibly another controller {reponse.get_loco_id()}")
            # Error - check it's for this allocate - but could be that the loco is already taken
            elif response.opcode() == "ERR":
                # This is an alternative to response.get_data()
                data = response.get_data()
                # ErrCode 2 = allocated - 
                if data.get("ErrCode") == 2:
                    print (f"Loco {response.get_loco_id()} is already allocated")
                    # Send a share command (could do steal instead by replacing share with steal
                    command = vlcb.share_loco(loco_id)
                    usb.send_data (command)
                    print (f"Sending share request {command}")

        # End of the check for opcodes
        if state == "allocated":
            # Send F1 on (normally turn on sound)
            functions[1] = 1
            command = vlcb.loco_set_function (session, 1, functions)
            usb.send_data (command)
            print (f"Sound on {command}")
            state = "soundon"
        elif state == "soundon":
            # Send F3 on (often whistle or horn)
            functions[3] = 1
            command = vlcb.loco_set_function (session, 3, functions)
            usb.send_data (command)
            print (f"Whistle {command}")
            state = "whistle"
            # allow send of keep alive before sending whistle off
        elif state == "whistle":
            functions[3] = 0
            command = vlcb.loco_set_function (session, 3, functions)
            usb.send_data (command)
            print (f"Whistle off {command}")
            state = "whistleoff"
        # Move the loco forward
        elif state == "whistleoff":
            speed = 36
            direction = 1 # 1 is forward, 0 is reverse
            command = vlcb.loco_speed_dir (session, speed, direction)
            usb.send_data (command)
            print (f"Forward speed {speed} - {command}")
            counter = 0
            state = "forward"
        elif state == "forward":
            # Only change when counter > 5 (approx 10 seconds)
            counter += 1
            if counter > 5:
                # stop loco (speed = 0)
                speed = 0
                direction = 1 # Direction irrelevant when stopping, but must say something
                command = vlcb.loco_speed_dir (session, speed, direction)
                usb.send_data (command)
                print (f"Stopping loco {command}")
                state = "stopped"
        elif state == "stopped":
            functions[1] = 0
            command = vlcb.loco_set_function (session, 1, functions)
            usb.send_data (command)
            print (f"Sound off {command}")
            state = "soundoff"
        elif state == "soundoff":
            # Release the loco
            command = vlcb.release_loco (session)
            usb.send_data (command)
            print (f"Loco release {command}")
            state = "end"
            break
                
        # Sleep for 2 seconds between commands
        # Not required but saves needing to track between keep alives - send keep alive every 2 seconds
        # This is outside of the receive packet check so that if multiple received they
        # are all handled before the sleep
        time.sleep(2)
        if state == "end":
            break
    
    print ("Finished")


if __name__ == "__main__":
    main()