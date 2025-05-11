# Holds a loco session

class Loco:
    # All arguments have default allowing creation of a dummy loco
    def __init__ (self, loco_id=0, session=0, direction=1, speed=0):
        self.status = "off"   # Starts in off status - change to on when allocated
        self.loco_id = loco_id
        self.session = session # If session == 0 then no session allocated (don't support none DCC)
        self.direction = direction # 1 = forward, 0 = reverse
        self.speed = speed #(0 to 127) - 1 = emergency stop (skip in normal use)
    
    def released (self):
        self.status = "off"
        self.session = 0
        
    def session_established (self, session):
        # Add session id to the loco
        self.status = on
        self.session = session
        
    # get Dir/Speed combined value
    def get_speed_dir (self):
        return (self.direction * 0x80) + self.speed
    
    # Takes combined speed & dir and updates direction / speed
    def set_speed_dir (self, speed_dir):
        self.direction = speed_dir >> 7
        self.speed = speed_dir & 0x7F
        
    # Not currently included
    # Todo add functions
    def set_functions (self, fn1, fn2, fn3):
        pass
        
    