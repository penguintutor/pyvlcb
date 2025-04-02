# Class for handling VLCB data formatting

from vlcbformat import VLCBformat, VLCBopcode

class VLCB:
    # 60 is default canid for canusb4 (127 is dcc controller)
    def __init__ (self, can_id=60):
        self.can_id = can_id
        self.debug = False
    
    # Takes input bytestring and parses header / data
    # Does not try and interpret op-code - that is left to VLCB_format
    def parse_input (self, input_bytes):
        input_string = input_bytes.decode("utf-8")
        if (input_string[0] != ":"):
            print ("No start frame")
            return False
        if (input_string[1] != "S"):
            print ("Format not supported - only Standard frames allowed")
            return False
        header = input_string[2:6]
        header_val = int(header, 16)
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
        # Data is rest excluding ; which was already stripped during read
        data = input_string[7:]
        if self.debug:
            print (f"Data {data}")
        # Creates a VLCB_format and returns that
        return VLCBformat (priority, can_id, data)
    
    # Create header using low priority and can_id (or self.can_id)
    def make_header (self, majpri = 0b10, minpri = 0b11, can_id = None):
        if can_id == None:
            can_id = self.can_id
        header_val = (majpri << 14) + (minpri << 12) + (can_id << 5)
        header_to_hex = ("000" + hex(header_val).upper()[2:])[-4:]
        header_string = f':S{header_to_hex}N'
        return header_string.encode('utf-8')
    
    def discover (self):
        # Return QNN 
        return self.make_header() + b'0D;'
        
        
    