# Holds a loco session
# Typically a single loco being controlled by the GUI, but multiple instances can be created for
# automation etc.
import json

class Loco:
    # All arguments have default allowing creation of a dummy loco
    # Normally use classmethod from_file to open an existing file
    # If filename specified must include full path
    def __init__ (self, loco_id=0, session=0, direction=1, speed=0, filename=None):
        # status starts in off, change to rloc when rloc sent, then on when allocated
        # if error after ploc then set to off
        # if gloc then set status to gloc - and then on after aquire (ploc)
        self.status = "off"   
        self.loco_id = loco_id
        #self.loco_class = ""
        self.loco_name = ""	# This needs to be unique (no checking so if not then the first will be returned)
        #					todo - need to remove this unique depenccency use filename instead
        self.loco_data = {}
        self.session = session # If session == 0 then no session allocated (don't support none DCC)
        self.direction = direction # 1 = forward, 0 = reverse
        self.speed = speed # Allow 0 to 128 but maximum sent is 127. Speed 1 = emergency stop (not used - instead status = stop)
        # Track all functions. Only F0 to F12 are found from PLOC - rest assume start off
        self.function_status = [0] * 29
        # Set filename to allow it to be saved - must be full path - this is unique
        # todo review alternatives to using full path - although doesn't cause any issues with portability as not saved within file
        self.filename = filename
    
    def set_status (self, value):
        self.status = value
        
    # Returns the display name
    def get_display_name (self):
        return self.loco_data['displayname']
        
        
    # Returns filename. If not filename then return default so as valid image
    # Note that default.png must exist in the locos directory
    def get_image_filename (self):
        if 'image' in self.loco_data and self.loco_data['image'] != "":
            return self.loco_data['image']
        else:
            return "default.png"
    
    # Data is a dict of what to change
    # Changes info about the loco
    def update_loco (self, data):
        for key, value in data.items():
            if key == 'address':
                self.loco_id = value
            #elif key == 'class':
            #    self.loco_class = value
            elif key == 'name':
                self.loco_name = value
            # Add to loco_data even if one of the special ones above
            self.loco_data[key] = value
        
    
    # Loads a json file with details of the loco
    # there are more details in the file - just pull out id and name for quick reference
    def load_file (self, filename):
        with open(filename, 'r') as data_file:
            self.loco_data = json.load(data_file)
        self.loco_id = self.loco_data["address"]
        self.loco_name = self.loco_data["displayname"]
        self.filename = filename
        
    # Returns True is successful save
    def save_file (self, filename=None):
        if filename == None:
            filename = self.filename
        try:
            with open(filename, 'w') as data_file:
                json.dump(self.loco_data, data_file, indent=4)
        except:
            return False
        return True
            
    # get number of functions
    # handles if none defined
    def num_functions (self):
        if "functions" in self.loco_data:
            return len(self.loco_data["functions"])
        else:
            # If none then return 5 (just none defined)
            return 5
            #return 0
        
    # Resets the functions - sets to all 0
    def function_reset (self):
        num_functions = self.num_functions()
        # Minimum of 29 even if not used / available to allow dfun return codes
        if num_functions < 29:
            num_functions = 29
        self.function_status = [0] * num_functions
    
    def get_functions (self):
        f_titles = []
        if "functions" not in self.loco_data.keys():
            # If no functions defined then return some default ones
            return ["F0", "F1", "F2", "F3", "F4" ]
        for this_function in self.loco_data["functions"]:
            # Function titles includes Fx and text
            f_titles.append(f"{this_function[0]} - {this_function[1]}")
        return f_titles
    
    # Returns status (ie. 1 on / 0 off) and type "toggle" vs "latch"
    def get_function_status (self, func_num):
        # Check valid - should not get this as func_num should be based on the loaded functions
        if ("functions" not in self.loco_data.keys()) or (len(self.loco_data["functions"]) < func_num):
            return [self.function_status[func_num], "trigger"]
        this_function = self.loco_data["functions"][func_num]
        # 2 is type
        return [self.function_status[func_num], this_function[2]]
    
    # Do we have an active session (respond True even if force stop)
    def is_active (self):
        if self.session != 0 and (self.status == "on" or self.status == "stop"):
            return True
        return False
    
    # Is setup in progress (rloc / gloc)
    def is_aquiring (self):
        if self.status == 'gloc' or self.status == 'rloc':
            return True
        return False
    
    # normalize speed value (subtract 1)
    def speed_value (self):
        if self.speed > 1:
            return self.speed -1
        return 0
    
    # Same as release but also set loco_id to 0 to indicate none requested
    def reset (self):
        self.loc_id = 0
        self.released()
    
    # Use when loco released
    def released (self):
        self.status = "off"
        self.session = 0
        
    def session_established (self, session):
        # Add session id to the loco
        self.status = on
        self.session = session
        
    # get Dir/Speed combined value
    def get_speeddir (self):
        # uses local variable for calculating return value
        speed = self.speed
        if self.speed > 127:
            speed = 127
        # If emergency stop then send 1 as speed
        if self.status == "stop":
            speed = 1
        return (self.direction * 0x80) + speed
    
    # Takes combined speed & dir and updates direction / speed
    # This is often used based on external values, so add 1
    def set_speeddir (self, speed_dir):
        speed = self.speed
        self.direction = speed_dir >> 7
        self.speed = speed_dir & 0x7F
        if self.speed > 1:
            self.speed += 1
    
    # emergency stop
    def set_stop (self):
        self.status = "stop"
      
    # Sets speed only - keep current direction
    # 0 = stop, 1 = increase to 2 (1 is emergency stop - so don't allow here)
    # all other values used as is (maximum 127 - but allow 128)
    def set_speed (self, speed_value):
        if speed_value > 128 or speed_value < 0:
            return
        # Add one to skip emergency stop
        if speed_value > 0 and speed_value < 127:
            speed_value += 1
        self.speed = speed_value
        
    # Direction is 1 for forward, 0 for reverse
    # Could add support for other variable types
    def set_direction (self, direction):
        if isinstance(direction, int) and (direction ==  0 or direction == 1):
            self.direction = direction
        # Otherwise just ignore
        
    # This sets the value of the functions from a PLOC message
    # Only stores values for F0 to F12
    # fn1 = <Dat5> is the function byte F0 to F4 - bit 5 = dir lighting (F0), bit 6 = direction, bit 7 = res, bit 8 = 0
    # fn2 = <Dat6> is the function byte F5 to F8 - bit 5 upwards reserved
    # fn3 = <Dat7> is the function byte F9 to F12
    def set_functions (self, fn1, fn2, fn3):
        data_in = [fn1, fn2, fn3]
        mask = [0b0001, 0b0010, 0b0100, 0b1000]
        # Handle 0 separately as it's in the upper nibble
        self.function_status[0] = data_in[0] & 0b10000
        for i in range (0, 3):
            for j in range (0, 4):
                self.function_status[(i*4)+j+1] = 1 if (data_in[i] & mask[j]) > 0 else 0
    

    # Sets function and returns bytes required for DFUN command
    # First byte is group (1 = F1 to F4, 2 = F5 to F8, 3 = F9 to F12)
    # 4 = F13 to 20, 5 = F21 to F27
    # Second byte is 1 bit per function - set 1 for on, 0 for off, lsb to right
    # eg. 1 = 0001, 2 = 0010
    # function = function number, on_off = 1 or 0
    def set_function_dfun (self, function, on_off):
        #print (f"Loco set_function_dfun - {function}, {on_off}, {self.function_status}")
        if function  > len (self.function_status):
            return None
        self.function_status[function] = on_off
        if function <= 4:
            byte1 = 1
            byte2 = (0b10000 * self.function_status[0] +  # fn0 is higher nibble (bit 5)
                     0b0001 * self.function_status[1] +
                     0b0010 * self.function_status[2] +
                     0b0100 * self.function_status[3] +
                     0b1000 * self.function_status[4]
                     )
        elif function <= 8:
            byte1 = 2
            byte2 = (0b0001 * self.function_status[5] +
                     0b0010 * self.function_status[6] +
                     0b0100 * self.function_status[7] +
                     0b1000 * self.function_status[8]
                     )
        elif function <= 12:
            byte1 = 3
            byte2 = (0b0001 * self.function_status[9] +
                     0b0010 * self.function_status[10] +
                     0b0100 * self.function_status[11] +
                     0b1000 * self.function_status[12]
                     )
        elif function <= 20:
            byte1 = 4
            byte2 = (0b0001 * self.function_status[13] +
                     0b0010 * self.function_status[14] +
                     0b0100 * self.function_status[15] +
                     0b1000 * self.function_status[16] +
                     0b10000 * self.function_status[17] +
                     0b100000 * self.function_status[18] +
                     0b1000000 * self.function_status[19] +
                     0b10000000 * self.function_status[20]
                     )
        elif function <= 28:
            byte1 = 5
            byte2 = (0b0001 * self.function_status[21] +
                     0b0010 * self.function_status[22] +
                     0b0100 * self.function_status[23] +
                     0b1000 * self.function_status[24] +
                     0b10000 * self.function_status[25] +
                     0b100000 * self.function_status[26] +
                     0b1000000 * self.function_status[27] +
                     0b10000000 * self.function_status[28]
                     )
        # Do not support above 28 using DFUN - would need to use DFNON / DFNOF instead
        else:
            print ("Functions above 28 are not supported")
            return None
        #print (f"Returning {byte1}, {byte2}")
        return [byte1, byte2]
    
    # Return the loco data which is already a dict
    def to_dict (self):
        return self.loco_data
    
    
    # Use this to normally create the class
    @classmethod
    def from_file (cls, loco_file):
        # create a initial entry
        new_loco = cls()
        new_loco.load_file (loco_file)
        return new_loco