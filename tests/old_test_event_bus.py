# test_event_bus.py
import unittest
import sys

# We need QCoreApplication for the event loop
from PySide6.QtCore import QCoreApplication, Qt

# To use QSignalSpy first install Pyside6.QtTest libraries
# sudo apt install python3-pyside6.qttest

# QSignalSpy is the best tool for testing signals
from PySide6.QtTest import QSignalSpy

# Import the singleton instance and the class to test
from eventbus import event_bus, EventBus

# We need to create a global app instance for our tests
# We use .instance() to avoid creating multiple if one already exists
# (e.g., if run from a larger Qt test suite)
app = QCoreApplication.instance() or QCoreApplication(sys.argv)


class TestEventBus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up the minimal Qt environment once for all tests in this class.
        """
        # We store the app on the class for potential use, 
        # but its main job is just to exist.
        cls.app = app
        #print("QCoreApplication initialized.")

    # Runs before individual tests - can reset so that tests don't interfere if required
    def setUp(self):
        #event_bus.reset()
        pass

    # Test that event_bus is a valid single instance
    def test_singleton_instance(self):
        self.assertIsNotNone(event_bus)
        self.assertIsInstance(event_bus, EventBus)
        
        # Import it again to verify it's the same object
        from eventbus import event_bus as event_bus_2
        self.assertIs(event_bus, event_bus_2)


if __name__ == '__main__':
    unittest.main()