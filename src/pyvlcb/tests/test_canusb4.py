import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure we can import the library if running standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pyvlcb.canusb import CanUSB4
from pyvlcb.exceptions import (
    DeviceConnectionError, 
    InvalidConfigurationError
)

class TestCanUSB4(unittest.TestCase):
    
    def setUp(self):
        # Patch 'serial.Serial' where it is imported IN THE MODULE (pyvlcb.canusb), 
        # not the serial module itself.
        self.serial_patcher = patch('pyvlcb.canusb.serial.Serial')
        self.mock_serial_class = self.serial_patcher.start()
        
        # Create a mock instance that the class will use
        self.mock_serial_instance = MagicMock()
        self.mock_serial_class.return_value = self.mock_serial_instance
        
        # Default successful setup
        self.port = '/dev/ttyTEST'
        self.canusb = CanUSB4(self.port)

    def tearDown(self):
        self.serial_patcher.stop()

    def test_init_valid(self):
        """Test that initialization opens the serial port with correct settings."""
        # Check if serial.Serial was called with correct args
        self.mock_serial_class.assert_called_with(self.port, 115200, timeout=0.01)

    def test_init_empty_port(self):
        """Test that empty port raises InvalidConfigurationError."""
        with self.assertRaises(InvalidConfigurationError):
            CanUSB4('')

    def test_connect_failure(self):
        """Test that serial exception during connect raises DeviceConnectionError."""
        import serial
        # Simulate the constructor raising SerialException
        self.mock_serial_class.side_effect = serial.SerialException("Boom")
        
        with self.assertRaises(DeviceConnectionError):
            CanUSB4('/dev/ttyFAIL')

    def test_send_data_string(self):
        """Test sending a standard string."""
        self.canusb.send_data("hello")
        # Should be encoded to ascii bytes
        self.mock_serial_instance.write.assert_called_with(b"hello")

    def test_send_data_bytes(self):
        """Test sending raw bytes."""
        self.canusb.send_data(b"rawbytes")
        self.mock_serial_instance.write.assert_called_with(b"rawbytes")

    def test_send_data_invalid_chars(self):
        """Test that non-ascii characters raise InvalidConfigurationError."""
        # CanUSB4 uses 'ascii' encoding, so unicode chars should fail
        with self.assertRaises(InvalidConfigurationError):
            self.canusb.send_data("Emoji 🚂")

    def test_send_data_write_failure(self):
        """Test that write failure raises DeviceConnectionError."""
        import serial
        self.mock_serial_instance.write.side_effect = serial.SerialException("Lost connection")
        
        with self.assertRaises(DeviceConnectionError):
            self.canusb.send_data("test")

    def test_read_data_no_data(self):
        """Test reading when no data is waiting."""
        self.mock_serial_instance.in_waiting = 0
        data = self.canusb.read_data()
        self.assertEqual(data, [])

    def test_read_data_complete_packet(self):
        """Test reading a single perfect packet :DATA;"""
        # Simulate 6 bytes waiting
        self.mock_serial_instance.in_waiting = 6
        # Simulate reading those bytes
        self.mock_serial_instance.read.return_value = b':DATA;'
        
        data = self.canusb.read_data()
        self.assertEqual(data, [':DATA;'])

    def test_read_data_multiple_packets(self):
        """Test reading multiple packets in one go :ONE;:TWO;"""
        payload = b':ONE;:TWO;'
        self.mock_serial_instance.in_waiting = len(payload)
        self.mock_serial_instance.read.return_value = payload
        
        data = self.canusb.read_data()
        self.assertEqual(data, [':ONE;', ':TWO;'])

    def test_read_data_fragmented(self):
        """Test reading a packet that arrives in two chunks."""
        # Chunk 1: ":HAL"
        self.mock_serial_instance.in_waiting = 4
        self.mock_serial_instance.read.return_value = b':HAL'
        data1 = self.canusb.read_data()
        self.assertEqual(data1, []) # Incomplete, should hold in buffer
        
        # Chunk 2: "F;"
        self.mock_serial_instance.in_waiting = 2
        self.mock_serial_instance.read.return_value = b'F;'
        data2 = self.canusb.read_data()
        self.assertEqual(data2, [':HALF;']) # Now complete

    def test_read_data_ignore_garbage(self):
        """Test that characters outside of : and ; are ignored."""
        payload = b'garbage:VALID;garbage'
        self.mock_serial_instance.in_waiting = len(payload)
        self.mock_serial_instance.read.return_value = payload
        
        data = self.canusb.read_data()
        # Should only capture the :VALID; part
        self.assertEqual(data, [':VALID;'])

if __name__ == '__main__':
    unittest.main()