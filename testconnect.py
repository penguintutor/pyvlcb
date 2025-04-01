#!/usr/bin/python3

import time
import serial
from pyvlcb import VLCB

vlcb = VLCB()

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)

print ("Writing")
ser.write(b':SB780N0D;')

#ser.write(b'SB000NB6FFFFA5090A;')

time.sleep(0.5)

print ("Wait on response")

#for i in range (0, 10):
#    input = ser.readline()
#    print ("Read input " + input.decode("utf-8") + " from USB")

in_string = b''
while True :
    this_char = ser.read(1)
    #print ("This char "+this_char.decode("utf-8"))
    if this_char == b'':
        time.sleep(0.5)
        continue
    elif this_char == b';':
        message = vlcb.parse_input(in_string)
        print (message)
        print ("")
        
        
        #print ("Input String " + in_string.decode("utf-8"))
        in_string = b'' 
    else:
        in_string += this_char
        #print (f"Read in {this_char}")

# write something 
#ser.write(b'SB780N0D;')



# read response 
#for i in range (0,3):
#        input = ser.read()
#        input_number = ord(input)
#        print ("Read input back: " + str(input_number))

