# Holds specific information about the locos
# particularly useful for giving friendly names

class LocoList:
    def __init__ (self):
        self.loco_names = {
            5190: "Prarie"
            }
        
    
    # get list of locos by keys (id)
    def get_locos (self):
        return self.loco_names.keys()
    
    # Returns loco name - option hide_id will not show the ID
    # Normally do want to include that
    # Cannot exclude if no name
    def loco_name (self, loco_id, hide_id=False):
        if (loco_id in self.loco_names.keys()):
            this_loco = self.loco_names[loco_id]
            if hide_id == False:
                this_logo += f" {loco_id}"
        else:
            return f"Loco: {loco_id}"
        
    