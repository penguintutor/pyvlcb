import unittest

from pyvlcb import VLCB
from vlcbformat import VLCBformat, VLCBopcode

# Test that the OpCodes are formatted correctly (particular the format field)
class TestOpCodes(unittest.TestCase):
    # Check each of the format entries exist in the field_formats list
    def test_opcode_format(self):
        for thisopcode in VLCBopcode.opcodes.keys():

            if VLCBopcode.opcodes[thisopcode]['format'] == "":
                continue
            field_codes = VLCBopcode.opcodes[thisopcode]['format'].split(',')
            for this_code in field_codes:
                print (f"Checking Opcode {thisopcode} format :{this_code}:")
                self.assertTrue(this_code in VLCBopcode.field_formats.keys())
                
                
if __name__ == '__main__':
    unittest.main()