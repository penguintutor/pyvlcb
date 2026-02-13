"""
exceptions.py
Custom exception hierarchy for the library.
"""

class MyLibraryError(Exception):
    """
    Base class for all exceptions in this library.
    
    Catching this exception allows the user to catch ANY error raised 
    specifically by this library, distinct from standard Python errors.
    """
    pass


class DeviceConnectionError(MyLibraryError):
    """
    Raised when a connection to the hardware cannot be established or is lost.
    
    Wraps underlying errors like serial.SerialException.
    """
    pass


class InvalidConfigurationError(MyLibraryError):
    """
    Raised when an invalid configuration or argument is provided.
    
    Used when arguments are the wrong type, out of range (e.g. byte > 255), 
    or logically inconsistent.
    """
    pass


class ProtocolError(MyLibraryError):
    """
    Raised when communication occurs, but the device response is invalid.
    
    Examples:
    - Checksum mismatch
    - Unexpected opcode
    - Malformed header
    """
    pass


class DeviceTimeoutError(MyLibraryError):
    """
    Raised when an operation times out waiting for a response from the device.
    """
    pass

class InvalidLocoError(MyLibraryError):
    """
    Raised for an invalid loco definition
    Includes if the ID is out of range
    or short code specified but code needs long code
    or if the packet does not contain a loco_id (eg. certain Err codes)
    """
    pass

class InvalidFunctionError(MyLibraryError):
    """
    Raised for an invalid function requests
    For example asking for function information
    from a response which doesn't include the function information.
    """
    pass