import unittest
import json
import os, sys
# Setup PySide6 environment for testing
from PySide6.QtCore import QObject, Signal
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from appvar import AppVar
from varevent import VarEvent
from automationsequence import AutomationSequence, AutomationStep
from automationstepdialog import AutomationStepDialog
from automationrule import AutomationRule

# A global QApplication instance is required for signal/slot testing
app = QApplication.instance() or QApplication(sys.argv)

# Import the module to be tested
# We specifically import the module-level singleton instance
from eventbus import EventBus, serialize_event, deserialize_event, event_bus

class MockWindow:
    pass

class TestAutomationSequenceSerialization(unittest.TestCase):
    def setUp(self):
        # Mock mainwindow and event bus if needed
        self.mainwindow = MockWindow()
        self.mainwindow.appvariables = AppVar(event_bus.var_event_signal)

    def create_sample_sequence(self):
        # Create a rule
#         rule = AutomationRule("VLCB", {"node_id": 301, "event": 1, "value": 1})
# 
#         # Create steps
#         step1 = AutomationStep("Var", "Create test var", {"varname": "test", "action": "set", "value": 0, "appvar": "temp"})
#         step2 = AutomationStep("Label", ":loopstart", {})
#         step3 = AutomationStep("Rule", "Set point 1 to A", {"node_id": 301, "event": 1, "value": 1}, rule)

        # Need to have a fake mainwindow for testing
        # For testing AutomationSequence / AutomationStep then this only needs to house a link to
        # appvariable
        mainwindow = MockWindow()
        mainwindow.appvariables = AppVar(event_bus.var_event_signal)
        
        steps = [
            {"type": "Var", "name": "Create test var", "varname": "test", "action": "set", "value": 0},
            {"type": "Label", "name": ":loopstart"},
            {"type": "Rule", "name": "Set point 1 to A", "ruletype": "VLCB", "node_id":301, "event": 1, "value": 1},
            {"type": "Var", "name": "Increase test variable by 1", "varname": "test", "action": "inc", "value": 1},
            {"type": "Rule", "name": "Set point 1 to B", "ruletype": "VLCB", "node_id":301, "event": 1, "value": 0},
            {"type": "Jump", "name": "Until loop end (if value1 <= value2 jump)", "test": "<=", "value1": "${test}", "value2": 10, "label": ":loopstart"}
            ]

        #return AutomationSequence("Test save seq", {"retry": True}, [step1, step2, step3])
        return AutomationSequence(mainwindow, "Test save seq", steps, {})

    def test_sequence_serialization_deserialization(self):
        
        # Need to have a fake mainwindow for testing
        # For testing AutomationSequence / AutomationStep then this only needs to house a link to
        # appvariable
        mainwindow = MockWindow()
        mainwindow.appvariables = AppVar(event_bus.var_event_signal)
        
        sequence = self.create_sample_sequence()

        # Serialize to JSON
        json_data = sequence.to_json()
        self.assertIsInstance(json_data, str)

        # Validate JSON structure
        parsed = json.loads(json_data)
        # print (f"Parsed: {parsed}")
        self.assertIn("title", parsed)
        self.assertIn("steps", parsed)
        self.assertEqual(parsed["title"], "Test save seq")
        self.assertEqual(len(parsed["steps"]), 6)

        # Check appvar excluded
        self.assertNotIn("appvar", parsed["steps"][0]["data"])

        # Deserialize back
        new_sequence = AutomationSequence.from_json(json_data, mainwindow)
        self.assertEqual(new_sequence.title, sequence.title)
        self.assertEqual(new_sequence.settings, sequence.settings)
        self.assertEqual(len(new_sequence.steps), len(sequence.steps))

        # Check step details
        self.assertEqual(new_sequence.steps[0].step_name, "Create test var")
        self.assertEqual(new_sequence.steps[2].rule.rule_type, "VLCB")

    def test_empty_steps(self):
        
        # Need to have a fake mainwindow for testing
        # For testing AutomationSequence / AutomationStep then this only needs to house a link to
        # appvariable
        mainwindow = MockWindow()
        mainwindow.appvariables = AppVar(event_bus.var_event_signal)
        
        sequence = AutomationSequence(mainwindow, "Empty Seq", [], {})
        json_data = sequence.to_json()
        new_sequence = AutomationSequence.from_json(json_data, mainwindow)
        self.assertEqual(len(new_sequence.steps), 0)

#     def test_step_without_rule(self):
#         step = AutomationStep("Var", "Simple Step", {"param": 123})
#         self.assertIsNone(step.rule)
#         json_data = json.dumps(step.to_dict())
#         parsed = json.loads(json_data)
#         self.assertIsNone(parsed["rule"])

if __name__ == "__main__":
    unittest.main()
