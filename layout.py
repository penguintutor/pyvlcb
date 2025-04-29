# Holds specific information about the layout
# particularly useful for giving friendly names
# to replace nodeIDs
class Layout:
    def __init__ (self):
        self.node_names = {
            300: "Solenoid1",
            301: "Servo1"
            }
        # 2 dimension node, evid, name
        self.ev_names = {
            0: {22: "Solenoid1"},
            300: {1: "Solenoid01", 2: "Solenoid02"},
            301: {1: "Servo1"}
            }
        
    def node_name (self, node_id):
        if (node_id in self.node_names.keys()):
            return self.node_names[node_id]
        else:
            return f"Node: {node_id}"
        
    # EV name normally use en, if not in lookup 
    def ev_name (self, node_id, ev_id, en=None):
        if (node_id in self.ev_names.keys() and ev_id in self.ev_names[node_id].keys()):
            return self.ev_names[node_id][ev_id]
        elif en != None:
            return f"{en:#08x}"
        else:
            return f"EV {ev_id}"