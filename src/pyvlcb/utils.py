""" Utils for use by other parts of the library """

from typing import Optional, Union, Tuple, List

# Where 1 x bytes (2 chars)
def num_to_1hexstr (num: int) -> str:
    """Convert number to a byte

    Args:
        num (int): Number to convert

    Returns:
        String: A hex representation of the number (2 chars)
    """
    return f"{hex(num).upper()[2:]:0>2}"

# Where 2 x bytes (4 chars)
def num_to_2hexstr (num: int) -> str:
    """Convert number to 2 bytes

    Args:
        num (int): Number to convert

    Returns:
        String: A hex representation of the number (4 chars)
    """
    return f"{hex(num).upper()[2:]:0>4}"

# Where 4 x bytes (8 chars)
def num_to_4hexstr (num: int) -> str:
    """Convert number to 4 bytes

    Args:
        num (int): Number to convert

    Returns:
        String: A hex representation of the number (8 chars)
    """
    return f"{hex(num).upper()[2:]:0>8}"


# dict to string without {} or ""
def dict_to_string (dictionary: dict) -> str:
    """ Convert a dict to a string without {} or quotes """
    data_string = ""
    for key, value in dictionary.items():
        if data_string != "":
            data_string += " , "
        data_string += f"{key} = {value}"
    return data_string

def f_to_bytes (f_num: int, function_status: List[int]) -> Tuple[str, str]:
    """ Convert a Fnumber (Loco function ID) to bytes as string representation

    Can be used to create correct format for loco_set_dfun
    Limited to range 0 to 28 - which is max for DFUN
    Higher would need to use DFNON/DFOFF

    Args:
        f_num: Function number
        function_status: List with value of all functions (must be updated before calling)
        
    Returns:
        Tuple of two x 2-characer strings representing the bytes
        
    Raises: ValueError

    """
    # Must be an F number between 0 and 28
    if f_num < 0 or f_num > 28:
        raise ValueError (f"Fnumber needs to be between 0 and 28. Number provided {f_num}")
    
    # Extend function_status to 29 entries
    function_list = function_status + [0] * (29 - len(function_status))

    if f_num <= 4:
        byte1 = 1
        byte2 = (0b10000 * function_list[0] +  # fn0 is higher nibble (bit 5)
                 0b0001 * function_list[1] +
                 0b0010 * function_list[2] +
                 0b0100 * function_list[3] +
                 0b1000 * function_list[4]
                 )
    elif f_num <= 8:
        byte1 = 2
        byte2 = (0b0001 * function_list[5] +
                 0b0010 * function_list[6] +
                 0b0100 * function_list[7] +
                 0b1000 * function_list[8]
                 )
    elif f_num <= 12:
        byte1 = 3
        byte2 = (0b0001 * function_list[9] +
                 0b0010 * function_list[10] +
                 0b0100 * function_list[11] +
                 0b1000 * function_list[12]
                 )
    elif f_num <= 20:
        byte1 = 4
        byte2 = (0b0001 * function_list[13] +
                 0b0010 * function_list[14] +
                 0b0100 * function_list[15] +
                 0b1000 * function_list[16] +
                 0b10000 * function_list[17] +
                 0b100000 * function_list[18] +
                 0b1000000 * function_list[19] +
                 0b10000000 * function_list[20]
                 )
    elif f_num <= 28:
        byte1 = 5
        byte2 = (0b0001 * function_list[21] +
                 0b0010 * function_list[22] +
                 0b0100 * function_list[23] +
                 0b1000 * function_list[24] +
                 0b10000 * function_list[25] +
                 0b100000 * function_list[26] +
                 0b1000000 * function_list[27] +
                 0b10000000 * function_list[28]
                 )
    # convert to strings before returning
    # and with 0xFF guarentees it doesn't overflow (although not really neccessary for this method)
    str1 = f"{ (byte1 & 0xFF) :02x}"
    str2 = f"{ (byte2 & 0xFF) :02x}"
    return (str1, str2)


# Where 2 bytes convert to addr id
def bytes_to_addr (byte1: bytes, byte2: bytes) -> int:
    """Convert 2 byte values into an address id string

    Args:
        byte1 (bytes): Most significant byte
        byte2 (bytes): Least significant byte

    Returns:
        Int: The address id value
    """
    msb = int(byte1)
    lsb = int(byte2)
    return ((msb << 8) + lsb)


