
# Automation routine, composed of multiple steps
class AutomationSequence:
    def __init__(self, title, steps, settings = {}):
        self.title = title
        self.steps = steps  # List of AutomationStep objects
        self.num_locos = settings['num_locos'] # 1, 2, or 3 locos required

    def __repr__(self):
        return f"Sequence: {self.title} ({self.num_locos} Locos)"
    
    
    
# Each step contains one or more rules, commands or sequences
class AutomationStep:
    def __init__(self, rules, settings={}):
        self.rules = rules  # List of AutomationRule objects
