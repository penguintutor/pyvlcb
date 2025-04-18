# pyvlcb
VLCB / CBUS implementation in Python

This is currently in development. The class and method names and arguments are all subject to change.

This will provide a way to send messages to / from VLCB / CBUS using a CANUSB4.

For more details about VLCB / CBUS see: [PenguinTutor MERG page](https://www.penguintutor.com/projects/merg) 

## Install

This requires pyserial and the GUI requires PySide6.

To setup using virtual environment:

    mkdir ~/.venv
    python3 -m venv ~/.venv/pyside6
    source ~/.venv/pyside6/bin/activate
    pip install pyside6
    pip install pyserial
    pip install zmq
    
Note: I have named the virtual environment pyside6 as that is the main package that is required, but you could name it differently if preferred.


# Running

After setting up the virtual environment activate using

    source ~/.venv/pyside6/bin/activate

Start the server using:

    python3 vlcbserver.py

Run the GUI application using:

    python3 vlcbapp.py 

