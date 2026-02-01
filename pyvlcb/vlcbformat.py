import logging
import warnings
from typing import List, Optional, Union, Dict, Any

# Set up a null handler so nothing prints by default unless the user enables it
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Custom type for returned Dict, containing inner Dict
OpcodeData = Dict[str, Union[str, Dict[str, Any]]]


# Handles a single packet
class VLCBFormat :
    """ Handles a single VLCB packet

    Attributes:
        priority: CAN priority
        can_id: CAN ID
        data: Remaining data as a hex str
    
    """ 
     
    def __init__ (self, priority: int, can_id: int, data: str) -> None:
        """Inits VLCBformat
        
        Args:
            priority: CAN priority
            can_id: CAN ID
            data: Remaining data as a hex string

        """
        self.priority = priority # Priority is actually high and low priority (2bit high / 2bit low) but just treated as single value
        self.can_id = can_id
        self.data = data # Data is left as hex string
        
    # Lookup OpCode
    def opcode (self): # -> Dict[str,str]:
        """Returns the opcode associated with the data string

        Returns:
            Dictionary of the opcode data

        Raises:
            ValueError: If opcode not found
        """
        str_value = self.data[0:2]
        if str_value in VLCBOpcode.opcodes.keys():
            return VLCBOpcode.opcodes[str_value]['opc']
        else:
            raise ValueError(f"Opcode '{str_value}' is not defined.")
    
    def format_data (self) -> OpcodeData:
        """Returns the opcode associated with the data string

        Returns:
            OpcodeData: Dict from the VLCBOpcode

        Raises:
            ValueError: If opcode not found
        """
        return VLCBOpcode.parse_data(self.data)
        
    def __str__ (self):
        return f'{self.priority} : {self.can_id} : {self.opcode()} ({self.data[0:2]}) : {self.data} / {self.format_data()}'

