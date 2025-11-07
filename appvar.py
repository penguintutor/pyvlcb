
from devicemodel import device_model
from eventbus import event_bus
from varevent import VarEvent

# Always use getters and setters as they can update device_model and/or trigger events if required
class AppVar():
    def __init__ (self, varsignal):
        # Variables in a dict with the variable name as the key
        self.variables={}

    def get_variable (self, variable_name):
        if variable_name in self.variables:
            return self.variables[variable_name]
        else:
            return None
        
    def set_variable (self, variable_name, new_value):
        # Does variable already exist - if so need to trigger new event (if not then change event)
        if variable_name in self.variables:    
            event_type = "change"
        else:
            event_type = "new"
        self.variables[variable_name] = new_value
        var_event = VarEvent ({"name":variable_name, "value":new_value, "event_type": event_type})
        event_bus.broadcast(var_event)
        # Return value - to be consistant with inc_variable
        return new_value
        
    # Increase variable - if variable does not exist or is not a number then replace with 1
    # Returns new variable
    def inc_variable (self, variable_name, inc_amount=1):
        if variable_name in self.variables:    
            event_type = "change"
        else:
            event_type = "new"
        # Use try and if unable to increase value (new or not number) then set to 1
        try:
            #print (f"Updating {variable_name} adding {inc_amount} to {self.variables[variable_name]}")
            self.variables[variable_name] += inc_amount
        except:
            #print ("Exception")
            self.variables[variable_name] = 1
        var_event = VarEvent ({"name":variable_name, "value":self.variables[variable_name], "event_type": event_type})
        event_bus.broadcast(var_event)
        return self.variables[variable_name]