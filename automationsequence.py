from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThread, QThreadPool
import time
import json
from automationrule import AutomationRule
from appvar import AppVar

# Helper QObject to hold signals (QRunnable cannot have signals)
class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

# Automation routine, composed of multiple steps
# Each step is a rule, command or launch another sequence
# These are provided as a list with each entry as a dict with the AutomationStep created in the init
# Settings is used to pass the locos,
class AutomationSequence (QRunnable):
    def __init__(self, appvariables, title, steps, settings = {}):
        # steps are provided as a list so save as list_steps, but then use self.steps when AutomationStep object created
        list_steps = steps
        #self.mainwindow = mainwindow
        self.vars = appvariables
        self.title = title
        self.steps = []  # List of AutomationStep objects
        self.settings = settings
        self.num_locos = settings.get('num_locos', 0) # 0 to 3 locos required
        #self.vars = settings.get("appvar", {})
        #if mainwindow != None:
        #    self.vars = self.mainwindow.appvariables
        #else:
        #    self.vars = None
        # Store the index of any labels to allow jumps (loops)
        # If order changes then labels needs to be updated
        self.labels = {}
        self.signals = WorkerSignals()
        self.active = False		# Set to true when starting, set back to false to stop
        
        # Each step contains self.step = {"step_type": rule_type, "step_name": step_name, data : data_dict}
        for i, step_data in enumerate(list_steps):
            #print (f"{step_data}")
            # If it's a label then add to dict of labels
            if step_data['type'] == "Label":
                self.labels[step_data['name']] = i
                #print (f"Adding label {step_data['name']}")
                #print (f"Labels : {self.labels}")
            # Include the vars in the step
            # Vars are accessed from the parent, so no need to pass 
            #if self.vars != None:
            #    step_data['appvar'] = self.vars
            #print (f"Step data {step_data}")
            #print (f"Name {step_data['name']}")
            self.steps.append(AutomationStep(self.vars, step_data['type'], step_data['name'], step_data))
         
    @Slot()
    def run (self):
        print ("Starting sequence")
        self.active = True
        position = 0
        while position < len(self.steps):
            # If set to false then stop
            if self.active == False:
                break
            print (f"Step {position}")
            # If it's a label then ignore
            if self.steps[position].step_type == "Label":
                pass
            elif self.steps[position].step_type == "Jump":
                # parse the condition and get the result
                result = self.steps[position].test_condition()
                # If the result is in the labels then jump to that 
                if result != None and result == True:
                    #print ("Test true")
                    label = self.steps[position].data.get("label")
                    #print (f"Label {label}")
                    if label != None and label in self.labels:
                        #print ("Jump to label")
                        position = self.labels[label]
                        continue
                # otherwise jump is ignored (eg. if loop then until no longer met)
            else:
                # Otherwise run it  
                self.steps[position].run()
            position += 1
        # Emit a signal to indicate the thread has finished
        self.signals.finished.emit()

    def to_dict(self) -> dict:
        """Convert AutomationSequence to dict."""
        return {
            "title": self.title,
            "settings": self.settings,
            "steps": [step.to_dict() for step in self.steps]
        }

    def to_json(self) -> str:
        """Serialize AutomationSequence to JSON string."""
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, d: dict, appvariables=None):
        """Create AutomationSequence from dict."""
        #steps = [AutomationStep.from_dict(s, self) for s in d.get("steps", [])]
        steps = d.get("steps", [])
        return cls(
            appvariables=appvariables,
            title=d.get("title", ""),
            steps=steps,
            settings=d.get("settings", {}),
            
        )

    #def __init__(self, mainwindow, title, list_steps, settings = {}):
    # from json also needs mainwindow - pass as optional argument
    @classmethod
    def from_json(cls, json_str: str, mainwindow=None):
        """Deserialize JSON string to AutomationSequence."""
        d = json.loads(json_str)
        return cls.from_dict(d, mainwindow)

    def __repr__(self):
        return f"AutomationSequence (title, steps, settings): {self.title} ({self.num_locos} Locos)"
    

    def __str__(self):
        return f"Sequence: {self.title} ({self.num_locos} Locos)"
    
    
    
