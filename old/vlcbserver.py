# Running communications with CANBUS
# Can be run in a seperate process

from canusb import CanUSB4
from pyvlcb import VLCB
import time

port = '/dev/ttyACM0'

usb = CanUSB4(port)
vlcb = VLCB()

# Send discovery
print (vlcb.parse_input(b':SB780N0D;'))
usb.send_data(vlcb.discover())
# Receive responses until no response
# This may not end if it's a busy CBUS???
while True:
    reply = usb.read_data()
    if reply == None:
        break
    # otherwise print details
    print (vlcb.parse_input(reply))