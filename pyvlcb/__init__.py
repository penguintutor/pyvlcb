# Class for handling VLCB data formatting
# Data is returned as string - needs to be encoded afterwards

from .vlcbformat import VLCBformat, VLCBopcode
from .canusb import CanUSB4

class VLCB:
    """Handle VLCB formatting
    
    It generates the appropriate strings which can be sent to CBUS / VLCB

    Attributs:
    can_id (int): The Can ID for your software (default = 60)
    
    """
    # 60 is default canid for canusb4 (127 is dcc controller)
    def __init__ (self, can_id=60):
        """Inits VLCB with a can_id
        
        Args:
            can_id (int): The can_id for the software (default = 60)
        """
        self.can_id = can_id
        self.debug = False
    
    # Takes input bytestring and parses header / data
    # Does not try and interpret op-code - that is left to VLCB_format
    def parse_input (self, input_bytes):
        """Parse a raw CBUS packet as an input bytestring

        Take a bytestring (or string) from the CBUS and extract the details

        Args: 
            input_types (bytestring): Input raw bytestring (or string)

        Returns:
            VLCBFormat: parsed data in VLCBFormat

        """
        # Also allow string (no need to decode)
        if isinstance (input_bytes, str):
            input_string = input_bytes
        else:
            input_string = input_bytes.decode("utf-8")
        if (len(input_string) < 5):        # packets are actually much longer
            print ("Data too short")    
            return False
        if (input_string[0] != ":"):
            print ("No start frame")
            return False
        if (input_string[1] != "S"):
            print ("Format not supported - only Standard frames allowed")
            return False
        # Use try when converting to number in case of error
        try:
            header = input_string[2:6]
            header_val = int(header, 16)
        except:
            print (f"Invalid format, number expected {header}")
            header_val = 0
        if self.debug:
            print (f"Header {hex(header_val)}")
        priority = (header_val & 0xf000) >> 12
        if self.debug:
            print (f"Priority {priority:b}")
        can_id = (header_val & 0xfe0) >> 5
        if self.debug:
            print (f"Can ID {can_id}")
        # Next is N / RTR can be ignored
        if self.debug:
            print (f"N / RTR {input_string[6]}")
        # Data is rest excluding ; 
        data = input_string[7:-1]
        if self.debug:
            print (f"Data {data}")
        # Creates a VLCB_format and returns that
        return VLCBformat (priority, can_id, data)
    
    # Parse and format into standard log format (datastring, direction, fulldata, direction, can_id, op_code, data
    # For log all values are returned as strings - note that the number (log entry number) is not returned
    def log_entry (self, input_string):
        # Input string is num,date,direction,message
        # First remove number and date from the front of the string
        entry_parts = input_string.split(',', 3)
        date_string = entry_parts[1]
        direction = entry_parts[2]
        message = entry_parts[3]
        vlcb_entry = self.parse_input (message)
        # Error handling of invalid packet
        if vlcb_entry == False:
            return [message, "??", "", "Invalid data"]
        # convert op-code to string
        # opcode is first two chars of data
        opcode = vlcb_entry.data[0:2]
        opcode_string = f'{opcode} - {VLCBopcode.opcode_mnemonic(opcode)}'
        #data_string = f"{VLCBopcode.parse_data(vlcb_entry.data)}"
        data_string = VLCB._dict_to_string(VLCBopcode.parse_data(vlcb_entry.data))
        return [date_string, direction, message, str(vlcb_entry.can_id), opcode_string, data_string]
        # Todo - error handling 
    
    # dict to string without {} or ""
    @staticmethod
    def _dict_to_string (dictionary):
        data_string = ""
        for key, value in dictionary.items():
            if data_string != "":
                data_string += " , "
            data_string += f"{key} = {value}"
        return data_string
    
    @staticmethod
    # Where 1 x bytes (2 chars)
    def num_to_1hexstr (num):
        return f"{hex(num).upper()[2:]:0>2}"
    
    @staticmethod
    # Where 2 x bytes (4 chars)
    def num_to_2hexstr (num):
        return f"{hex(num).upper()[2:]:0>4}"
    
    @staticmethod
    # Where 4 x bytes (8 chars)
    def num_to_4hexstr (num):
        return f"{hex(num).upper()[2:]:0>8}"
    
    @staticmethod
    # Where 2 bytes convert to addr id
    def bytes_to_addr (byte1, byte2):
        msb = int(byte1)
        lsb = int(byte2)
        return ((msb << 8) + lsb)
    
    @staticmethod
    def bytes_to_hexstr (byte1, byte2):
        return f"{hex(byte1).upper()[2:]:0>2}{hex(byte2).upper()[2:]:0>2}"
        
    
    # Create header using low priority and can_id (or self.can_id)
    # If opcode provided, but no priority then appropriate min code looked up
    # MajPri would be based on packet aging - needs to be managed outside of this
    def make_header (self, majpri = 0b10, minpri = None, can_id = None, opcode=None):
        if can_id == None:
            can_id = self.can_id
            
        if minpri == None and opcode != None:
            minpri = VLCBopcode.opcode_priority(opcode)
            
        # If opcode not updated then use default low priority
        # Lower number is higher priority
        if minpri == None:
            minpri = 0b11
            
        header_val = (majpri << 14) + (minpri << 12) + (can_id << 5)
        header_to_hex = ("000" + hex(header_val).upper()[2:])[-4:]
        header_string = f':S{header_to_hex}N'
        return header_string
        #return header_string.encode('utf-8')
    
    # Discover nodes
    def discover (self):
        # Return QNN 
        return self.make_header(opcode='0D') + '0D;'
    
    # Discover number of events configured
    def discover_evn (self, node_id):
        return f"{self.make_header(opcode='58')}58{VLCB.num_to_2hexstr(node_id)};" 
        
    # Discover number of events available
    def discover_nevn (self, node_id):
        return f"{self.make_header(opcode='56')}56{VLCB.num_to_2hexstr(node_id)};"
    
    # Discover stored events NERD
    def discover_nerd (self, node_id):
        return f"{self.make_header(opcode='57')}57{VLCB.num_to_2hexstr(node_id)};"
    
    # Emergency stop all locos
    # RESTP
    def loco_stop_all (self):
        return f"{self.make_header(opcode='0A')}0A;"
    
    # node and ev should be the IDs - state either "on" or "off" / True or False
    def accessory_command (self, node_id, ev_id, state):
        # if ev_id is a string then convert to an int
        # Setting based to 0 will automatically handle base 10 or hex
        ev_id = int(ev_id, 0)
        # determine if long or short
        if ev_id <= 0xffff:
            return self.accessory_short_command (node_id, ev_id, state)
        else:
            return self.accessory_long_command (node_id, ev_id, state)
        
    # Note that short is the same as long but different code and node_id is added (already included in long)
    def accessory_short_command (self, node_id, ev_id, state):
        # Turn on
        if state == True or state == "on":
            # ASON
            return f"{self.make_header(opcode='98')}98{VLCB.num_to_2hexstr(node_id)}{VLCB.num_to_2hexstr(ev_id)};"
        # Turn off = ASOFF
        else:
            return f"{self.make_header(opcode='99')}99{VLCB.num_to_2hexstr(node_id)}{VLCB.num_to_2hexstr(ev_id)};"
        
    def accessory_long_command (self, node_id, ev_id, state):
        # Turn on
        if state == True or state == "on":
            # ASON
            return f"{self.make_header(opcode='90')}90{VLCB.num_to_4hexstr(ev_id)};"
        # Turn off = ASOFF
        else:
            return f"{self.make_header(opcode='91')}91{VLCB.num_to_4hexstr(ev_id)};"
        
    # RLOC (Allocate loco) :SB040N40D446;
    # Short address upper address all zeros, only 6 bits of the lower byte are used (1 to 127) 0 is decoderless
    # :SB040N40D446 D446 becomes 5190(10) = 1446(H) + C000 (highest 2 bits set by CAB - indicate long mode)
    
    # Generate code to allocate a loco
    # Assume long code, but if long = False and ID < 128 then use short mode
    def allocate_loco (self, loco_id, long=True):
        # Generate RLOC to allocate loco to a session
        if long == False and loco_id >= 127:
            print ("Invalid short code")
            return False
        if long == True:
            loco_id = loco_id | 0xC000
        return f"{self.make_header(opcode='40')}40{VLCB.num_to_2hexstr(loco_id)};"
    
    def release_loco (self, session_id):
        return f"{self.make_header(opcode='21')}21{VLCB.num_to_1hexstr(session_id)};"
    
    def steal_loco (self, loco_id, long=True):
        # GLOC 61 - flag = 1 for steal, flag = for share
        if long == False and loco_id >= 127:
            print ("Invalid short code")
            return False
        if long == True:
            loco_id = loco_id | 0xC000
        return f"{self.make_header(opcode='61')}61{VLCB.num_to_2hexstr(loco_id)}01;"   
        
    def share_loco (self, loco_id, long=True):
        # GLOC 61 - flag = 1 for steal, flag = for share
        if long == False and loco_id >= 127:
            print ("Invalid short code")
            return False
        if long == True:
            loco_id = loco_id | 0xC000
        return f"{self.make_header(opcode='61')}61{VLCB.num_to_2hexstr(loco_id)}02;" 
        
    def keep_alive (self, session_id):
        return f"{self.make_header(opcode='23')}23{VLCB.num_to_1hexstr(session_id)};"
    
    # Set loco speed and direction (always done together)
    # Maximum once every 32 miliseconds (GUI configured based on non triggered so shouldn't be an issue)
    # Could add time detection if required
    # This uses the combined speed and direction value
    def loco_speeddir (self, session_id, speeddir):
        return f"{self.make_header(opcode='47')}47{VLCB.num_to_1hexstr(session_id)}{VLCB.num_to_1hexstr(speeddir)};"
    
    # Set function using DFUN - needs to be provided with the two bytes
    # First byte is group (1 = F1 to F4, 2 = F5 to F8, 3 = F9 to F12)
    # 4 = F13 to 19, 5 = F20 to F28
    # Second byte is 1 bit per function - set 1 for on, 0 for off, lsb to right
    # eg. 1 = 0001, 2 = 0010
    def loco_set_dfun (self, session_id, byte1, byte2):
        return f"{self.make_header(opcode='60')}60{VLCB.num_to_1hexstr(session_id)}{VLCB.num_to_1hexstr(byte1)}{VLCB.num_to_1hexstr(byte2)};"
        
