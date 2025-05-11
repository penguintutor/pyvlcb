# Holds a loco session

class Loco:
    # All arguments have default allowing creation of a dummy loco
    def __init__ (self, loco_id=0, session=0, direction=1, speed=0):
        self.status = "off"   # Starts in off status - change to on when allocated
        self.loco_id = loco_id
        self.session = session # If session == 0 then no session allocated (don't support none DCC)
        self.direction = direction # 1 = forward, 0 = reverse
        self.speed = speed #(0 to 127) - 1 = emergency stop (skip in normal use)
        # Actual values are updated based on responses but only LCD is updated
        self.actual_direction = 1
        self.actual_speed = 0
    
    def released (self):
        self.status = "off"
        self.session = 0
        
    def session_established (self, session):
        # Add session id to the loco
        self.status = on
        self.session = session
        
    # get Dir/Speed combined value
    def get_speeddir (self):
        return (self.direction * 0x80) + self.speed
    
    # Takes combined speed & dir and updates direction / speed
    def set_speeddir (self, speed_dir):
        self.direction = speed_dir >> 7
        self.speed = speed_dir & 0x7F
        
    # Sets speed only - keep current direction
    # 0 = stop, 1 = ignored
    # all other values used as is (maximum 127)
    def set_speed (self, speed_value):
        if speed_value == 1 or speed_value > 127 or speed_value < 0:
            return
        self.speed = speed_value
        
    # Not currently included
    # Todo add functions
    def set_functions (self, fn1, fn2, fn3):
        pass
        
    