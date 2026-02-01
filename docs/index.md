# Welcome to PyVLCB 

PyVLCB is a python library for use with model railway electronics using CBUS or VLCB.
It includes a module for the CANUSB4 controller from MERG.

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
** Easy to use methods for reading and writing CBUS / VLCB commands
* VLCBFormat - VLCB formatting
** Converts data packets for sending 
* VLCBOpcode - Lookup opcode values. 
** Primarily intended for internal use by the other classes
* CanUSB4 - Communicate with the CAN USB 4 controller
** Uses pyserial for communication with the Merg CAN USB 4
** Can accept packets created using the VLCB core library

## Additional documentation

For further details please see [PenguinTutor PyVLCB page](https://www.penguintutor.com/projects/pyvlcb)

## Key Features

* Simplified methods for CBUS / VLCB lookup
* Full CBUS opcode support
* Fully type-hinted for better IDE support


