import unittest

import os

from pyvlcb import VLCB, VLCBFormat, VLCBOpcode

## Test for VLCB library
# Test that the OpCodes are formatted correctly (particular the format field)
class TestOpCodes(unittest.TestCase):
    # Check each of the format entries exist in the field_formats list
    def test_opcode_format(self):
        for thisopcode in VLCBOpcode.opcodes.keys():

            if VLCBOpcode.opcodes[thisopcode]['format'] == "":
                continue
            field_codes = VLCBOpcode.opcodes[thisopcode]['format'].split(',')
            for this_code in field_codes:
                #print (f"Checking Opcode {thisopcode} format :{this_code}:")
                self.assertTrue(this_code in VLCBOpcode.field_formats.keys())

                
if __name__ == '__main__':
    unittest.main()
