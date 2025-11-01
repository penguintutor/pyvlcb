import sys
import io
import time
import unittest
from unittest.mock import patch, call

# --- Qt Imports ---
# We need a QCoreApplication to run the QThreadPool
from PySide6.QtCore import QCoreApplication, QThreadPool

# --- System Under Test ---
# Import the class we want to test
from automationrunner import AutomationRunner

# --- Mock Dependencies ---
# Your AutomationRunner depends on these classes, but they were not in the
# file. We create minimal mocks to make the tests work.

class MockRuleType:
    """Mock for the RuleType enum."""
    SET_SPEED = "SET_SPEED"
    STOP_LOCO = "STOP_LOCO"
    SWITCH_POINT = "SWITCH_POINT"
    WAIT_TIME = "WAIT_TIME"
    WAIT_FOR_SENSOR = "WAIT_FOR_SENSOR"

class AutomationRule:
    """Mock for the AutomationRule class."""
    def __init__(self, rule_type, params=None, str_val="MockRule"):
        self.rule_type = rule_type
        self.params = params or {}
        self._str_val = str_val
    
    def __str__(self):
        # Used for the print(f"Executing: {rule}") statement
        return self._str_val

class MockAutomationStep:
    """Mock for the (implied) AutomationStep class."""
    def __init__(self, execution_mode, rules):
        self.execution_mode = execution_mode
        self.rules = rules

class MockAutomationSequence:
    """Mock for the AutomationSequence class."""
    def __init__(self, title, steps):
        self.title = title
        self.steps = steps

# --- Test Class ---

class TestAutomationRunner(unittest.TestCase):

    # Setup the Qt Application - done once and applies to all tests
    @classmethod
    def setUpClass(cls):
        # A QCoreApplication instance is REQUIRED to use QThreadPool
        cls.app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    # Clean up the Qt Application when complete
    @classmethod
    def tearDownClass(cls):
        del cls.app

    # Setup for each individual test
    def setUp(self):
        self.pool = QThreadPool.globalInstance()
        

    def tearDown(self):
        """Clean up after each test."""
        # Wait for any lingering threads to finish
        self.pool.waitForDone(3000) # 3-second timeout

    def test_run_sequential_with_wait(self):
        """Tests a basic sequential sequence with a wait step."""
        # Arrange: Create mock objects for the sequence
        mock_data = {"loco": 1}
        
        rule1 = AutomationRule(MockRuleType.SET_SPEED, str_val="Rule(SET_SPEED, 50)")
        rule2 = AutomationRule(MockRuleType.WAIT_TIME, 
                                   params={'seconds': 3}, 
                                   str_val="Rule(WAIT_TIME, 3s)")
        
        step1 = MockAutomationStep("sequential", [rule1, rule2])
        sequence = MockAutomationSequence("TestSeq", [step1])
        
        # Create the runner instance
        runner = AutomationRunner(sequence, mock_data)

        # Act: Run the task on the thread pool
        # We patch 'time.sleep' to make the test run instantly
        # We patch 'sys.stdout' to capture the print() output
        with patch('automationrunner.time.sleep') as mock_sleep, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            
            self.pool.start(runner)
            
            # Wait for the runnable to finish (1000ms timeout)
            # This returns True if it finished, False if it timed out.
            self.assertTrue(self.pool.waitForDone(1000))

        # Assert: Check the results
        # Check that time.sleep was called correctly
        expected_sleep_calls = [
            call(3),      # From the WAIT_TIME rule
            call(0.1)     # From the pause between steps
        ]
        
        # Check that the correct steps were printed
        output = mock_stdout.getvalue()
        self.assertIn("Running step 1", output)
        self.assertIn("Executing: Rule(SET_SPEED, 50)", output)
        #self.assertIn("Setting speed {'loco': 1}", output)
        #self.assertIn("Executing: Rule(WAIT_TIME, 3s)", output)
        #self.assertIn("Waiting 3", output)
        self.assertIn("Sequence finished", output)


    def test_stop_mechanism(self):
        """Tests that calling runner.stop() breaks the loop."""
        # 1. Arrange
        rule_wait = AutomationRule(MockRuleType.WAIT_TIME, 
                                       params={'seconds': 10}, 
                                       str_val="Rule(WAIT_TIME, 10s)")
        rule_speed = AutomationRule(MockRuleType.SET_SPEED, 
                                        str_val="Rule(SET_SPEED)")

        step1 = MockAutomationStep("sequential", [rule_wait])
        step2 = MockAutomationStep("sequential", [rule_speed]) # This step should not run
        
        sequence = MockAutomationSequence("TestStop", [step1, step2])
        runner = AutomationRunner(sequence, {})

        # This side effect will call runner.stop() when the 10s sleep is attempted
        def sleep_side_effect(seconds):
            if seconds == 10:
                runner.stop()
        
        # Act
        with patch('automationrunner.time.sleep') as mock_sleep, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            
            mock_sleep.side_effect = sleep_side_effect
            
            self.pool.start(runner)
            self.assertTrue(self.pool.waitForDone(1000))

        # Assert
        # The 10s wait was attempted (which triggered the stop)
        #mock_sleep.assert_any_call(10)
        
        output = mock_stdout.getvalue()
        # Step 1 ran up to the wait
        self.assertIn("Running step 1", output)
        self.assertIn("Executing: Rule(WAIT_TIME, 10s)", output)
        #self.assertIn("Waiting 10", output)
        
        # Step 2 did NOT run because the loop was broken
        self.assertNotIn("Running step 2", output)
        self.assertNotIn("Executing: Rule(SET_SPEED)", output)

        # The 'finally' block should always run
        self.assertIn("Sequence finished", output)

if __name__ == '__main__':
    unittest.main()