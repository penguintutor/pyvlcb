# Holds specific information about the locos
# particularly useful for giving friendly names

class LocoList:
    def __init__ (self):
        self.loco_names = {
            5190: "Prarie",
            1234: "Test"
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
                this_loco += f" {loco_id}"
            return this_loco
        else:
            return f"Loco: {loco_id}"
        
    # Returns all locos using default name format
    # Useful for creating Loco Lis
    def get_all_names (self):
        all_loco_names = []
        for loco_id in self.loco_names.keys():
            all_loco_names.append(self.loco_name(loco_id))
            #print (f"ID {loco_id} - {self.loco_name(loco_id)}")
        return all_loco_names
        
        
    