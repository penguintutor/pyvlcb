# List of layouts - just used to manage the layouts
# Not needed to load default layout as that comes from settings
# If not already exist then create empty one
import json
import os


class Layouts():
    def __init__ (self, data_dir, layout_file):
        self.data_dir = data_dir
        self.layout_file = layout_file
        self.layouts = {}		# Dict key=filename, value=title

        filename = os.path.join(self.data_dir, self.layout_file)
        try:
            with open(filename, 'r') as data_file:
                self.layouts = json.load(data_file)
        except:
            print (f"No layout list '{filename}' creating new")
            self.layouts = {}
            self.save_file()
            

    def save_file (self):
        filename = os.path.join(self.data_dir, self.layout_file)
        try:
            with open(filename, 'w') as data_file:
                json.dump(self.layouts, data_file, indent=4)
        except Exception as e:
            print (f"Error saving layouts file {filename} {e}")
            
            