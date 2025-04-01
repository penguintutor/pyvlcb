# Class for handling VLCB data formatting

class VLCB:
    # 127 is default canid for canusb4
    def __init__ (self, canid=127):
        pass
    
    # Takes input bytestring and parses header / data
    # Does not try and interpret op-code - that is left to VLCB_format
    def parse_input (self, input_bytes):
        input_string = input_bytes.decode("utf-8")
        if (input_string[0] != ":"):
            print ("No start frame")
            return False
        if (input_string[1] != "S"):
            print ("Format not supported - only Standard frames allowed")
            return False
        header = input_string[2:6]
        header_val = int(header, 16)
        print (f"Header {hex(header_val)}")
        priority = (header_val & 0xf000) >> 12
        print (f"Priority {priority:b}")
        can_id = (header_val & 0xfe0) >> 5
        print (f"Can ID {can_id}")
        # Next is N / RTR can be ignored
        print (f"N / RTR {input_string[6]}")
        # Data is rest excluding ; which was already stripped during read
        data = input_string[7:]
        print (f"Data {data}")
        # Creates a VLCB_format and returns that
        return VLCBformat (priority, can_id, data)
    
    def discover (self):
        return b':SB780N0D;'
        
        
# Handles a single packet
class VLCBformat:
    def __init__ (self, priority, can_id, data):
        self.priority = priority # Priority is actually high and low priority (2bit high / 2bit low) but just treated as single value
        self.can_id = can_id
        self.data = data # Data is left as hex string
        
    # Lookup OpCode
    def opcode (self):
        if self.data[0:2] in VLCBopcode.opcodes.keys():
            return VLCBopcode.opcodes[self.data[0:2]]['opc']
        return '??'
        
    def __str__ (self):
        return f'{self.priority} : {self.can_id} : {self.data[0:2]} : {self.opcode()} : {self.data}'

        
