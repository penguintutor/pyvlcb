# Device Model or known as a Domain Model
# manages the logical state of devices

from eventbus import EventBus, event_bus


class DeviceModel(QObject):
    # This signal is internal to the model or for ViewModels to subscribe to
    # to react to state changes in the core data.
    model_updated = Signal(str) # Emits device_id when its state changes

    def __init__(self):
        super().__init__()
        self._devices = {
            "device": {"status": "UNKNOWN", "event": None}
        }
        # Subscribe to events from the API layer
        event_bus.device_event_trigger.connect(self._update_device_status)
        event_bus.layout_event_trigger.connect(self._update_layout_status)

    def _update_device_status(self, event: DeviceStatusEvent):
        if event.device_id in self._devices:
            self._devices[event.device_id]["status"] = event.status
            print(f"Model: {event.device_id} status updated to {event.status}")
            self.model_updated.emit(event.device_id) # Notify others of change

    def _update_layout_status(self, event: TemperatureReadingEvent):
        if event.device_id in self._devices:
            self._devices[event.device_id]["layout"] = event.layout_event
            print(f"Model: {event.device_id} updated to {event.layout_event}")
            self.model_updated.emit(event.device_id) # Notify others of change

    def get_device_info(self, device_id: str):
        return self._devices.get(device_id, {})

    def activate_device(self, device_id: str, status: bool):
        # This method is called by the ViewModel, which then publishes a command
        # This isn't strictly necessary as the ViewModel could publish directly,
        # but the Model can act as a central place for business rules/validation.
        print(f"Model: Activating device {device_id} to {status}")
        event_bus.publish(SetDeviceCommand(device_id, status))

# Singleton for the Device Model
device_model = DeviceModel()