# Each step contains a rule commands or sequences
# These are created from a dict and then extracted for the Automation Rule
class AutomationStep:
    # sequence is the sequence this is part of (needed for loops etc.)
    # type is Rule, Var (plus operation), Label, Loop, Sequence
    # name is the name passed to the rule, or in the case of the label is the actual label
    # all other parameters are included in settings
    # rule is not normally provided - unless loading from json
    # Only used if this has an instance of AutomationRule
    def __init__(self, appvariables, step_type, step_name, data={}, rule=None):
        #print (f"Creating step with {data}")
        #self.parent = parent #parent sequence
        #self.mainwindow = self.parent.mainwindow
        #self.step_type = data["type"]
        self.step_type = step_type
        #self.step_name = data["name"]
        self.step_name = step_name
        self.data = data
        #self.vars = data['appvars']
        #self.vars = self.mainwindow.appvariables
        self.vars = appvariables
        self.rule = rule # Only used if this has an instance of AutomationRule
        
        # If the step_type is a rule then create an automation rule
        if self.rule == None and self.step_type == "Rule":
            #self.rule = AutomationRule(self.step_name, self.step_type, self.data)
            # If ruletype not in the step then look in step.data['data']
            ruletype = self.data.get('ruletype', '')
            if ruletype == "":
                #print (f"* Rule {self.data}")
                ruletype = self.data['data'].get('ruletype', '')
            self.rule = AutomationRule(self.step_name, ruletype, self.data)
        #  Variables are not created / updated here - only when run

            
    def parse_var (self):
        # Copy data dict to run_data - which allows for any variable substitutions
        run_data = {}
        var_data = False # If parse a variable then set to True to indicate updated
        for key, value in self.data.items():           
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_data = True
                var_name = value[2:-1]
                if vars == None:
                    print ("Variable detected {var_name} but no AppVar created")
                    continue
                # If the value doesn't exist then it will be None
                run_data[key] = self.vars.get_variable(var_name)
            else:
                run_data[key] = value
        # If a substitution has been made then temporarily add it to the dict
        # so that the calling method knows a substitution has been made
        if var_data:
            run_data["var_data"] = True
        return run_data

    # If any variable tokens are found they are handled in the run        
    def run (self):
        run_data = self.parse_var()
        # Now use run_data - which has any variables parsed
        if self.step_type == "Rule":
            # check any value fields for variables
            if ("var_data" in run_data and run_data["var_data"]):
                # remove it from the dict
                del run_data['var_data']
                # If new data (ie. variable) then replace data within the rule object
                self.rule.run(run_data)
            else:
                self.rule.run()
        # Variable can be "set" (which create or set value)
        # or "inc" - allows increase without needing to query current value
        elif self.step_type == "Var":
            # check we have an appvar
            if self.vars == None:
                print ("Warning: Attempt to set a variable with no AppVar configured")
                return
            if run_data["action"] == "set":
                self.vars.set_variable(run_data["varname"], run_data["value"])
            elif run_data["action"] == "inc":
                # value is optional for inc - default to 1
                self.vars.inc_variable(run_data["varname"], run_data.get("value",1))
        elif self.step_type == "Wait":
            # default 1 second
            delay_time = self.data.get("time", 1)
            # If this is a basic wait / delay (which is default) then sleep and continue
            waittype = self.data.get("waittype", "delay")
            if waittype == "delay":
                time.sleep(delay_time)
            else:
                loop_num = 0
                # max_loop 0 means no maximum (keep looping)
                # this is not subject to variable substitution 
                max_loop = self.data.get("maxloop", 0)
                # Create a loop until the condition is met
                while test_condition():
                    time.sleep(delay_time)
                    loop_num += 1
                    if max_loop > 0 and loop_num > max_loop:
                        break

    # Test condition is used for any check operations eg. 
    # "test": "equals" "==" or "lessthan" "<" or "greaterthan" ">", or 
    # "notequal" "!=" or "<=" or ">=" (no long version of those)
    # Returns True / False
    def test_condition (self):
        # first substitute in any variables
        run_data = self.parse_var()
        # Now test the condition
        condition = run_data.get("test")
        value1 = run_data.get("value1")
        value2 = run_data.get("value2")
        
        #print (f"Test {value1} {condition} {value2}")
        
        # if any of the values are not varlid then return False
        if (condition == None or value1 == None or value2 == None):
            return False
        # Now perform the check
        if (condition == "equal" or condition == "=="):
            return (value1 == value2)
        elif (condition == "notequal" or condition == "!="):
            return (value1 != value2)
        elif (condition == "lessthan" or condition == "<"):
            return (value1 < value2)
        elif (condition == "greaterthan" or condition == ">"):
            return (value1 > value2)
        elif (condition == ">="):
            return (value1 >= value2)
        elif (condition == "<="):
            return (value1 <= value2)
        else:
            return False
        
    def get_type (self):
        return self.step_type
        
    def get_name (self):
        return self.step_name

    def __repr__(self):
        return f"Step: {self.step_type}: {self.step_name}"
    
    

    def to_dict(self) -> dict:
        """Convert the object to a dictionary, excluding 'appvar' from data."""
        filtered_data = {k: v for k, v in self.data.items() if k != 'appvar'}
        return {
            "type": self.step_type,
            "name": self.step_name,
            "data": filtered_data,
            "rule": self.rule.to_dict() if self.rule else None
        }

    # Json created at Sequence
    #def to_json(self) -> str:
    #    """Serialize the object to a JSON string."""
    #    return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, d: dict, parent = None):
        """Create an object from a dictionary."""
        return cls(
            parent=parent,
            step_type=d.get("step_type", ""),
            step_name=d.get("step_name", ""),
            data=d.get("data", {}),
            rule=d.get("rule", None)
        )

    @classmethod
    def from_json(cls, json_str: str, parent = None):
        """Deserialize from JSON string to object."""
        d = json.loads(json_str)
        return cls.from_dict(d, parent)
