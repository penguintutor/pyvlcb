# pyvlcb
VLCB / CBUS implementation in Python

This is currently in development. The class and method names and arguments are all subject to change.

This will provide a way to send messages to / from VLCB / CBUS using a CANUSB4.

For more details about VLCB / CBUS see: [PenguinTutor MERG page](https://www.penguintutor.com/projects/merg) 

## Install

This requires pyserial and the GUI requires PySide6.

To setup using virtual environment:

    sudo apt install python3-flask
    mkdir ~/.venv
    python3 -m venv ~/.venv/pyside6
    source ~/.venv/pyside6/bin/activate
    pip install pyside6
    pip install pyserial
    pip install fastapi uvicorn
    
Note: I have named the virtual environment pyside6 as that is the main package that is required, but you could name it differently if preferred.
    

# Running

After setting up the virtual environment activate using

    source ~/.venv/pyside6/bin/activate
    python3 vlcbapp.py 