def bytes_to_locoid (byte1: bytes, byte2: bytes) -> int:
    """ Convert 2 byte values into DCC Loco ID.
    Strips highest two bits
    
    Args:
        byte1 (bytes): Most significant byte
        byte2 (bytes): Least significant byte

    Returns:
        Int: The address id value
    """
    return bytes_to_addr(byte1, byte2) & 0x3FFF
    
    
def byte_to_sessionid (byte1: bytes) -> int:
    """ Converts a single type to a session ID.
    Sames as casting the byte to an int, but here for
    consistant function name. 
    
    Args:
        byte1 (bytes): Data byte

    Returns:
        Int: The session id value
    """
    return int(byte1)
    


def bytes_to_hexstr (byte1: bytes, byte2: bytes) -> str:
    """Convert 2 bytes to a hex string

    Args:
        byte1 (bytes): Most significant byte
        byte2 (bytes): Least significant byte

    Returns:
        String: A hex representation of the number
    """
    return f"{hex(byte1).upper()[2:]:0>2}{hex(byte2).upper()[2:]:0>2}"
    
def dfun_to_functions (fn: int, byte1: int) -> dict[int, int]:
    """ Takes the fn and byte from a dfun command and extracts into a dict of function values. Depending upon the value of fn determines the range of functions included in the response. 
    fn = 1 - F0 to F4
    fn = 2 - F5 to F8
    fn = 3 - F9 to F12
    fn = 4 - F13 to F20
    fn = 5 - F21 to F28
    Functions above F28 are not supported and need to use DFNON / DFNOFF instead.
    Assumes that the fn and byte1 values are already converted into ints
    
    Args: 
        fn: Function range (FR). Which function values are included.
        byte1: byte of set values
    Returns:
        Dict of function values as 0 or 1 for each function as off and on. The Key is an int of the function number 
    """
    func_dict =  {} # dict to store the functions to return
    # Establish first and number of functions included in bytes
    # Could do this by having condition for 4 and 5 having 8 instead of 4
    # but this should be easier to follow
    match fn:
        case 1:
            # special case for 0 - fn0 is in the higher nibble bit 5
            func_dict[0] = 1 if (byte1 & 0b10000) else 0
            # first value (after 0)
            start_func = 1
            num_func = 4
        case 2:
            start_func = 5
            num_func = 4
        case 3:
            start_func = 9
            num_func = 4
        case 4:
            start_func = 13
            # More num_func as uses 2nd nibble
            num_func = 8
        case 5:
            start_func = 21
            num_func = 8
        # default is invalid
        case _:
            raise ValueError (f"Function range is not a valid number between 1 and 5 = {fn}")
    # bit_index will count 0, 1 ...
    # func_num will count start_func, start_func+1 ...
    for bit_index, func_num in enumerate(range(start_func, start_func + num_func)):
        func_dict[func_num] = (byte1 >> bit_index) & 1
    return func_dict
        
            


def bytes_to_functions (fn1: bytes, fn2: bytes, fn3: bytes) -> List[int]:
    """ Sets the value of the functions from a PLOC message
    Only returns values for F0 to F12 (others not included in PLOC)
    Provides as a list for inclusion in menus etc.
    
    Args:
        fn1: Function byte F0 to F4 - bit 5 = dir lighting (F0), bit 6 = direction, bit 7 = res, bit 8 = 0
        fn2: Function byte F5 to F8 - bit 5 upwards reserved
        fn3: Function byte F9 to F12
        
    Returns:
        List of function values as 0 or 1 for each function as off and on
    
    """    
    data_in = [fn1, fn2, fn3]
    mask = [0b0001, 0b0010, 0b0100, 0b1000]
    function_status = [0] * 29
    # Handle 0 separately as it's in the upper nibble
    function_status[0] = data_in[0] & 0b10000
    # Create a list of 12 entries
    for i in range (0, 3):
        for j in range (0, 4):
            function_status[(i*4)+j+1] = 1 if (data_in[i] & mask[j]) > 0 else 0
            
    return function_status
