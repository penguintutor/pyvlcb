import unittest

import os, sys
# Setup PySide6 environment for testing
from PySide6.QtCore import QObject
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from pyvlcb import VLCB
from vlcbformat import VLCBformat, VLCBopcode
from loco import Loco
from guiobject import GuiObject
from devicemodel import device_model

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
        



    # Test the very basic rule elements
    # Each event type is tested
    def test_rule_dev_1 (self):
        # Set Signal spy to watch for signal sent to device
        dev_spy = QSignalSpy(event_bus.device_event_signal)
        
        # Create a rule - needs values for the Event
        dev_rule = AutomationRule ("Set point 1 to A", "VLCB", {"node_id":301, "event": 1, "value": 1})
        
        dev_rule.run()
        
        # Test that the event_bus count has increased, that it equals the event we created
        # and that the values match the expected string
        self.assertEqual(dev_spy.count(), 1)
        #Detect 
        self.assertEqual(dev_spy.at(0)[0], dev_rule.event)
        self.assertEqual(str(dev_spy.at(0)[0]), "VLCB 301 1 1")
        
        

                
if __name__ == '__main__':
    unittest.main()