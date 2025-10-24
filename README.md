# pyvlcb
VLCB / CBUS implementation in Python

This is currently in development. The class and method names and arguments are all subject to change.

The application is client server based using a Python GUI code / VLCB library.

This will provide a way to send messages to / from VLCB / CBUS using a CANUSB4.

For more details about VLCB / CBUS see: [PenguinTutor MERG page](https://www.penguintutor.com/projects/merg) 

## Install


The GUI requires PySide6.

To install on Raspberry Pi OS Trixie (or later)
sudo apt install python3-pyside6.qtgui python3-pyside6.qtwidgets python3-pyside6.qtuitools  


To setup using virtual environment:

    mkdir ~/venv
    python3 -m venv ~/venv/pyvlcb
    source ~/venv/pyvlcb/bin/activate
    pip install strip_tags
    pip install flask
    pip install flask.wtf
    pip install pyserial




# Running

Start the server using

    source ~/.venv/pyvlcb/bin/activate
    python3 vlcbserver.py


After starting the server then from another terminal session run 

    python3 app.py 


# Tests

Unittest is used to provide testing of some of the backend classes. This is not exhaustive.
There is no testing of the GUI components beyond testing of the use of Signals and Slots.

To run the tests change to the tests directory and run 

    python3 run_tests.py


# Features / limitations

All requests are sent to a message queue, so there may be a short delay in them being actioned. This should not be noticeable
unless there are a lot of updates in progress.

For loco control the dial shows the desired speed, the LCD display shows the value provided in the last update
