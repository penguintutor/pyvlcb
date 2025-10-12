# List of layouts - just used to manage the layouts
# Not needed to load default layout as that comes from settings
# If not already exist then create empty one
import json
import os


class Layouts():
    def __init__ (self, data_dir, layouts_file):
        self.data_dir = data_dir
        self.layouts_file = layouts_file
        self.layouts = {}		# Dict key=filename, value=title

        filename = os.path.join(self.data_dir, self.layouts_file)
        try:
            with open(filename, 'r') as data_file:
                self.layouts = json.load(data_file)
        except:
            print (f"No layout list '{filename}' creating new")
            self.layouts = {}
            self.save_file()
            
    def add_layout (self, filename, title):
        self.layouts[filename] = title
        # Save
        self.save_file()
            

    def save_file (self):
        filename = os.path.join(self.data_dir, self.layouts_file)
        try:
            with open(filename, 'w') as data_file:
                json.dump(self.layouts, data_file, indent=4)
        except Exception as e:
            print (f"Error saving layouts file {filename} {e}")
            
            