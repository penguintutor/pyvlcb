import unittest
from typing import Optional
from pyvlcb import VLCB
from pyvlcb.vlcbformat import VLCBFormat

class TestVLCB(unittest.TestCase):

    def setUp(self):
        """Initialize the VLCB instance before each test."""
        self.vlcb = VLCB(can_id=60)

    ## Tests for Hex Conversion Utilities
    def test_num_to_hex_conversions(self):
        """Test that numbers are correctly padded and converted to hex strings."""
        # Test 1 byte (2 chars)
        self.assertEqual(VLCB.num_to_1hexstr(10), "0A")
        self.assertEqual(VLCB.num_to_1hexstr(255), "FF")
        
        # Test 2 bytes (4 chars)
        self.assertEqual(VLCB.num_to_2hexstr(10), "000A")
        
        # Test 4 bytes (8 chars)
        self.assertEqual(VLCB.num_to_4hexstr(10), "0000000A")

    ## Tests for Packet Parsing
    def test_parse_input_valid_1(self):
        """Test parsing a valid standard CBUS packet string."""
        # Example packet: :S0B80N400001; 
        # :S (Start), 0B80 (Header), N (Separator), 400001 (Data), ; (End)
        raw_packet = ":S0B80N400001;"
        result = self.vlcb.parse_input(raw_packet)
        
        self.assertIsInstance(result, VLCBFormat)
        self.assertEqual(result.can_id, 92)
        self.assertEqual(result.data, "400001") 

    ## Tests for Packet Parsing
    def test_parse_input_valid_2(self):
        """Test parsing a valid standard CBUS packet string."""
        # Example packet: :SB020NF2012C0000000101; 
        # :S (Start), 0B80 (Header), N (Separator), 400001 (Data), ; (End)
        raw_packet = ":SB020NF2012C0000000101;"
        result = self.vlcb.parse_input(raw_packet)
        
        self.assertIsInstance(result, VLCBFormat)
        self.assertEqual(result.can_id, 1)
        self.assertEqual(result.data, "F2012C0000000101")

    def test_parse_input_invalid_format(self):
        """Test that invalid packets raise the appropriate ValueError."""
        # Test too short
        with self.assertRaises(ValueError):
            self.vlcb.parse_input(":S;")
        
        # Test missing start frame
        with self.assertRaises(ValueError):
            self.vlcb.parse_input("S0B80N400001;")

    ## Tests for Header Generation
    def test_make_header_default(self):
        """Test header generation with default CAN ID and priority."""
        # Expected calculation: (0b10 << 14) + (0b11 << 12) + (60 << 5) = 46976 (0xB780)
        header = self.vlcb.make_header()
        self.assertEqual(header, ":SB780N")

    ## Tests for High-Level Commands
    def test_loco_stop_all(self):
        """Test the emergency stop command generation."""
        # Opcode for RESTP is 0A
        command = self.vlcb.loco_stop_all()
        self.assertTrue(command.endswith("0A;"))
        self.assertIn(":S", command)

    def test_allocate_loco_long_address(self):
        """Test allocating a loco with a long address (adds 0xC000 offset)."""
        loco_id = 3  # Binary 0011
        # Long address logic: 3 | 0xC000 = 0xC003
        command = self.vlcb.allocate_loco(loco_id, long=True)
        self.assertIn("C003", command)

    def test_allocate_loco_short_error(self):
        """Test that invalid short addresses (> 127) raise an error."""
        with self.assertRaises(ValueError):
            self.vlcb.allocate_loco(150, long=False)

if __name__ == "__main__":
    unittest.main()
