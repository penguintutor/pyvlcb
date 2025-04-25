# Class for handling VLCB data formatting
# Data is returned as string - needs to be encoded afterwards

from vlcbformat import VLCBformat, VLCBopcode

class VLCB:
    # 60 is default canid for canusb4 (127 is dcc controller)
    def __init__ (self, can_id=60):
        self.can_id = can_id
        self.debug = False
    
    # Takes input bytestring and parses header / data
    # Does not try and interpret op-code - that is left to VLCB_format
    def parse_input (self, input_bytes):
        # Also allow string (no need to decode)
        if isinstance (input_bytes, str):
            input_string = input_bytes
        else:
            input_string = input_bytes.decode("utf-8")
        print (f"Parsing {input_string}")
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
    
    # Parse and format into standard log format (fulldata, can_id, op_code, data)
    # For log all values are returned as strings
    def log_entry (self, input_string):
        # First remove date from the front of the string
        date_log = input_string.split(',', 2)
        date_string = date_log[0]
        vlcb_entry = self.parse_input (date_log[1])
        # Error handling of invalid packet
        if vlcb_entry == False:
            return [date_log[1], "??", "", "Invalid data"]
        # convert op-code to string
        # opcode is first two chars of data
        opcode = vlcb_entry.data[0:2]
        opcode_string = f'{opcode} - {VLCBopcode.opcode_mnemonic(opcode)}'
        #data_string = f"{VLCBopcode.parse_data(vlcb_entry.data)}"
        data_string = VLCB._dict_to_string(VLCBopcode.parse_data(vlcb_entry.data))
        return [date_string, date_log[1], str(vlcb_entry.can_id), opcode_string, data_string]
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
    def num_to_hexstr (num):
        return f"{hex(num).upper()[2:]:0>4}"
    
    # Create header using low priority and can_id (or self.can_id)
    def make_header (self, majpri = 0b10, minpri = 0b11, can_id = None):
        if can_id == None:
            can_id = self.can_id
        header_val = (majpri << 14) + (minpri << 12) + (can_id << 5)
        header_to_hex = ("000" + hex(header_val).upper()[2:])[-4:]
        header_string = f':S{header_to_hex}N'
        return header_string
        #return header_string.encode('utf-8')
    
    # Discover nodes
    def discover (self):
        # Return QNN 
        return self.make_header() + '0D;'
    
    # Discover number of events configured
    def discover_evn (self, node_id):
        return f"{self.make_header()}58{VLCB.num_to_hexstr(node_id)};" 
        
    # Discover number of events available
    def discover_nevn (self, node_id):
        return f"{self.make_header()}56{VLCB.num_to_hexstr(node_id)};"
    
    # Discover stored events NERD
    def discover_nerd (self, node_id):
        return f"{self.make_header()}57{VLCB.num_to_hexstr(node_id)};"
        
    #manufaturer name  is requested by RQMN.
    #<0x11>
    #The response is NAME
    #<0xE2><><char1><char2><char3><char4><char5><char6><char7>
    #Obviously the NAME string is limited to 7 chars, all 7 characters are used
    