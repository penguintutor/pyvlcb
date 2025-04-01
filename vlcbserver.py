# Running communications with CANBUS
# Can be run in a seperate process

from canusb import CanUSB4
from pyvlcb import VLCB, VLCBformat
import time

port = '/dev/ttyACM0'

usb = CanUSB4(port)
vlcb = VLCB()

# Send discovery
usb.send_data(vlcb.discover())
# Receive responses until no response
# This may not end if it's a busy CBUS???
while True:
    reply = usb.read_data()
    if reply == None:
        break
    # otherwise print details
    print (vlcb.parse_input(reply))