# Opcodes are provided to interpret read signals
# or to allow code to provide user friendly information
# Format provides a string that an be used to help interpret data portion
# Uses class variables & staticmethods 
class VLCBOpcode:
    """List of opcodes and other related data
    
    Includes format information and user friendly strings
    
    Attributes:
        opcodes: Dict of opcodes indexed by opcode number as a hex string
        field_formats: Dict of data type and number of characters for each field
        accessory_codes: Dict of accessory on and off codes

    """
    # Dict from opcode to dict of opcode information
    opcodes = {
        '00':  {'opc': 'ACK', 'title': 'General Acknowledgement', 'format': '', 'minpri': 2, 'comment': 'Positive response to query/request performed for report of availability online'},
        '01':  {'opc': 'NAK', 'title': 'General No Ack', 'format': '', 'minpri': 2, 'comment': 'Negative response to query/request denied'},
        '02':  {'opc': 'HLT', 'title': 'Bus Halt', 'format': '', 'minpri': 0, 'comment': 'Commonly broadcasted to all nodes to indicate CBUS is not available and no further packets should be sent until a BON or ARST is received'},
        '03':  {'opc': 'BON', 'title': 'Bus On', 'format': '', 'minpri': 1, 'comment': 'Commonly broadcasted to all nodes to indicate CBUS is available following a HLT.'},
        '04':  {'opc': 'TOF', 'title': 'Track Off', 'format': '', 'minpri': 1, 'comment': 'Commonly broadcasted to all nodes by a command station to indicate track power is off and no further command packets should be sent, except inquiries..'},
        '05':  {'opc': 'TON', 'title': 'Track On', 'format': '', 'minpri': 1, 'comment': 'Commonly broadcasted to all nodes by a command station to indicate track power is on.'},
        '06':  {'opc': 'ERSTOP', 'title': 'Emergency Stop', 'format': '', 'minpri': 1, 'comment': 'Commonly broadcase to all nodes by a command station to indicate all engines have been emergency stopped.'},
        '07':  {'opc': 'ARST', 'title': 'System Reset', 'format': '', 'minpri': 0, 'comment': 'Commonly broadcasted to all nodes to indicate a full system reset.'},
        '08':  {'opc': 'RTOF', 'title': 'Request Track Off', 'format': '', 'minpri': 1, 'comment': 'Sent to request change of track power to off.'},
        '09':  {'opc': 'RTON', 'title': 'Request Track On', 'format': '', 'minpri': 1, 'comment': 'Sent to request change of track power to on.'},
        '0A':  {'opc': 'RESTP', 'title': 'Request Emergency Stop All', 'format': '', 'minpri': 0, 'comment': 'Sent to request an emergency stop to all trains . Does not affect accessory control.'},
        '0C':  {'opc': 'RSTAT', 'title': 'Request Command Station Status', 'format': '', 'minpri': 2, 'comment': 'Sent to query the status of the command station. See description of (STAT) for the response from the command station.'},
        '0D':  {'opc': 'QNN', 'title': 'Query node number', 'format': '', 'minpri': 3, 'comment': 'Sent by a node to elicit a PNN reply from each node on the bus that has a node number. See OpCode 0xB6'},
        '10':  {'opc': 'RQNP', 'title': 'Request node parameters', 'format': '', 'minpri': 3, 'comment': 'Sent to a node while in ?setup?mode to read its parameter set. Used when initially configuring a node.'},
        '11':  {'opc': 'RQMN', 'title': 'Request module name', 'format': '', 'minpri': 2, 'comment': 'Sent by a node to request the name of the type of module that is in setup mode. The module in setup mode will reply with opcode NAME. See OpCode 0xE2'},
        # Session is the engine session number as HEX byte.
        '21':  {'opc': 'KLOC', 'title': 'Release Engine', 'format': 'Session', 'minpri': 2, 'comment': 'Sent by a CAB to the Command Station. The engine with that Session number is removed from the active engine list.'},
        '22':  {'opc': 'QLOC', 'title': 'Query Engine', 'format': 'Session', 'minpri': 2, 'comment': 'The command station responds with PLOC if the session is assigned. Otherwise responds with ERR: engine not found.'},
        '23':  {'opc': 'DKEEP', 'title': 'Session keep alive', 'format': 'Session', 'minpri': 2, 'comment': 'The cab sends a keep alive at regular intervals for the active session. The interval between keep alive messages must be less than the session timeout implemented by the command station.'},
        '30':  {'opc': 'DBG1', 'title': 'Debug with one data byte', 'format': 'Status', 'minpri': 2, 'comment': '<Dat1> is a freeform status byte for debugging during CBUS module development. Not used during normal operation'},
        '3F':  {'opc': 'EXTC', 'title': 'Extended op-code with no additional bytes', 'format': 'ExtOpc', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        #AddrHigh_AddrLow = Address of the decoder - 7 bit addresses have (AddrH=0). 14 bit addresses have bits 6,7 of AddrH set to 1.
        '40':  {'opc': 'RLOC', 'title': 'Request engine session', 'format': 'AddrHigh_AddrLow', 'minpri': 2, 'comment': 'The command station responds with (PLOC) if engine is free and is being assigned. Otherwise responds with (ERR): engine in use or (ERR:) stack full. This command is typically sent by a cab to the command station following a change of the controlled decoder address. RLOC is exactly equivalent to GLOC with all flag bits set to zero, but command stations must continue to support RLOC for backwards compatibility.'},
        # Consist = Consist address
        # Index = Engine index of the consist
        '41':  {'opc': 'QCON', 'title': 'Query Consist', 'format': 'Consist,Index', 'minpri': 2, 'comment': 'Allows enumeration of a consist. Command station responds with PLOC if an engine exists at the specified index, otherwise responds with ERR: no more engines'},
        # NNHigh = high byte of the node number
        # NNLow = low byte of the node number
        '42':  {'opc': 'SNN', 'title': 'Set Node Number', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to assign a node number to a requesting node in response to a RQNN message. The target node must be in ?setup? mode.'},
        # AllocCode = specific allocation code (1 byte)
        '43':  {'opc': 'ALOC', 'title': 'Allocate loco to activity', 'format': 'Session,AllocCode', 'minpri': 2, 'comment': ''},
        '44':  {'opc': 'STMOD', 'title': 'Set CAB session mode', 'format': 'Session,Mode', 'minpri': 2, 'comment': 'MMMMMMMM = mode bits: 0 ? 1: speed mode; 00 ? 128 speed steps; 01 ? 14 speed steps; 10 ? 28 speed steps with interleave steps; 11 ? 28 speed steps; 2: service mode; 3: sound control mode'},
        # Consist is consist address (8 bits)
        '45':  {'opc': 'PCON', 'title': 'Consist Engine', 'format': 'Session,Consist', 'minpri': 2, 'comment': 'Adds a decoder to a consist. Dat2 has bit 7 set if consist direction is reversed.'},
        '46':  {'opc': 'KCON', 'title': 'Remove Engine from consist', 'format': 'Session,Consist', 'minpri': 2, 'comment': 'Removes a loco from a consist.'},
        # SpeedDir = Speed/dir value. Most significant bit is direction and 7 bits are unsigned speed value. 
        '47':  {'opc': 'DSPD', 'title': 'Set Engine Speed/Dir', 'format': 'Session,SpeedDir', 'minpri': 0, 'comment': 'the unsigned speed value. Sent by a CAB or equivalent to request an engine speed/dir change.'},
        # SpeedFlag - Is speed flags
        '48':  {'opc': 'DFLG', 'title': 'Set Engine Flags', 'format': 'Session,SpeedFlag', 'minpri': 2, 'comment': 'Bits 0-1: Speed Mode 00 ? 128 speed steps; 01 ? 14 speed steps; 10 ? 28 speed steps with interleave steps; 11 ? 28 speed steps Bit 2: Lights On/OFF; Bit 3: Engine relative direction; Bits 4-5: Engine state (active =0 , consisted =1, consist master=2, inactive=3) Bits 6-7: Reserved.; Sent by a cab to notify the command station of a change in engine flags.'},
        # Fnum = Function number, 0 to 27
        '49':  {'opc': 'DFNON', 'title': 'Set Engine function on', 'format': 'Session,Fnum', 'minpri': 2, 'comment': 'Sent by a cab to turn on a specific loco function. This provides an alternative method to DFUN for controlling loco functions. A command station must implement both methods.'},
        '4C':  {'opc': 'SSTAT', 'title': 'Service mode status', 'format': 'Session,Status', 'minpri': 3, 'comment': 'Status returned by command station/programmer at end of programming operation that does not return data.'},
        '50':  {'opc': 'RQNN', 'title': 'Request node number', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a node that is in setup/configuration mode and requests assignment of a node number (NN). The node allocating node numbers responds with (SNN) which contains the newly assigned node number. <NN hi> and <NN lo> are the existing node number, if the node has one. If it does not yet have a node number, these bytes should be set to zero.'},
        '51':  {'opc': 'NNREL', 'title': 'Node number release', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by node when taken out of service. e.g. when reverting to SLiM mode.'},
        '52':  {'opc': 'NNACK', 'title': 'Node number acknowledge', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a node to verify its presence and confirm its node id. This message is sent to acknowledge an SNN.'},
        '53':  {'opc': 'NNLRN', 'title': 'Set node into learn mode', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to put a specific node into learn mode.'},
        '54':  {'opc': 'NNULN', 'title': 'Release node from learn mode', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to take node out of learn mode and revert to normal operation.'},
        '55':  {'opc': 'NNCLR', 'title': 'Clear all events from a node', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to clear all events from a specific node. Must be in learn mode first to safeguard against accidental erasure of all events.'},
        '56':  {'opc': 'NNEVN', 'title': 'Read number of events available in a node', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to read the number of available event slots in a node.Response is EVLNF (0x70)'},
        '57':  {'opc': 'NERD', 'title': 'Read back all stored events in a node', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to read all the stored events in a node. Response is 0xF2.'},
        '58':  {'opc': 'RQEVN', 'title': 'Request to read number of stored events', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a configuration tool to read the number of stored events in a node. Response is 0x74( NUMEV).'},
        '59':  {'opc': 'WRACK', 'title': 'Write acknowledge', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by a node to indicate the completion of a write to memory operation. All nodes must issue WRACK when a write operation to node variables, events or event variables has completed. This allows for teaching nodes where the processing time may be slow.'},
        '5A':  {'opc': 'RQDAT', 'title': 'Request node data event', 'format': 'NN', 'minpri': 3, 'comment': 'Sent by one node to read the data event from another node.(eg: RFID data). Response is 0xF7 (ARDAT).'},
        # DN = Device number
        '5B':  {'opc': 'RQDDS', 'title': 'Request device data - short mode', 'format': 'DNHigh_DNLow', 'minpri': 3, 'comment': 'To request a data set from a device using the short event method. where DN is the device number. Response is 0xFB (DDRS)'},
        '5C':  {'opc': 'BOOTM', 'title': 'Put node into bootload mode', 'format': 'NN', 'minpri': 3, 'comment': 'For SliM nodes with no NN then the NN of the command must be zero. For SLiM nodes with an NN, and all FLiM nodes the command must contain the NN of the target node. Sent by a configuration tool to prepare for loading a new program.'},
        '5D':  {'opc': 'ENUM', 'title': 'Force a self enumeration cyble for use with CAN', 'format': 'NN', 'minpri': 3, 'comment': 'For nodes in FLiM using CAN as transport. This OPC will force a self-enumeration cycle for the specified node. A new CAN_ID will be allocated if needed. Following the ENUM sequence, the node should issue a NNACK to confirm completion and verify the new CAN_ID. If no CAN_ID values are available, an error message 7 will be issued instead.'},
        '5F':  {'opc': 'EXTC1', 'title': 'Extended op-code with 1 additional byte', 'format': 'ExtOpc,Byte1', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        # 3rd data section
        '60':  {'opc': 'DFUN', 'title': 'Set Engine functions', 'format': 'Session,Fn1,Fn2', 'minpri': 2, 'comment': '<Dat2> (Fn1) is the function range. 1 is F0(FL) to F4; 2 is F5 to F8; 3 is F9 to F12; 4 is F13 to F20; 5 is F21 to F28; <Dat3> (Fn2) is the NMRA DCC format function byte for that range in corresponding bits. Sent by a CAB or equivalent to request an engine Fn state change.'},
        '61':  {'opc': 'GLOC', 'title': 'Get engine session', 'format': 'AddrHigh_AddrLow,Flags', 'minpri': 2, 'comment': '<Dat1> and <Dat2> are [AddrH] and [AddrL] of the decoder, respectively.; 7 bit addresses have (AddrH=0).; 14 bit addresses have bits 6,7 of AddrH set to 1.; <Flags> contains flag bits as follows:Bit 0: Set for "Steal" mode; Bit 1: Set for "Share" mode; Both bits set to 0 is exactly equivalent to an RLOC request; Both bits set to 1 is invalid, because the 2 modes are mutually exclusive; The command station responds with (PLOC) if the request is successful. Otherwise responds with (ERR): engine in use. (ERR:) stack full or (ERR) no session. The latter indicates that there is no current session to steal/share depending on the flag bits set in the request. GLOC with all flag bits set to zero is exactly equivalent to RLOC, but command stations must continue to support RLOC for backwards compatibility.'},
        '63':  {'opc': 'ERR', 'title': 'Command station error report', 'format': 'Byte1,Byte2,ErrCode', 'minpri': 2, 'comment': 'Sent in response to an error situation by a command station.'},
        '6F':  {'opc': 'CMDERR', 'title': 'Error messages from nodes during configuration', 'format': 'NN,Error', 'minpri': 3, 'comment': 'Sent by node if there is an error when a configuration command is sent.'},
        '70':  {'opc': 'EVNLF', 'title': 'Event space left reply from node', 'format': 'NN,EVSPC', 'minpri': 3, 'comment': 'EVSPC is a one byte value giving the number of available events left in that node.'},
        '71':  {'opc': 'NVRD', 'title': 'Request read of a node variable', 'format': 'NN,NVIndex', 'minpri': 3, 'comment': 'NV# is the index for the node variable value requested. Response is NVANS.'},
        '72':  {'opc': 'NENRD', 'title': 'Request read of stored events by event index', 'format': 'NN,EnIndex', 'minpri': 3, 'comment': 'EN# is the index for the stored event requested. Response is 0xF2 (ENRSP)'},
        '73':  {'opc': 'RQNPN', 'title': 'Request read of a node parameter by index', 'format': 'NN,ParaIndex', 'minpri': 3, 'comment': 'Para# is the index for the parameter requested. Index 0 returns the number of available parameters, Response is 0x9B (PARAN).'},
        '74':  {'opc': 'NUMEV', 'title': 'Number of events stored in node', 'format': 'NN,NumEvents', 'minpri': 3, 'comment': 'Response to request 0x58 (RQEVN)'},
        '75':  {'opc': 'CANID', 'title': 'Set a CAN_ID in existing FLiM node', 'format': 'NN,CAN_ID', 'minpri': 0, 'comment': 'Used to force a specified CAN_ID into a node. Value range is from 1 to 0x63 (99 decimal) This OPC must be used with care as duplicate CAN_IDs are not allowed. Values outside the permitted range will produce an error 7 message and the CAN_ID will not change.'},
        '7F':  {'opc': 'EXTC2', 'title': 'Extended op-code with 2 additional bytes', 'format': 'ExtOpc,Byte1,Byte2', 'minpri': 0, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        # 4 data byte packets
        '80':  {'opc': 'RDCC3', 'title': 'Request 3-byte DCC Packet', 'format': 'Rep,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': '<Dat1(REP)> is number of repetitions in sending the packet. <Dat2>..<Dat4> 3 bytes of the DCC packet. Allows a CAB or equivalent to request a 3 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis. Note: a 3 byte DCC packet is the minimum allowed.'},
        '82':  {'opc': 'WCVO', 'title': 'Write CV (byte) in OPS mode', 'format': 'Session,CVHigh_CVLow,CVVal', 'minpri': 2, 'comment': '<Dat1> is the session number of the loco to be written to; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the byte value to be written; Sent to the command station to write a DCC CV byte in OPS mode to specific loco.(on the main)'},
        '83':  {'opc': 'WCVB', 'title': 'Write CV (bit) in OPS mode', 'format': 'Session,CVHigh_CVLow,CVVal', 'minpri': 2, 'comment': '<Dat1> is the session number of the loco to be written to; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the value to be written; The format for Dat4 is that specified in RP 9.2.1 for OTM bit manipulation in a DCC packet.; This is ?111CDBBB? where C is here is always 1 as only ?writes? are possible OTM. (unless some loco ACK scheme like RailCom is used). D is the bit value, either 0 or 1 and BBB is the bit position in the CV byte. 000 to 111 for bits 0 to 7.; Sent to the command station to write a DCC CV in OPS mode to specific loco.(on the main)'},
        '84':  {'opc': 'QCVS', 'title': 'Read CV', 'format': 'Session,CVHigh_CVLow,Mode', 'minpri': 2, 'comment': 'This command is used exclusively with service mode.; Sent by the cab to the command station in order to read a CV value. The command station shall respond with a PCVS message containing the value read, or SSTAT if the CV cannot be read.'},
        '85':  {'opc': 'PCVS', 'title': 'Report CV', 'format': 'Session,CVHigh_CVLow,CVVal', 'minpri': 2, 'comment': '<Dat1> is the session number of the cab; <Dat2> is the MSB # of the CV read (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV read; <Dat4> is the read value; This command is used exclusively with service mode.; Sent by the command station to report a read CV.'},
        '90':  {'opc': 'ACON', 'title': 'Accessory ON', 'format': 'NN,EnHigh_EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ?ON? event using the full event number of 4 bytes. (long event)'},
        '91':  {'opc': 'ACOF', 'title': 'Accessory OFF', 'format': 'NN,EnHigh_EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ?OFF? event using the full event number of 4 bytes. (long event)'},
        '92':  {'opc': 'AREQ', 'title': 'Accessory Request Event', 'format': 'NN,EnHigh_EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number (MS WORD of the full event #); <Dat2> is the low byte of the node number (MS WORD of the full event #); <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates a ?request? event using the full event number of 4 bytes. (long event); A request event is used to elicit a status response from a producer when it is required to know the state of the producer without producing an ON or OFF event and to trigger an event from a combi node'},
        '93':  {'opc': 'ARON', 'title': 'Accessory Response Event', 'format': 'NN,EnHigh_EnLow', 'minpri': 3, 'comment': 'Indicates an ?ON? response event. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        '94':  {'opc': 'AROF', 'title': 'Accessory Response Event', 'format': 'NN,EnHigh_EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ‘OFF’ response event. A response event is a reply to a status request; (AREQ) without producing an ON or OFF event'},
        '95':  {'opc': 'EVULN', 'title': 'Unlearn an event in learn mode', 'format': 'NN,EnHigh_EnLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to remove an event from a node.'},
        # NVIndex is NV Index number
        '96':  {'opc': 'NVSET', 'title': 'Set a node variable', 'format': 'NN,NVIndex,NVVal', 'minpri': 3, 'comment': 'Sent by a configuration tool to set a node variable. NV# is the NV index number.'},
        '97':  {'opc': 'NVANS', 'title': 'Response to a request for a node variable value', 'format': 'NN,NVIndex,NVVal', 'minpri': 3, 'comment': 'Sent by node in response to request. (NVRD)'},
        # Short events
        # DNHigh, DNLow = Lower two bytes define device number - considered same as a device address - full 4byte event is still sent
        # <Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the Device Number; <Dat4> is the low byte of the Device Number
        '98':  {'opc': 'ASON', 'title': 'Accessory short ON', 'format': 'NN,DNHigh_DNLow', 'minpri': 3, 'comment': 'Indicates an ‘ON’ event using the short event number of 2 LS bytes.'},
        '99':  {'opc': 'ASOF', 'title': 'Accessory short OFF', 'format': 'NN,DNHigh_DNLow', 'minpri': 3, 'comment': 'Indicates an ‘OFF’ event using the short event number of 2 LS bytes.'},
        '9A':  {'opc': 'ASRQ', 'title': 'Accessory Short Request Event', 'format': 'NN,DNHigh_DNLow', 'minpri': 3, 'comment': 'Indicates a ‘request’ event using the short event number of 2 LS bytes. A request event is used to elicit a response from a producer ‘device’ when it is required to know the ‘state’ of the device without producing an ON or OFF event and to trigger an event from a combi node.'},
        # ParaIndex = Index of parameter
        # ParaVal = Parameter value
        '9B':  {'opc': 'PARAN', 'title': 'Response to request for individual node parameter', 'format': 'NN,ParaIndex,ParaVal', 'minpri': 3, 'comment': 'NN is the node number of the sending node. Para# is the index of the parameter and Para val is the parameter value.'},
        # EnIndex is event index
        # EvIndex is Event variable index
        '9C':  {'opc': 'REVAL', 'title': 'Request for read of an event variable', 'format': 'NN,EnIndex,EvIndex', 'minpri': 3, 'comment': 'This request differs from B2 (REQEV) as it doesn’t need to be in learn mode but does; require the knowledge of the event index to which the EV request is directed.; EN# is the event index. EV# is the event variable index. Response is B5 (NEVAL)'},
        '9D':  {'opc': 'ARSON', 'title': 'Accessory short response event', 'format': 'NN,DNHigh_DNLow', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event.'},
        '9E':  {'opc': 'ARSOF', 'title': 'Accessory short response event', 'format': 'NN,DNHigh_DNLow', 'minpri': 3, 'comment': 'ndicates an ‘OFF’ response event. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event.'},
        '9F':  {'opc': 'EXTC3', 'title': 'Extended op-code with 3 additional bytes', 'format': 'ExtOpc,Byte1,Byte2,Byte3', 'minpri': 0, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        # 5 data byte packets
        # Rep = repeat
        'A0':  {'opc': 'RDCC4', 'title': 'Request 4-byte DCC packet', 'format': 'Rep,Byte1,Byte2,Byte3,Byte4', 'minpri': 2, 'comment': '<Dat1(REP)> is number of repetitions in sending the packet.; <Dat2>..<Dat5> 4 bytes of the DCC packet.; Allows a CAB or equivalent to request a 4 byte DCC packet to be sent to the track. The; packet is sent <REP> times and is not refreshed on a regular basis.'},
        # CVHigh MSB of CV (1-65536)
        # CVLow LSB of CV
        # Mode - service write mode
        #CVVal - CV value
        'A2':  {'opc': 'WCVS', 'title': 'Write CV in Service Mode', 'format': 'Session,CVHigh_CVLow,Mode,CVVal', 'minpri': 0, 'comment': '<Dat1> is the session number of the cab; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the service write mode; <Dat5> is the CV value to be written; Sent to the command station to write a DCC CV in service mode.'},
        'B0':  {'opc': 'ACON1', 'title': 'Accessory ON', 'format': 'NN,EnHigh_EnLow,Byte1', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; <Dat5> is an additional data byte; Indicates an ‘ON’ event using the full event number of; 4 bytes with one additional data byte.'},
        'B1':  {'opc': 'ACOF1', 'title': 'Accessory OFF', 'format': 'NN,EnHigh_EnLow,Byte1', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; <Dat5> is an additional data byte; Indicates an ‘OFF’ event using the full event number of 4 bytes with one additional data byte.'},
        'B2':  {'opc': 'REQEV', 'title': 'Read event variable in learn mode', 'format': 'NN,EnHigh_EnLow,EvIndex', 'minpri': 3, 'comment': 'Allows a configuration tool to read stored event variables from a node. EV# is the EV index. Reply is (EVANS)'},
        'B3':  {'opc': 'ARON1', 'title': 'Accessory Response Event', 'format': 'NN,EnHigh_EnLow,Byte1', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event with one additional data byte. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        'B4':  {'opc': 'AROF1', 'title': 'Accessory Response Event', 'format': 'NN,EnHigh_EnLow,Byte1', 'minpri': 3, 'comment': 'Indicates an ‘OFF’ response event with one additional data byte. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        # NNHigh, NNLow node replying
        # EvVal is value of Event Variable
        'B5':  {'opc': 'NEVAL', 'title': 'Response to request for read of EV value', 'format': 'NN,EnIndex,EvIndex,EvVal', 'minpri': 3, 'comment': 'NN is the node replying. EN# is the index of the event in that node. EV# is the index of the event variable. EVval is the value of that EV. This is response to 9C (REVAL)'},
        'B6':  {'opc': 'PNN', 'title': 'Response to Query Node', 'format': 'NN,ManufId,ModId,Flags', 'minpri': 3, 'comment': '<NN Hi> is the high byte of the node number; <NN Lo> is the low byte of the node number; <Manuf Id> is the Manufacturer id as defined in the node parameters; <Module Id> is the Module Type Id id as defined in the node parameters; <Flags> is the node flags as defined in the node parameters. The Flags byte contains bit flags as follows:; Bit 0: Set to 1 for consumer node; Bit 1: Set to 1 for producer node; Bit 2: Set to 1 for FLiM mode; Bit 3: Set to 1 for Bootloader compatible; If a module is both a producer and a consumer then it is referred to as a combi node and; both flags will be set.; Every node should send this message in response to a QNN message.'},
        'B8':  {'opc': 'ASON1', 'title': 'Accessory Short ON', 'format': 'NN,DNHigh_DNLow,Byte1', 'minpri': 3, 'comment': 'Indicates an ‘ON’ event using the short event number of 2 LS bytes with one added data byte.'},
        'B9':  {'opc': 'ASOF1', 'title': 'Accessory Short OFF', 'format': 'NN,DNHigh_DNLow,Byte1', 'minpri': 3, 'comment': 'Indicates an ‘OFF’ event using the short event number of 2 LS bytes with one added data byte.'},
        'BD':  {'opc': 'ARSON1', 'title': 'Accessory Short Response Event with one data byte', 'format': 'NN,DNHigh_DNLow,Byte1', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event with one added data byte. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event.'},
        'BE':  {'opc': 'ARSOF1', 'title': 'Accessory short response event with one data byte', 'format': 'NN,DNHigh_DNLow,Byte1', 'minpri': 3, 'comment': 'Indicates an ‘OFF’ response event with one added data byte. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event.'},
        'BF':  {'opc': 'EXTC4', 'title': 'Extended op-code with 4 data bytes', 'format': 'ExtOpc,Byte1,Byte2,Byte3,Byte4', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        # 6 data byte packets
        'C0':  {'opc': 'RDCC5', 'title': 'Requst 5-byte DCC packet', 'format': 'Rep,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 2, 'comment': '<Dat1(REP)> is # of repetitions in sending the packet.; <Dat2>..<Dat6> 5 bytes of the DCC packet.; Allows a CAB or equivalent to request a 5 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis.'},
        'C1':  {'opc': 'WCVOA', 'title': 'Write CV (byte) in OPS mode by address', 'format': 'AddrHigh_AddrLow,CVHigh_CVLow,Mode,CVVal', 'minpri': 2, 'comment': '<Dat1> and <Dat2> are [AddrH] and [AddrL] of the decoder, respectively.; 7 bit addresses have (AddrH=0).; 14 bit addresses have bits 7,8 of AddrH set to 1.; <Dat3> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat4> is the LSB # of the CV to be written; <Dat5> is the programming mode to be used; <Dat6> is the CV byte value to be written; Sent to the command station to write a DCC CV byte in OPS mode to specific loco (on the main). Used by computer based ops mode programmer that does not have a valid throttle handle.'},
        'CF':  {'opc': 'FCLK', 'title': 'Fast Clock', 'format': 'DateTime', 'minpri': 3, 'comment': 'This addendum defines a time encoding'},
        'D0':  {'opc': 'ACON2', 'title': 'Accessory ON', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2', 'minpri': 3, 'comment': 'Indicates an ‘ON’ event using the full event number of 4 bytes with two additional data bytes.'},
        'D1':  {'opc': 'ACOF2', 'title': 'Accessory OFF', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2', 'minpri': 3, 'comment': 'ndicates an ‘OFF’ event using the full event number of 4 bytes with two additional data bytes.'},
        'D2':  {'opc': 'EVLRN', 'title': 'Teach an event in learn mode', 'format': 'NN,EnHigh_EnLow,EvIndex,EvVal', 'minpri': 3, 'comment': 'A node response to a request from a configuration tool for the EVs associated with an event (REQEV). For multiple EVs, there will be one response per request.'},
        'D3':  {'opc': 'EVANS', 'title': 'Response to a request for an EV value in a node in learn mode', 'format': 'NN,EnHigh_EnLow,EvIndex,EvVal', 'minpri': 3, 'comment': 'A node response to a request from a configuration tool for the EVs associated with an event (REQEV). For multiple EVs, there will be one response per request.'},
        'D4':  {'opc': 'ARON2', 'title': 'Accessory Response Event', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event with two added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        'D5':  {'opc': 'AROF2', 'title': 'Accessory Response Event', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2', 'minpri': 3, 'comment': 'Indicates an ‘OFF’ response event with two added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        'D8':  {'opc': 'ASON2', 'title': 'Accessory Short ON', 'format': 'NN,DNHigh_DNLow,Byte1,Byte2', 'minpri': 3, 'comment': 'Indicates an ‘ON’ event using the short event number of 2 LS bytes with two added data bytes.'},
        'DD':  {'opc': 'ARSON2', 'title': 'Accessory Short Response Event with two bytes', 'format': 'NN,DNHigh_DNLow,Byte1,Byte2', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event with two added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event.'},
        'DE':  {'opc': 'ARSOF2', 'title': 'Accessory Short Response Event with two bytes','format': 'NN,DNHigh_DNLow,Byte1,Byte2', 'minpri': 3, 'comment': 'Indicates an ‘OFF’ response event with two added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event.'},
        'DF':  {'opc': 'EXTC5', 'title': 'Extended op-code with 5 data bytes', 'format': 'ExtOpc,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
         # 7 data byte packets
        'E0':  {'opc': 'RDCC6', 'title': 'Request 6 byte DCC packet', 'format': 'Rep,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 2, 'comment': 'Allows a CAB or equivalent to request a 6 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis.'},
        'E1':  {'opc': 'PLOC', 'title': 'Engine Report', 'format': 'Session,AddrHigh_AddrLow,SpeedDir,Fn1,Fn2,Fn3', 'minpri': 2, 'comment': '<Dat4> is the Speed/Direction value. Bit 7 is the direction bit and bits 0-6 are the speed value.; <Dat5> is the function byte F0 to F4; <Dat6> is the function byte F5 to F8; <Dat7> is the function byte F9 to F12; A report of an engine entry sent by the command station. Sent in response to QLOC or as an acknowledgement of acquiring an engine requested by a cab (RLOC or GLOC).'},
        'E2':  {'opc': 'NAME', 'title': 'Response to request for node name string', 'format': 'Char1_7', 'minpri': 3, 'comment': 'A node response while in ‘setup’ mode for its name string. Reply to (RQMN). The string for the module type is returned in char1 to char7, space filled to 7 bytes. The Module Name prefix , currently either CAN or ETH, depends on the Interface Protocol parameter, it is not included in the response, see section 12.2 for the definition of the parameters.'},
        'E3':  {'opc': 'STAT', 'title': 'Command station status report', 'format': 'NN,CSNum,Flags,MajRev,MinRev,Build', 'minpri': 2, 'comment': '<NN hi> <NN lo> Gives node id of command station, so further info can be got from parameters or interrogating NVs; <CS num> For future expansion - set to zero at present; <flags> Flags as defined below; <Major rev> Major revision number; <Minor rev> Minor revision letter; <Build no.> Build number, always 0 for a released version.; <flags> is status defined by the bits below.; bits:; 0 - Hardware Error (self test); 1 - Track Error; 2 - Track On/ Off; 3 - Bus On/ Halted; 4 - EM. Stop all performed; 5 - Reset done; 6 - Service mode (programming) On/ Off; 7 – reserved; Sent by the command station in response to RSTAT.'},
        'EF':  {'opc': 'PARAMS', 'title': 'Response to request for node parameters', 'format': 'Para1_7', 'minpri': 3, 'comment': 'A node response while in ‘setup’ mode for its parameter string. Reply to (RQNP)'},
        'F0':  {'opc': 'ACON3', 'title': 'Accessory ON', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': 'Indicates an ON event using the full event number of 4 bytes with three additional data bytes.'},
        'F1':  {'opc': 'ACOF3', 'title': 'Accessory OFF', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': 'Indicates an OFF event using the full event number of 4 bytes with three additional data bytes.'},
        'F2':  {'opc': 'ENRSP', 'title': 'Response to request to read node events', 'format': 'NN,En3_0,EnIndex', 'minpri': 3, 'comment': 'Where the NN is that of the sending node. EN3 to EN0 are the four bytes of the stored event. EN# is the index of the event within the sending node. This is a response to either 57 (NERD) or 72 (NENRD)'},
        'F3':  {'opc': 'ARON3', 'title': 'Acessory Response Event', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event with three added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        'F4':  {'opc': 'AROF3', 'title': 'Acessory Response Event', 'format': 'NN,EnHigh_EnLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': 'Indicates an ‘ON’ response event with three added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        'F5':  {'opc': 'EVLRNI', 'title': 'Teach and event in learn mode using event indexing', 'format': 'NN,EnHigh_EnLow,EnIndex,EvIndex,EvVal', 'minpri': 3, 'comment': 'Sent by a configuration tool to a node in learn mode to teach it an event. The event index must be known. Also teaches it the associated event variables.(EVs). This command is repeated for each EV required.'},
        'F6':  {'opc': 'ACDAT', 'title': 'Accessory node data event', 'format': 'NN,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 3, 'comment': 'Indicates an event from this node with 5 bytes of data. For example, this can be used to send the 40 bits of an RFID tag. There is no event number in order to allow space for 5 bytes of data in the packet, so there can only be one data event per node.'},
        'F7':  {'opc': 'ARDAT', 'title': 'Accessory node data response', 'format': 'NN,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 3, 'comment': 'Indicates a node data response. A response event is a reply to a status request (RQDAT) without producing a new data event.'},
        'F8':  {'opc': 'ASON3', 'title': 'Accessory Short ON', 'format': 'NN,DNHigh_DNLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': 'Indicates an ON event using the short event number of 2 LS bytes with three added data bytes.'},
        'F9':  {'opc': 'ASOF3', 'title': 'Accessory Short OFF', 'format': 'NN,DNHigh_DNLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': 'Indicates an OFF event using the short event number of 2 LS bytes with three added data bytes.'},
        'FA':  {'opc': 'DDES', 'title': 'Device data event (short mode)', 'format': 'DNHigh_DNLow,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 3, 'comment': 'Function is the same as F6 but uses device addressing so can relate data to a device attached to a node. e.g. one of several RFID readers attached to a single node.'},
        'FB':  {'opc': 'DDRS', 'title': 'Device data response (short mode)', 'format': 'DNHigh_DNLow,Byte1,Byte2,Byte3,Byte4,Byte5', 'minpri': 3, 'comment': "The response to a request for data from a device. (0x5B)"},
        'FD':  {'opc': 'ARSON3', 'title': 'Accessory Short Response Event', 'format': 'NN,DNHigh_DNLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': "Indicates an ON response event with with three added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event."},
        'FE':  {'opc': 'ARSOF3', 'title': 'Accessory Short Response Event', 'format': 'NN,DNHigh_DNLow,Byte1,Byte2,Byte3', 'minpri': 3, 'comment': "Indicates an OFF response event with with three added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event."},
        'FF':  {'opc': 'EXTC6', 'title': 'Extended op-code with 6 data bytes', 'format': 'ExtOpc,Byte1,Byte2,Byte3,Byte4,Byte5,Byte6', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'}
        }
    
    # Number of chars (2 per byte) in each field and how to show to use (eg. hex / num / char)
    # Num vs Hex is just suggested formatting - stored as a number the same
    # In char then it's ascii - otherwise normally convert to a number and return that
    field_formats = {
            "Unknown": [2, "hex"],        # Generic if not known how to format
            "CAN_ID": [2, "num"],         # Canbus id
            "Session": [2, "hex"],        # Engine session number
            "AddrHigh_AddrLow": [4, "num"], # Address of dcoder (7 or 14 bit) - 14bit have bits 6,7 of AddrHigh set to 1
            "Consist": [2, "num"],        # Consist ID
            "Index": [2, "num"],          # Index of loco in consist
            "Status": [2, "hex"],     
            "NN": [4, "num"],    # Node number
            "AllocCode": [2, "num"],       # Specific allocation code
            "SpeedDir": [2, "hex"],
            "SpeedFlag": [2, "hex"],       # Speed flags DDD-DDDDD
            "Fnum": [2, "num"],            # Function number
            "Fn1": [2,"num"],              # Function number (multi byte)
            "Fn2": [2,"num"],              # Function number (multi byte)
            "Fn3": [2,"num"],              # Function number (multi byte)
            "DNHigh_DNLow": [4, "num"],    # Device number (aka Device address)
            "ExtOpc": [2, "char"],         # Extended op code
            "Byte1": [2, "hex"],           # Byte (eg extended)
            "Byte2": [2, "hex"],           # Byte (eg extended)
            "Byte3": [2, "hex"],           # Byte (eg extended)
            "Byte4": [2, "hex"],           # Byte (eg extended)
            "Byte5": [2, "hex"],           # Byte (eg extended)
            "Byte6": [2, "hex"],           # Byte (eg extended)
            "CVHigh_CVLow": [2, "num"],    # CV number (DCC Configuration variables)
            "CVVal": [2, "num"],           # CV value 
            "NVIndex": [2, "num"],         # NV Node variable index
            "NVVal": [2, "hex"],           # NV value
            "NumEvents": [2, "num"],       # Number of events
            "ParaIndex": [2, "num"],       # Index of node parameter
            "ParaVal": [2, "num"],         # Value of node parameter
            "Para1_7": [14, "hex"],        # Multiple parameters
            "EnHigh_EnLow": [4, "num"],    # En
            "EnIndex": [2, "num"],         # Index of Event
            "EvIndex": [2, "num"],         # Index of Event variable
            "EvVal": [2, "num"],           # Event variable value
            "Rep": [2, "num"],             # Repeat, num of times to send signal
            "Mode": [2, "hex"],            # Service write mode
            "ManufId": [2, "hex"],         # Manufacturer
            "ModId": [2, "hex"],           # Module
            "Flags": [2, "hex"],           # Module flags
            "CSNum": [2, "hex"],           # Zero (future expansion)
            "MajRev": [2, "num"],          # Major revision number
            "MinRev": [2, "ascii"],        # Minor revision letter
            "Build": [2, "num"],           # Built number always 0 for a released version
            "DateTime": [8, "hex"],        # Date and time encoded
            "Char1_7": [14, "ascii"],      # Name string 7 bytes long - padded
            "En3_0": [8, "hex"],           # 4 bytes of stored event
            "EVSPC": [2, "num"],           # Amount of space available for events
            "ErrCode": [2, "hex"],         # Short 1 byte error code
            "Error": [4, "hex"]            # Error code
        }
    
    # Accessory Codes - provided for convenient lookup
    accessory_codes = {
        'on': [
            'ACON',
            'ASON',
            'ACON1',
            'ACON2',
            'ACON3',
            'ASON1',
            'ASON2',
            'ASON3'
            ],
        'off': [
            'ACOF',
            'ASOF',
            'ACOF1',
            'ACOF2',
            'ACOF3',
            'ASOF1',
            'ASOF2',
            'ASOF3'
            ]
        }
    
    # Shorten op-code (remove extra characters)
    # Used to allow methods to be used if mnemonic is included in op-code
    # Or you could pass the entire data section
    @staticmethod
    def opcode_extract (opcode_string: str) -> str:
        """Shortens op code by removing extra characters

        Returns:
            String: shortened opcode string

        Raises:
            ValueError: If string does not contain at least 2 characters
        """
        if len(opcode_string) >= 2:
            return opcode_string[0:2]
        else:
            raise ValueError(f"String '{opcode_string}' is too short.")
    
    # Get min priority from opcode
    @staticmethod
    def opcode_priority (opcode: str) -> int:
        """Get priority from opcode

        Returns:
            int: priority value

        Raises:
            ValueError: If opcode not found
        """
        opcode = VLCBOpcode.opcode_extract(opcode)
        if opcode in VLCBOpcode.opcodes.keys():
            return VLCBOpcode.opcodes[opcode]['minpri']
        else:
            raise ValueError(f"Opcode '{opcode}' is not defined.")
    
    # Title of opcode (used in tooltip)
    @staticmethod
    def opcode_title (opcode: str) -> str:
        """Get title from opcode

        Returns:
            String: Opcode Title

        Raises:
            ValueError: If opcode not found
        """
        opcode = VLCBOpcode.opcode_extract(opcode)
        if opcode in VLCBOpcode.opcodes.keys():
            return VLCBOpcode.opcodes[opcode]['title']
        else:
            raise ValueError(f"Opcode '{opcode}' is not defined.")
    
    # Convert op-code to mnemonic
    @staticmethod
    def opcode_mnemonic (opcode):
        """Get mnemonic from opcode

        Returns:
            String: Opcode mnemonic

        Raises:
            ValueError: If opcode not found
        """
        opcode = VLCBOpcode.opcode_extract(opcode)
        if opcode in VLCBOpcode.opcodes.keys():
            return VLCBOpcode.opcodes[opcode]['opc']
        else:
            raise ValueError(f"Opcode '{opcode}' is not defined.")
    
    # Parse the data based on the format str and store in a dictionary
    @staticmethod
    def parse_data (data: str) -> OpcodeData:
        """Returns the data associated with the data string as a dict

        Returns:
            OpcodeData: Dict in OpcodeData format

        Raises:
            ValueError: If opcode not found
        """
        # Does not raise any explicit exceptions but uses methods that could raise a ValueError
        opcode = VLCBOpcode.opcode_extract(data)
        # strip opcode from data
        data = data[2:]

        #print (f"Data {data}")
        # Include opcode in data if required for future use
        data_parsed = {'opid': opcode}
        # check valid opcode (if not then empty format)
        if not opcode in VLCBOpcode.opcodes.keys():
            format = ""
            data_parsed['opcode'] = "UNKNOWN"
        else:
            format = VLCBOpcode.opcodes[opcode]['format']
            data_parsed['opcode'] = VLCBOpcode.opcodes[opcode]['opc']
        format_fields = format.split(',')
        # Remove data as added to dict so when reach 0 we are complete
        # parse each of the fields
        for this_field in format_fields:
            # If no format then skip and add any data at end
            if this_field == "":
                break
            # If unknown then flag here - should only get this during unittests if a new format is added
            if this_field not in VLCBOpcode.field_formats.keys():
                logging.warning (f"Warning format field {this_field} not recognised")
                this_field = "Unknown"
            # Take number of bytes from remaining data
            # Check enough first - if not then add warning
            num_chars = VLCBOpcode.field_formats[this_field][0] 
            if len(data) < num_chars :
                data_parsed[this_field] = f"Insufficient data {data}"
                # remove remaining
                data = ""
            else:
                # Move number of chars (typically 2 chars per byte) into this_val
                this_val = data[0:num_chars]
                data = data[num_chars:]
                # if number expected then convert
                if VLCBOpcode.field_formats[this_field][1] != "char":
                    this_val = int(this_val, 16)
                data_parsed[this_field] = this_val
        # remaining data added to final field (shouldn't normally get this)
        if len(data) > 0:
            data_parsed["ExtraData"] = data
        return data_parsed

# Alias for backwards compability 
# Deprecated
VLCBformat = VLCBFormat
VLCBopcode = VLCBOpcode