class VLCBopcode:
    
    # Dict from opcode to dict of opcode information
    opcodes = {
        '00':  {'opc': 'ACK', 'title': 'General Acknowledgement', 'format': '', 'minpri': 2, 'comment': 'Positive response to query/request performed for report of availability online'},
        '01':  {'opc': 'NAK', 'title': 'General No Ack', 'format': '', 'minpri': 2, 'comment': 'Negaive response to query/request denied'},
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
        '3F':  {'opc': 'EXTC', 'title': 'Extended op-code with no additional bytes', 'format': 'extopc', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        #AddrH,AddrL = Address of the decoder - 7 bit addresses have (AddrH=0). 14 bit addresses have bits 6,7 of AddrH set to 1.
        '40':  {'opc': 'RLOC', 'title': 'Request engine session', 'format': 'AddrH,AddrL', 'minpri': 2, 'comment': 'The command station responds with (PLOC) if engine is free and is being assigned. Otherwise responds with (ERR): engine in use or (ERR:) stack full. This command is typically sent by a cab to the command station following a change of the controlled decoder address. RLOC is exactly equivalent to GLOC with all flag bits set to zero, but command stations must continue to support RLOC for backwards compatibility.'},
        # ConID = Consist address
        # Index = Engine index of the consist
        '41':  {'opc': 'QCON', 'title': 'Query Consist', 'format': 'ConID,Index', 'minpri': 2, 'comment': 'Allows enumeration of a consist. Command station responds with PLOC if an engine exists at the specified index, otherwise responds with ERR: no more engines'},
        # NNHigh = high byte of the node number
        # NNLow = low byte of the node number
        '42':  {'opc': 'SNN', 'title': 'Set Node Number', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to assign a node number to a requesting node in response to a RQNN message. The target node must be in ?setup? mode.'},
        # AllocCode = specific allocation code (1 byte)
        '43':  {'opc': 'ALOC', 'title': 'Allocate loco to activity', 'format': 'Session,AllocCode', 'minpri': 2, 'comment': ''},
        '44':  {'opc': 'STMOD', 'title': 'Set CAB session mode', 'format': 'session,MMMMMMMM', 'minpri': 2, 'comment': 'MMMMMMMM = mode bits: 0 ? 1: speed mode; 00 ? 128 speed steps; 01 ? 14 speed steps; 10 ? 28 speed steps with interleave steps; 11 ? 28 speed steps; 2: service mode; 3: sound control mode'},
        # Consist is consist address (8 bits)
        '45':  {'opc': 'PCON', 'title': 'Consist Engine', 'format': 'Session,Consist', 'minpri': 2, 'comment': 'Adds a decoder to a consist. Dat2 has bit 7 set if consist direction is reversed.'},
        '46':  {'opc': 'KCON', 'title': 'Remove Engine from consist', 'format': 'Session,Consist', 'minpri': 2, 'comment': 'Removes a loco from a consist.'},
        # SpeedDir = Speed/dir value. Most significant bit is direction and 7 bits are unsigned speed value. 
        '47':  {'opc': 'DSPD', 'title': 'Set Engine Speed/Dir', 'format': 'Session,SpeedDir', 'minpri': 0, 'comment': 'the unsigned speed value. Sent by a CAB or equivalent to request an engine speed/dir change.'},
        # DDDDDDDD - Is speed flags
        '48':  {'opc': 'DFLG', 'title': 'Set Engine Flags', 'format': 'Session,DDDDDDDD', 'minpri': 2, 'comment': 'Bits 0-1: Speed Mode 00 ? 128 speed steps; 01 ? 14 speed steps; 10 ? 28 speed steps with interleave steps; 11 ? 28 speed steps Bit 2: Lights On/OFF; Bit 3: Engine relative direction; Bits 4-5: Engine state (active =0 , consisted =1, consist master=2, inactive=3) Bits 6-7: Reserved.; Sent by a cab to notify the command station of a change in engine flags.'},
        # Fnum = Function number, 0 to 27
        '49':  {'opc': 'DFNON', 'title': 'Set Engine function on', 'format': 'Session,Fnum', 'minpri': 2, 'comment': 'Sent by a cab to turn on a specific loco function. This provides an alternative method to DFUN for controlling loco functions. A command station must implement both methods.'},
        '4C':  {'opc': 'SSTAT', 'title': 'Service mode status', 'format': 'Session,Status', 'minpri': 3, 'comment': 'Status returned by command station/programmer at end of programming operation that does not return data.'},
        '50':  {'opc': 'RQNN', 'title': 'Request node number', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a node that is in setup/configuration mode and requests assignment of a node number (NN). The node allocating node numbers responds with (SNN) which contains the newly assigned node number. <NN hi> and <NN lo> are the existing node number, if the node has one. If it does not yet have a node number, these bytes should be set to zero.'},
        '51':  {'opc': 'NNREL', 'title': 'Node number release', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by node when taken out of service. e.g. when reverting to SLiM mode.'},
        '52':  {'opc': 'NNACK', 'title': 'Node number acknowledge', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a node to verify its presence and confirm its node id. This message is sent to acknowledge an SNN.'},
        '53':  {'opc': 'NNLRN', 'title': 'Set node into learn mode', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to put a specific node into learn mode.'},
        '54':  {'opc': 'NNULN', 'title': 'Release node from learn mode', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to take node out of learn mode and revert to normal operation.'},
        '55':  {'opc': 'NNCLR', 'title': 'Clear all events from a node', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to clear all events from a specific node. Must be in learn mode first to safeguard against accidental erasure of all events.'},
        '56':  {'opc': 'NNEVN', 'title': 'Read number of events available in a node', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to read the number of available event slots in a node.Response is EVLNF (0x70)'},
        '57':  {'opc': 'NERD', 'title': 'Read back all stored events in a node', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to read all the stored events in a node. Response is 0xF2.'},
        '58':  {'opc': 'RQEVN', 'title': 'Request to read number of stored events', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a configuration tool to read the number of stored events in a node. Response is 0x74( NUMEV).'},
        '59':  {'opc': 'WRACK', 'title': 'Write acknowledge', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by a node to indicate the completion of a write to memory operation. All nodes must issue WRACK when a write operation to node variables, events or event variables has completed. This allows for teaching nodes where the processing time may be slow.'},
        '5A':  {'opc': 'RQDAT', 'title': 'Request node data event', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'Sent by one node to read the data event from another node.(eg: RFID data). Response is 0xF7 (ARDAT).'},
        # DN = Device number
        '5B':  {'opc': 'RQDDS', 'title': 'Request device data - short mode', 'format': 'DNHigh,DNLow', 'minpri': 3, 'comment': 'To request a data set from a device using the short event method. where DN is the device number. Response is 0xFB (DDRS)'},
        '5C':  {'opc': 'BOOTM', 'title': 'Put node into bootload mode', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'For SliM nodes with no NN then the NN of the command must be zero. For SLiM nodes with an NN, and all FLiM nodes the command must contain the NN of the target node. Sent by a configuration tool to prepare for loading a new program.'},
        '5D':  {'opc': 'ENUM', 'title': 'Force a self enumeration cyble for use with CAN', 'format': 'NNHigh,NNLow', 'minpri': 3, 'comment': 'For nodes in FLiM using CAN as transport. This OPC will force a self-enumeration cycle for the specified node. A new CAN_ID will be allocated if needed. Following the ENUM sequence, the node should issue a NNACK to confirm completion and verify the new CAN_ID. If no CAN_ID values are available, an error message 7 will be issued instead.'},
        '5F':  {'opc': 'EXTC1', 'title': 'Extended op-code with 1 additional byte', 'format': 'Extopc, <byte>', 'minpri': 3, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        # 3rd data section
        '60':  {'opc': 'DFUN', 'title': 'Set Engine functions', 'format': 'Session,Fn1,Fn2', 'minpri': 2, 'comment': '<Dat2> (Fn1) is the function range. 1 is F0(FL) to F4; 2 is F5 to F8; 3 is F9 to F12; 4 is F13 to F20; 5 is F21 to F28; <Dat3> (Fn2) is the NMRA DCC format function byte for that range in corresponding bits. Sent by a CAB or equivalent to request an engine Fn state change.'},
        '61':  {'opc': 'GLOC', 'title': 'Get engine session', 'format': 'Dat1,Dat2,Flags', 'minpri': 2, 'comment': '<Dat1> and <Dat2> are [AddrH] and [AddrL] of the decoder, respectively.; 7 bit addresses have (AddrH=0).; 14 bit addresses have bits 6,7 of AddrH set to 1.; <Flags> contains flag bits as follows:Bit 0: Set for "Steal" mode; Bit 1: Set for "Share" mode; Both bits set to 0 is exactly equivalent to an RLOC request; Both bits set to 1 is invalid, because the 2 modes are mutually exclusive; The command station responds with (PLOC) if the request is successful. Otherwise responds with (ERR): engine in use. (ERR:) stack full or (ERR) no session. The latter indicates that there is no current session to steal/share depending on the flag bits set in the request. GLOC with all flag bits set to zero is exactly equivalent to RLOC, but command stations must continue to support RLOC for backwards compatibility.'},
        '63':  {'opc': 'ERR', 'title': 'Command station error report', 'format': 'Dat1,Dat2,Dat3', 'minpri': 2, 'comment': 'Sent in response to an error situation by a command station.'},
        '6F':  {'opc': 'CMDERR', 'title': 'Error messages from nodes during configuration', 'format': 'NNHigh,NNLow,Error', 'minpri': 3, 'comment': 'Sent by node if there is an error when a configuration command is sent.'},
        '70':  {'opc': 'EVNLF', 'title': 'Event space left reply from node', 'format': 'NNHigh,NNLow,EVSPC', 'minpri': 3, 'comment': 'EVSPC is a one byte value giving the number of available events left in that node.'},
        '71':  {'opc': 'NVRD', 'title': 'Request read of a node variable', 'format': 'NNHigh,NNlow,NV', 'minpri': 3, 'comment': 'NV# is the index for the node variable value requested. Response is NVANS.'},
        '72':  {'opc': 'NENRD', 'title': 'Request read of stored events by event index', 'format': 'NNHigh,NNLow,En', 'minpri': 3, 'comment': 'EN# is the index for the stored event requested. Response is 0xF2 (ENRSP)'},
        '73':  {'opc': 'RQNPN', 'title': 'Request read of a node parameter by index', 'format': 'NNHigh,NNLow,Para', 'minpri': 3, 'comment': 'Para# is the index for the parameter requested. Index 0 returns the number of available parameters, Response is 0x9B (PARAN).'},
        '74':  {'opc': 'NUMEV', 'title': 'Number of events stored in node', 'format': 'NNHigh,NNLow,NumEvents', 'minpri': 3, 'comment': 'Response to request 0x58 (RQEVN)'},
        '75':  {'opc': 'CANID', 'title': 'Set a CAN_ID in existing FLiM node', 'format': 'NNHigh,NNLow,CAN_ID', 'minpri': 0, 'comment': 'Used to force a specified CAN_ID into a node. Value range is from 1 to 0x63 (99 decimal) This OPC must be used with care as duplicate CAN_IDs are not allowed. Values outside the permitted range will produce an error 7 message and the CAN_ID will not change.'},
        '7F':  {'opc': 'EXTC2', 'title': 'Extended op-code with 2 additional bytes', 'format': 'Extopc,byte1,byte2', 'minpri': 0, 'comment': 'Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs'},
        # 4 data byte packets
        '80':  {'opc': 'RDCC3', 'title': 'Request 3-byte DCC Packet', 'format': 'Rep,Byte0,Byte1,Byte2', 'minpri': 3, 'comment': '<Dat1(REP)> is number of repetitions in sending the packet. <Dat2>..<Dat4> 3 bytes of the DCC packet. Allows a CAB or equivalent to request a 3 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis. Note: a 3 byte DCC packet is the minimum allowed.'},
        '82':  {'opc': 'WCVO', 'title': 'Write CV (byte) in OPS mode', 'format': 'Session,HighCV,LowCV,Val', 'minpri': 2, 'comment': '<Dat1> is the session number of the loco to be written to; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the byte value to be written; Sent to the command station to write a DCC CV byte in OPS mode to specific loco.(on the main)'},
        '83':  {'opc': 'WCVB', 'title': 'Write CV (bit) in OPS mode', 'format': 'Session,HighCV,LowCV,Val', 'minpri': 2, 'comment': '<Dat1> is the session number of the loco to be written to; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the value to be written; The format for Dat4 is that specified in RP 9.2.1 for OTM bit manipulation in a DCC packet.; This is ?111CDBBB? where C is here is always 1 as only ?writes? are possible OTM. (unless some loco ACK scheme like RailCom is used). D is the bit value, either 0 or 1 and BBB is the bit position in the CV byte. 000 to 111 for bits 0 to 7.; Sent to the command station to write a DCC CV in OPS mode to specific loco.(on the main)'},
        '84':  {'opc': 'QCVS', 'title': 'Read CV', 'format': 'Session,HighCV,LowCV,Mode', 'minpri': 2, 'comment': 'This command is used exclusively with service mode.; Sent by the cab to the command station in order to read a CV value. The command station shall respond with a PCVS message containing the value read, or SSTAT if the CV cannot be read.'},
        '85':  {'opc': 'PCVS', 'title': 'Report CV', 'format': 'Session,HighCV,LowCV,Val', 'minpri': 2, 'comment': '<Dat1> is the session number of the cab; <Dat2> is the MSB # of the CV read (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV read; <Dat4> is the read value; This command is used exclusively with service mode.; Sent by the command station to report a read CV.'},
        '90':  {'opc': 'ACON', 'title': 'Accessory ON', 'format': 'NNHigh,NNLow,EnHigh,EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ?ON? event using the full event number of 4 bytes. (long event)'},
        '91':  {'opc': 'ACOFF', 'title': 'Accessory OFF', 'format': 'NNHigh,NNLow,EnHigh,EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ?OFF? event using the full event number of 4 bytes. (long event)'},
        '92':  {'opc': 'AREQ', 'title': 'Accessory Request Event', 'format': 'NNHigh,NNLow,EnHigh,EnLow', 'minpri': 3, 'comment': '<Dat1> is the high byte of the node number (MS WORD of the full event #); <Dat2> is the low byte of the node number (MS WORD of the full event #); <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates a ?request? event using the full event number of 4 bytes. (long event); A request event is used to elicit a status response from a producer when it is required to know the state of the producer without producing an ON or OFF event and to trigger an event from a combi node'},
        '93':  {'opc': 'ARON', 'title': 'Accessory Response Event', 'format': 'NNHigh,NNLow,EnHigh,EnLow', 'minpri': 3, 'comment': 'Indicates an ?ON? response event. A response event is a reply to a status request (AREQ) without producing an ON or OFF event.'},
        'B6':  {'opc': 'PNN', 'title': 'Response to Query Node', 'format': 'NNHigh,NNLow,ManufId,ModId,Flags', 'minpri': 3, 'comment': '<NN Hi> is the high byte of the node number; <NN Lo> is the low byte of the node number; <Manuf Id> is the Manufacturer id as defined in the node parameters; <Module Id> is the Module Type Id id as defined in the node parameters; <Flags> is the node flags as defined in the node parameters. The Flags byte contains bit flags as follows:; Bit 0: Set to 1 for consumer node; Bit 1: Set to 1 for producer node; Bit 2: Set to 1 for FLiM mode; Bit 3: Set to 1 for Bootloader compatible; If a module is both a producer and a consumer then it is referred to as a combi node and; both flags will be set.; Every node should send this message in response to a QNN message.'}        
        }

    # Create an opcode object if required
    # Or access relevant opcode directly as a class variable
    def __init__ (self):
        pass
    