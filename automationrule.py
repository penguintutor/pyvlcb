


# Automation rule determines the actions
# data is a dict with any additional parameters
# eg. data['loco_id'] is used if the rule controls a loco
class AutomationRule:
    def __init__ (self, rule_name, rule_type, data):
        self.name = rule_name
        self.type = rule_type
        self.data = data
    
    def __repr__(self):
        return (f"Rule {self.rule_type}, {self.data}")
    
