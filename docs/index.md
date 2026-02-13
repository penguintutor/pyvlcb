# Welcome to PyVLCB 

PyVLCB is a Python library for VLCB (Versatile Layout Control Bus). It implements the core
communication protocols defined by the CBUS® protocol and includes extensions for the newer
VLCB specifications.
It also includes a module for the CANUSB4 controller from MERG.

[PyVLCB project page on PenguinTutor.com](https://www.penguintutor.com/projects/pyvlcb)


## Installation

Basic install can be performed by downloading the files and running

pip install pyvlcb

See the README.md for more detailed install details, including how the library can be installed as a submodule within your own software.

## Demo code

See the demo directory for simple code examples. 

## Core concepts

The library conists of 4 core classes which are imported from pyvlcb

* VLCB - core library
    * Easy to use methods for reading and writing CBUS / VLCB commands
* VLCBFormat - VLCB formatting
    * Converts data packets for sending 
* VLCBOpcode - Lookup opcode values. 
    * Primarily intended for internal use by the other classes
* CanUSB4 - Communicate with the CAN USB 4 controller
    * Uses pyserial for communication with the Merg CAN USB 4
    * Can accept packets created using the VLCB core library

Initially connection is made to CanUSB4 to establish a connection with the hardware.
For most uses sending a command is performed by calling the appropriate VLCB method to generate a command string. Then passing that command string to the CanUSB4 send_data method.
Data from the bus is read using read_usb which can then be passed to the VLCB parse_input method. Additional methods are available to extract the relevant information from the parse_input response.

## Additional documentation

For further details please see [PenguinTutor PyVLCB page](https://www.penguintutor.com/projects/pyvlcb)

## Key Features

* Simplified methods for CBUS / VLCB lookup
* Full CBUS opcode support
* Fully type-hinted for better IDE support

## Legal and Trademarks

* **CBUS®** is a registered trademark of Dr. Michael Bolton.
* This library is an independent implementation based on publicly available protocol documentation and is not officially affiliated with or endorsed by the trademark holder.
* All other trademarks are the property of their respective owners.


