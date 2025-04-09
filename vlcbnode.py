
#ManufId,ModId,Flags
# Stores Nodes defined / discovered
class VLCBNode():
    def __init__ (self, node_id, manuf_id, mod_id, flags):
        self.node_id = node_id
        self.manuf_id = manuf_id
        self.mod_id = mod_id
        self.flags = flags
        self.events = []
        
    