# Tracks events against devices.
# When we receive / send an event do we need to update devices and corresponding objects
class DeviceEvent:
    def __init__(self):
        self.devices = []