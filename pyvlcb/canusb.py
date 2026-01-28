import serial
from typing import Optional, Union
from .exceptions import DeviceConnectionError, InvalidConfigurationError, ProtocolError, DeviceTimeoutError
import logging

# Set up a null handler so nothing prints by default unless the user enables it
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Based on CANUSB4 - sends using pyserial
# This just makes calls to pyserial, but by abstracting would mean you could
# replace easier if using a different way to connect to CANBUS
# Needs port (eg. /dev/ttyACM0)
class CanUSB4 ():
    """Handle USB serial communication to CANUSB4
    
    Uses pyserial to communicate over USB.

    Attributes:
        port: The usb port eg. /dev/ttyACM0 (RPi)
    """
    def __init__ (self, 
                  port: str, 
                  baud: Optional[int] = 115200, 
                  timeout: Optional[float] = 0.01) -> None:
        """Inits CanUSB4 with a USB port
        
        Args:
            port: USB port eg. /dev/ttyACM0 (RPi)
            baud: Baud rate in bytes
            timeout: How long to wait for a serial timeout (seconds)

        Raises:
            DeviceConnectionError: If the port cannot be opened or is already in use.
            InvalidConfigurationError: If the port name is empty or invalid.

        """
        self.debug = False
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.max_retry = 30    # How many times to attempt on get_data must be at least as long as frame
        # Timeout for a request could be max_rety x timeout
        
        if not port:
            raise InvalidConfigurationError("Port name cannot be empty")

        # buffer to hold partial string - allows us to continue if read ends partway through a packet
        self.current_buffer = ''
        # Track if we are in a valid string (ie. ignore any data outside of : ; blocks
        self.data_start = False
        self.connect()
        
        
    # Optional arguments override existing
    def connect(self, port=None, baud=None, timeout=None):
        """Inits CanUSB4 with a USB port
        
        Args:
            port: USB port eg. /dev/ttyACM0 (RPi)
            baud: Baud rate in bytes
            timeout: How long to wait for a serial timeout (seconds)

        Raises:
            DeviceConnectionError: If the port cannot be opened or is already in use.
            InvalidConfigurationError: If the port name is empty or invalid.

        """
        if port != None:
            self.port = port
        if not port:
            raise InvalidConfigurationError("Port name cannot be empty")
        if baud != None:
            self.baud = baud
        if timeout != None:
            self.timeout = timeout
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        except serial.SerialException as e:
            raise DeviceConnectionError(f"Could not open port {self.port}") from e
        if self.ser:
            logger.info("Connected to serial port")


    # Data can either be string or bytestring
    def send_data(self, data: Union[str, bytes]) -> None:
        """Send data to serial

        Args:
            data: Data to send, normally from a VLCB method

        Raises:
            InvalidConfigurationError: If string contains invalid characters
            TypeError: If data passed is not a string or a bytestring
            

        """
        logger.debug(f"Sending {data}")
        if isinstance(data, str):
            try:
                # Convert string to bytes
                payload = data.encode('ascii') # using ascii which is more restrictive than default "utf-8"
            except UnicodeEncodeError as e:
                raise InvalidConfigurationError(f"String contains invalid characters: {data}") from e
        elif isinstance(data, bytes):
            # It's already bytes, just use it
            payload = data
        else:
            # User sent an int, list, or something else weird
            raise TypeError(f"Expected str or bytes, got {type(data).__name__}")

        # Send payload which is now bytes
        try:
            self.ser.write(payload)
        except serial.SerialException as e:
            raise DeviceConnectionError("Connection lost during write") from e
    
    def read_data(self):
        #print (f"Reading data - status {self.ser.is_open}")
        num_bytes = self.ser.in_waiting
        #print (f"Num bytes {num_bytes}")
        # As each data string is read then it is stored into this list
        # Which allows all new packets to be returned
        # First packet is number of entries (or in the case of error negative)
        # If error then always 2 more strings - First general error, next is output from e
        received_data = [0]
        if num_bytes > 1:
            try:
                in_chars = self.ser.read(num_bytes)
            except serial.SerialException:
                pass
            # Unable to communicate with USB
            except TypeError as e:
                # Close if not already
                self.ser.close()
                return [-1, "NotConnect", "e"]
            # Any other error
            except Exception as e:
                return [-2, "Error", "e"]
            
            #print (f"Num chars {len(in_chars)}")
            #print (f"Chars are {in_chars}")
            
            for i in range(0, len(in_chars)):
                this_char = chr(in_chars[i])
                #print (f"This char {this_char}")
                # End of packet
                if this_char == ';':
                    # Check we have some data if not then ignore
                    if len(self.current_buffer) == 0:
                        continue
                    # Add the terminating char
                    self.current_buffer += this_char
                    if self.debug:
                        print (f"Read {self.current_buffer}")
                    #received_data.append(self.current_buffer.decode('utf-8'))
                    received_data.append(self.current_buffer)
                    received_data[0] += 1
                    # delete the data
                    self.current_buffer = ''
                    # no longer inside a data packet
                    self.data_start = False
                # Start of packet (resets string even if previous data)
                elif this_char == ':':
                    self.data_start = True
                    self.current_buffer = ':'
                # Only add character if we are inside a data block
                elif self.data_start == True:
                    self.current_buffer += this_char
                # If not then we are not in data block
                else:
                    continue
        #print (f"USB returning {received_data}")
        return received_data    
        
        
    # Reads byte at a time looking for : (start) and ; (end)
    # timesout if no data received
    # Returns list [status, data]
    # Status = "Data", "NoData", "NotConnect", "Error" (other error)
    # If error then e is sent instead of data
    def read_data_old(self):
        retry_count = 0
        data_start = False    # After : goes to true to signify data being received
        in_string = b''
        while retry_count < self.max_retry:
            try:
                this_char = self.ser.read(1)
            # No data
            except serial.SerialException:
                retry_count += 1
                continue
            # Unable to communicate with USB
            except TypeError as e:
                # Close if not already
                self.ser.close()
                return ["NotConnect", "e"]
            # Any other error
            except Exception as e:
                return ["Error", "e"]
            #print (f"Read returned {this_char}")
            if this_char == b'':
                retry_count += 1
            # End of packet
            elif this_char == b';':
                # Check we have some data if not then return NoData
                if len(in_string) == 0:
                    return ["NoData", ""]
                # Add the terminating char
                in_string += this_char
                if self.debug:
                    print (f"Read {in_string}")
                return ["Data", in_string]
            # Start of packet (resets string even if previous data)
            elif this_char == b':':
                in_string = b':'
                # reset retry value
                retry_count = 0
                data_start = True
            # Only add character if we are inside a data block
            elif data_start == True:
                in_string += this_char
                # increment retry (otherwise won't exist if we don't get a ;)
                retry_count += 1
            # If not then we are not in data block
            else:
                retry_count += 1
        # Reach here we exited from retry_count due to a timeout
        if self.debug:
            print ("Read timeout")
        return ["NoData", ""]