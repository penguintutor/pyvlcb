import unittest

import os, sys
# Setup PySide6 environment for testing
from PySide6.QtCore import QObject, Signal
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from pyvlcb import VLCB
from vlcbformat import VLCBformat, VLCBopcode
from loco import Loco
from guiobject import GuiObject
from devicemodel import device_model

from appvar import AppVar
from varevent import VarEvent
from automationsequence import AutomationSequence, AutomationStep
from automationrule import AutomationRule

# A global QApplication instance is required for signal/slot testing
app = QApplication.instance() or QApplication(sys.argv)

# Import the module to be tested
# We specifically import the module-level singleton instance
from eventbus import EventBus, serialize_event, deserialize_event, event_bus


## Test creation of rules, including importing and handling recursion
class TestAutomationRules(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
        
    def test_sequence_1 (self):
        # Set Signal spy to watch for signal sent to device
        dev_spy = QSignalSpy(event_bus.device_event_signal)
        app_spy = QSignalSpy(event_bus.app_event_signal)
        
        steps = []
        
        # Create a dict for a rule: 
        rule0 = {"type": "Rule", "name": "Set point 1 to A", "ruletype": "VLCB", "node_id":301, "event": 1, "value": 1}
        rule1 = {"type": "Rule", "name": "Set point 1 to B", "ruletype": "VLCB", "node_id":301, "event": 1, "value": 0}
        # This is an unusual thing for automation, but allows testing of an AppEvent 
        rule2 = {"type": "Rule", "name": "Show Console", "ruletype": "App", "action":"showconsole"}
        
        # Combine steps into sequence
        steps.append(rule0)
        steps.append(rule1)
        steps.append(rule2)
        
        # Create a rule - needs values for the Event
        sequence_1 = AutomationSequence ("Test sequence 1", steps, {})
        
        # Run the sequence
        sequence_1.run()
        
        # Test that the event_bus count has increased, that it equals the event we created
        # and that the values match the expected string
        self.assertEqual(dev_spy.count(), 2)
        self.assertEqual(dev_spy.at(0)[0], sequence_1.steps[0].rule.event)



    # Test with a simple loop
    def test_sequence_loop (self):
        # Set Signal spy to watch for signal sent to device
        dev_spy = QSignalSpy(event_bus.device_event_signal)
        var_spy = QSignalSpy(event_bus.var_event_signal)
        
        appvariables = AppVar (event_bus.var_event_signal)
        
        steps = []
        
        # Create a dict for a rule: 
        rule0 = {"type": "Rule", "name": "Set point 1 to A", "ruletype": "VLCB", "node_id":301, "event": 1, "value": 1}
        rule1 = {"type": "Rule", "name": "Set point 1 to B", "ruletype": "VLCB", "node_id":301, "event": 1, "value": 0}
        
        # Combine steps into sequence
        steps.append(rule0)
        steps.append(rule1)
        
        # Create a rule - needs values for the Event
        sequence_1 = AutomationSequence ("Test sequence 1", steps, {"appvar": appvariables})
        
        # Run the sequence
        sequence_1.run()
        
        # Test that the event_bus count has increased, that it equals the event we created
        # and that the values match the expected string
        self.assertEqual(dev_spy.count(), 2)
        self.assertEqual(dev_spy.at(0)[0], sequence_1.steps[0].rule.event)
        self.assertEqual(str(dev_spy.at(0)[0]), "VLCB 301 1 1")
        self.assertEqual(dev_spy.at(1)[0], sequence_1.steps[1].rule.event)
        self.assertEqual(str(dev_spy.at(1)[0]), "VLCB 301 1 0")

                
if __name__ == '__main__':
    unittest.main()