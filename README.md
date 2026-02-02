# PyVLCB Python Software Library for CBUS / VLCB

This is a small software library for CBUS and VLCB using Python. 

It's designed for use with the MERG CANUSB4 CBUS adapter. The 


## Install

The library can be installed from github.

For most systems including a Raspberry Pi then Python is managed using virtual environment.
To setup a virtual environment enter the following commands

    mkdir ~/venv
    python3 -m venv ~/venv/pyvlcb --system-site-packages

You will then need to run the following command to activate the virtual environment

    source ~/venv/pyvlcb/bin/activate

## Installing current version only

If you just want to install the current version from Github enter you project library and run:

    pip install git+https://github.com/penguintutor/pyvlcb.git --target lib/pyvlcb

Your project does not have to be a git repository for this option.

## Installing as a git submodule

To install the library, as a submodule in your own git project repository, then enter your project directory and run:

    git submodule add https://github.com/penguintutor/pyvlcb.git lib/pyvlcb
    pip install lib/pyvlcb

If you subsequenctly want to get the latest version of the library run a git pull then use the pip install command again. 

_Important_ To use as a submodule you must create your own git project first and install within the project folder.

## Library Reference 

See the link below for the library reference documentation
[PyVLCB Library Reference Documentation](https://penguintutor.github.io/pyvlcb/reference/)


## Demo examples 

Example code is stored within the demo folder. Copy these into your project folder to test the library and connectivity. 
The demos are created for a Raspberry Pi or other Linux computer. The USB port is hard-coded as /dev/ttyACM0
For other computers / USB ports then edit the python file directory and update the port statement.

## More Details

For more details see: [PenguinTutor PyVLCB library page](https://www.penguintutor.com/projects/pyvlcb)

For an example of a program using this library see the [PenguinTutor Pi SignalBox project page](https://www.penguintutor.com/projects/pisignalbox)
