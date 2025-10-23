# test_eventbus.py
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Setup PySide6 environment for testin
from PySide6.QtCore import QObject
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

# Get the directory of the run_tests.py file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root directory
project_root = os.path.join(current_dir, '..')
# Add the project root to the system path
sys.path.insert(0, project_root)

# Import from application
from deviceevent import DeviceEvent
from appevent import AppEvent
from guievent import GuiEvent
from locoevent import LocoEvent
from timerevent import TimerEvent

# A global QApplication instance is required for signal/slot testing
app = QApplication.instance() or QApplication(sys.argv)

# ---
# Mock definitions for missing imports (Event, AppEvent, etc.)
# ---
# These mocks simulate the behavior needed by the EventBus,
# specifically the __init__, __dict__, and matches methods.

class Event:
    def __init__(self, data=None):
        if data:
            self.event_type = data.get("event_type")
            self.value = data.get("value")
        else:
            self.event_type = "Generic"
            self.value = None

    def __dict__(self):
        # Used by serialize_event
        return {"event_type": self.event_type, "value": self.value}

    def matches(self, other_event):
        # Simple match logic for testing:
        # Match if type is the same and value is the same.
        return (isinstance(other_event, type(self)) and
                self.value == other_event.value)

    def __eq__(self, other):
        # Useful for assertions
        return isinstance(other, type(self)) and self.__dict__() == other.__dict__()

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"


# Patch sys.modules BEFORE importing the eventbus
# This injects our mock classes so the import succeeds
sys.modules['event'] = MagicMock(Event=Event)


# Now, import the module to be tested
# We specifically import the module-level singleton instance
from eventbus import EventBus, serialize_event, deserialize_event, event_bus

