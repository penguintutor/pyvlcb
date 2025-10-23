import unittest

import os

from pyvlcb import VLCB
from vlcbformat import VLCBformat, VLCBopcode
from loco import Loco
from guiobject import GuiObject
from devicemodel import device_model
                
## Tests for DeviceModel
# The DeviceModel is created as a singleton known as device_model
class TestDeviceModel(unittest.TestCase):
    def test_create(self):
        #print ("Testing device model")
        self.assertTrue(device_model != False)
        
    def test_load_locos (self):
        #print ("Test load locos")
        basedir = os.path.dirname(__file__)
        test_dir = os.path.join(basedir, "data")
        locos_file = os.path.join(test_dir, "locos.json")
        #print (f"Loading locos file {test_dir} : {locos_file}")
        device_model.load_locos (test_dir, locos_file)
        #print ("Getting all locos")
        all_locos = device_model.get_all_locos()
        #print (f"Locos {all_locos}")
        #print (f"Loco 0 {all_locos[0].loco_name}")
        self.assertTrue(all_locos[0].loco_name == "5190 - Prairie")
        
    def test_add_gui_node (self):
        gui_objects = []
        gui_objects.append(GuiObject(None, "Point", "Test point 1", {}))
        device_model.add_gui_node(gui_objects[-1])
        # Retrieve the gui_node
        this_node = device_model.get_gui_node(0)
        self.assertTrue(this_node.device_type == "Gui")
        self.assertTrue(this_node.object_type == "Point")
        self.assertTrue(this_node.name == "Test point 1")
        # Also test using get_type_node
        this_node_type = device_model.get_type_node ("Test point 1")
        #print (f"Node type is {this_node_type}")
        self.assertTrue(this_node_type == this_node.device_type)
        

                
                
if __name__ == '__main__':
    unittest.main()