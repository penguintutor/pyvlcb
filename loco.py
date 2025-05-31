# Holds a loco session

class Loco:
    # All arguments have default allowing creation of a dummy loco
    def __init__ (self, loco_id=0, session=0, direction=1, speed=0):
        # status tarts in off, change to rloc when rloc sent, then on when allocated
        # if error after ploc then set to off
        # if gloc then set status to gloc - and then on after aquire (ploc)
        self.status = "off"   
        self.loco_id = loco_id
        self.session = session # If session == 0 then no session allocated (don't support none DCC)
        self.direction = direction # 1 = forward, 0 = reverse
        self.speed = speed # Allow 0 to 128 but maximum sent is 127. Speed 1 = emergency stop (not used - instead status = stop)
    
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
        speed = self.speed
        if self.speed > 127:
            speed = 127
        return (self.direction * 0x80) + speed
    
    # Takes combined speed & dir and updates direction / speed
    # This is often used based on external values, so add 1
    def set_speeddir (self, speed_dir):
        speed = self.speed
        self.direction = speed_dir >> 7
        self.speed = speed_dir & 0x7F
        if self.speed > 1:
            self.speed += 1
        
      
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
        
    # Not currently included
    # Todo add functions
    def set_functions (self, fn1, fn2, fn3):
        pass
    

    