# PyVLCB Python Software Library for VLCB

This is a Python library for VLCB (Versatile Layout Control Bus). It implements the core 
communication protocols defined by the CBUS® protocol and includes extensions for the newer 
VLCB specifications.

It is designed for use with the MERG CANUSB4 CBUS adapter and other compatible hardware.

---

## Install


For most systems including a Raspberry Pi then Python is managed using virtual environment.

**Setup a virtual environment:**

```bash
mkdir ~/venv
python3 -m venv ~/venv/pyvlcb --system-site-packages
```

**Activate the virtual environment:**

```bash
source ~/venv/pyvlcb/bin/activate
```
    
**Install the latest release:**

```bash
pip install pyvlcb
```

---

## Development 

The latest source code is available from GitHub. [PyVLCB on GitHub](https://github.com/penguintutor/pyvlcb).


### Installing as a git submodule

To install the library, as a submodule in your own git project repository, then enter your project directory and run:

```bash
git submodule add https://github.com/penguintutor/pyvlcb.git lib/pyvlcb
pip install lib/pyvlcb
```

*Note: To use as a submodule, you must create your own git project first and install within the project folder. To update, run `git pull` and repeat the pip install command.*

---

## Library Reference 

See the link below for the library reference documentation
[PyVLCB Library Reference Documentation](https://penguintutor.github.io/pyvlcb/reference/)


## Demo examples 

Example code is stored within the demo folder available on GitHub. Copy these into your project folder to test the library and connectivity.

* The demos are created for a Raspberry Pi or other Linux computers.
* The USB port is hard-coded as /dev/ttyACM0.
* For other computers or USB ports, edit the Python file and update the port statement.Example code is stored within the demo folder available from GitHub. Copy these into your project folder to test the library and connectivity. 

## More Details

* Project page: [PenguinTutor PyVLCB library page](https://www.penguintutor.com/projects/pyvlcb)
* Application example: [PenguinTutor Pi SignalBox project page](https://www.penguintutor.com/projects/pisignalbox)

## Legal and Trademarks

* **CBUS®** is a registered trademark of Dr. Michael Bolton. 
* This library is an independent implementation based on publicly available protocol documentation and is not officially affiliated with or endorsed by the trademark holder.
* All other trademarks are the property of their respective owners.


