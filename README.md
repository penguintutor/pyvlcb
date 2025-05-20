# pyvlcb
VLCB / CBUS implementation in Python / C

This is currently in development. The class and method names and arguments are all subject to change.

The application is client server based using a C server, but Python GUI code / VLCB library.

This will provide a way to send messages to / from VLCB / CBUS using a CANUSB4.

For more details about VLCB / CBUS see: [PenguinTutor MERG page](https://www.penguintutor.com/projects/merg) 

## Install

The server needs libmicrohttpd
    sudo apt install libmicrohttpd-dev

The GUI requires PySide6.

To setup using virtual environment:

    mkdir ~/.venv
    python3 -m venv ~/.venv/pyside6
    source ~/.venv/pyside6/bin/activate
    pip install pyside6

    
Note: I have named the virtual environment pyside6 as that is the main package that is required, but you could name it differently if preferred.


# Compiling the C code

    cd c-server
    gcc vlcbserver.c -o vlcbserver -lmicrohttpd -lrt
(For additional warning messages you can use the -Wall option)
    

# Running

Start the server using
    cd c-server
    ./vlcbserver


After setting up the virtual environment activate using

    source ~/.venv/pyside6/bin/activate
    python3 app.py 



# Features / limitations

All requests are sent to a message queue, so there may be a short delay in them being actioned. This should not be noticeable
unless there are a lot of updates in progress.

For loco control the dial shows the desired speed, the LCD display shows the value provided in the last update



Steal = GLOC (61) Flags = 1
eg. :SB040N61D44601;

- 63 Err code 8 = Session cancelled
Followed by E1 PLOC


GLOC Flags = 2 = Share

44 STMOD - mode = 0 ? - is speed mode 128 steps (is this required)?
