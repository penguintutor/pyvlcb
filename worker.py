# Simple Worker class used by the ApiHandler class
# Complex automation tasks use AutomationRunner which hands off to the API
from PySide6.QtCore import Qt, QTimer, QThreadPool, QRunnable, Slot

class Worker (QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        #print (f"Function {fn} args {args}")
        
    @Slot() # Pyside6.QtCore.Slot
    def run(self):
        self.fn(*self.args, **self.kwargs)