class TestEventBus(unittest.TestCase):

    def setUp(self):
        # Get the singleton instance and reset its state for each test
        self.bus = event_bus
        self.bus.event_rules = []
        self.bus.automation_enabled = True
        self.bus.automation_count = 0
        self.bus.max_automation_count = 100 # Reset to default
        self.test_filename = "test_rules.json"

    def tearDown(self):
        # Clean up any created files
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
        # FIXED: Removed disconnect from here to avoid RuntimeWarning
        # The only test that connects this signal will now disconnect it.

    def test_singleton_instance(self):
        # FIXED: Don't call EventBus() constructor again.
        # Instead, import the module 'eventbus' again and check
        # that the 'event_bus' instance from it is the *same object*
        # as the one we got in setUp. This proves it's a singleton.
        import eventbus
        bus_again = eventbus.event_bus
        self.assertIs(self.bus, bus_again, "Imported event_bus should always be the same instance")
        self.assertIs(self.bus, event_bus, "Global event_bus should be the same as self.bus")

    def test_broadcast_signals(self):
        # Test that broadcast emits the correct signal for each event type
        app_event = AppEvent("showconsole")
        dev_event = DeviceEvent({"title":"Test dev event"})
        gui_event = GuiEvent({"title":"Test Gui event"})
        loco_event = LocoEvent("ERR", {"title":"Test Loco event"})
        timer_event = TimerEvent("timer", {"title":"Test timer event"})

        # Create QSignalSpy instances for each signal
        app_spy = QSignalSpy(self.bus.app_event_signal)
        dev_spy = QSignalSpy(self.bus.device_event_signal)
        gui_spy = QSignalSpy(self.bus.gui_event_signal)
        loco_spy = QSignalSpy(self.bus.loco_event_signal)
        timer_spy = QSignalSpy(self.bus.timer_event_signal)

        # Broadcast one of each event
        self.bus.broadcast(app_event)
        self.bus.broadcast(dev_event)
        self.bus.broadcast(gui_event)
        self.bus.broadcast(loco_event)
        self.bus.broadcast(timer_event)

        # Disable test #todo
        self.assertEqual(1,1)
        
        self.assertEqual(app_spy.count(), 1)
        self.assertEqual(dev_spy.count(), 1)
        self.assertEqual(gui_spy.count(), 1)
        self.assertEqual(loco_spy.count(), 1)
        self.assertEqual(timer_spy.count(), 1)

        self.assertEqual(app_spy.at(0)[0], app_event)
        self.assertEqual(dev_spy.at(0)[0], dev_event)
        self.assertEqual(gui_spy.at(0)[0], gui_event)
        self.assertEqual(loco_spy.at(0)[0], loco_event)
        self.assertEqual(timer_spy.at(0)[0], timer_event)

    def test_rule_management(self):
        self.assertEqual(self.bus.num_rules(), 0)

        # Add rule 1
        event1 = DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10})
        action1 = GuiEvent({"title":"Test Gui event"})
        self.bus.add_rule(event1, action1)
        self.assertEqual(self.bus.num_rules(), 1)
        self.assertEqual(self.bus.event_rules[0][0], event1)
        self.assertEqual(self.bus.event_rules[0][1], action1)

        # Add rule 2
        event2 = AppEvent("showconsole", {"Title":"App Event"})
        action2 = LocoEvent("ERR", {"title":"Test Loco event"})
        self.bus.add_rule(event2, action2)
        self.assertEqual(self.bus.num_rules(), 2)

        # Test del_entry (deletes by index)
        self.bus.del_entry(0) # Delete the first rule
        self.assertEqual(self.bus.num_rules(), 1)
        self.assertEqual(self.bus.event_rules[0][0], event2) # Check remaining rule
        self.assertEqual(self.bus.event_rules[0][1], action2)

    def test_consume_applies_rules(self):
        # 'consume' should apply rules but NOT broadcast the original event
        trigger = DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10})
        action = GuiEvent({"title":"Test Gui event"})
        self.bus.add_rule(trigger, action)

        gui_spy = QSignalSpy(self.bus.gui_event_signal)
        dev_spy = QSignalSpy(self.bus.device_event_signal)

        # Consume the event
        self.bus.consume(trigger)

        # Use .count()
        # Assert: The action event should be broadcast
        self.assertEqual(gui_spy.count(), 1, "Action event should be broadcast")
        # FIXED: Use .pop(0)[0]
        self.assertEqual(gui_spy.at(0)[0], action)

        # Assert: The original event should NOT be broadcast
        self.assertEqual(dev_spy.count(), 0, "Original event should not be broadcast by consume")

    def test_publish_applies_rules_and_broadcasts(self):
        # 'publish' should BOTH apply rules AND broadcast the original event
        trigger = DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10})
        action = GuiEvent({"title":"Test Gui event"})
        self.bus.add_rule(trigger, action)

        dev_spy = QSignalSpy(self.bus.device_event_signal)
        gui_spy = QSignalSpy(self.bus.gui_event_signal)

        # Publish the trigger event
        self.bus.publish(trigger)

        # Use .count()
        # Assert: The original event (trigger) was broadcast
        self.assertEqual(dev_spy.count(), 1, "Original event should be broadcast by publish")
        # FIXED: Use .pop(0)[0]
        self.assertEqual(dev_spy.at(0)[0], trigger)

        # Assert: The rule's action (action) was ALSO broadcast
        self.assertEqual(gui_spy.count(), 1, "Action event should be broadcast by rule")
        # FIXED: Use .pop(0)[0]
        self.assertEqual(gui_spy.at(0)[0], action)

    def test_consume_automation_disabled(self):
        self.bus.automation_enabled = False

        trigger = DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10})
        action = GuiEvent({"title":"Test Gui event"})
        self.bus.add_rule(trigger, action)

        gui_spy = QSignalSpy(self.bus.gui_event_signal)

        self.bus.consume(trigger)

        # Use .count()
        # Assert: No signals fired because automation is off
        self.assertEqual(gui_spy.count(), 0)

    def test_rule_matching_logic(self):
        # Rule: DeviceEvent(value=10) -> GuiEvent(value=20)
        trigger = DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10})
        action = GuiEvent({"title":"Test Gui event"})
        self.bus.add_rule(trigger, action)

        gui_spy = QSignalSpy(self.bus.gui_event_signal)

        # 1. Test match
        self.bus.consume(DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10}))
        self.assertEqual(gui_spy.count(), 1)
        self.assertEqual(gui_spy.at(0)[0], action)

        # 2. Test no match (wrong value)
        self.bus.consume(DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':22}))
        # prev event is on so still only 1
        self.assertEqual(gui_spy.count(), 1)

        # 3. Test no match (wrong type)
        self.bus.consume(AppEvent("showconsole"))
        self.assertEqual(gui_spy.count(), 1)

#     def test_automation_limit(self):
#         test_limit = 5
#         self.bus.max_automation_count = test_limit
# 
#         # Create a recursive rule: App(1) -> App(1)
#         recursive_trigger = AppEvent("Another test")
#         self.bus.add_rule(recursive_trigger, recursive_trigger)
# 
#         app_spy = QSignalSpy(self.bus.app_event_signal)
# 
#         # Connect the broadcast signal back to 'consume' to create a loop
#         self.bus.app_event_signal.connect(self.bus.consume)
# 
#         self.assertTrue(self.bus.automation_enabled)
# 
#         # Use try/finally to ensure disconnect
#         try:
#             with patch('builtins.print') as mock_print:
#                 self.bus.consume(recursive_trigger)
#                 # Check that the warning was printed
#                 mock_print.assert_called_with("*** Warning automation events exceeded ***")
# 
#             # Check assertions
#             self.assertFalse(self.bus.automation_enabled, "Automation should be disabled")
#             # Use .count()
#             self.assertEqual(app_spy.count(), test_limit, f"Signal should fire {test_limit} times")
#             # The count increments and decrements, so it should be 0 after stack unwinds
#             self.assertEqual(self.bus.automation_count, 0)
#         finally:
#             # Disconnect the signal here, inside the test that connected it
#             self.bus.app_event_signal.disconnect(self.bus.consume)


## Not currently implemented - perhaps not required 
#     def test_serialization_helpers(self):
#         # Test serialize_event
#         event = AppEvent("showconsole")
#         data = serialize_event(event)
#         self.assertEqual(data, {"event_type": "App", "value": "test_serialize"})
# 
#         # Test deserialize_event
#         deserialized = deserialize_event(data)
#         self.assertIsInstance(deserialized, AppEvent)
#         self.assertEqual(deserialized.value, "test_serialize")
# 
#         # Test with a different type
#         data_dev = {"event_type": "Device", "value": 123}
#         deserialized_dev = deserialize_event(data_dev)
#         self.assertIsInstance(deserialized_dev, DeviceEvent)
#         self.assertEqual(deserialized_dev.value, 123)
# 
#     def test_serialize_event_error(self):
#         class NotAnEvent:
#             pass
#         with self.assertRaises(TypeError):
#             serialize_event(NotAnEvent())

    def test_save_and_load_rules(self):
        # 1. Add rules
        rule1_event = DeviceEvent({"title":"Test dev event", 'node_id':100, 'event_id':10})
        rule1_action = GuiEvent({"title":"Test Gui event"})
        rule2_event = AppEvent("showconsole")
        rule2_action = LocoEvent("ERR", {"title":"Test Loco event"})
        self.bus.add_rule(rule1_event, rule1_action)
        self.bus.add_rule(rule2_event, rule2_action)

        # 2. Save rules
        # This first call to load_rules is expected to print "File not found"
        # as it just sets the filename
        with patch('builtins.print') as mock_print:
            self.bus.load_rules(self.test_filename)
            mock_print.assert_called_with(f"File not found {self.test_filename}")