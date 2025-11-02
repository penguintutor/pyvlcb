
# Automation routine, composed of multiple steps
# Each step is a rule, command or launch another sequence
# These are provided as a list with each entry as a dict with the AutomationStep
class AutomationSequence:
    def __init__(self, title, steps, settings = {}):
        self.title = title
        self.steps = steps  # List of AutomationStep objects
        self.settings = settings
        if num_locos in settings:
            self.num_locos = settings['num_locos'] # 1, 2, or 3 locos required

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
    def __init__(self, parent, step_type, step_name, settings={}):
        self.parent = parent #parent sequence
        self.step_type = data["type"]
        self.step_name = data["name"]
        self.data = data
        
        # If the step_type is a rule then create an automation rule
        if self.step_type == "Rule":
            self.rule = AutomationRule(step_name, step_type, data)
            
            
    def run (self):
        if self.step_type == "Rule":
            self.rule.run()
        
        
    def __repr__(self):
        return f"Step: {self.step_type}: {self.step_name}"
