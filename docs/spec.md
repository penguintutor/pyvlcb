# Protocol OpCodes

| OpCode | Hex: 00 Decimal 0 |
| :--- | :--- |
| Name | ACK |
| Title | General Acknowledgement |
| Args / data | *None* |
| Priority | 2 |
| Description | Positive response to query/request performed for report of availability online |

---

| OpCode | Hex: 01 Decimal 1 |
| :--- | :--- |
| Name | NAK |
| Title | General No Ack |
| Args / data | *None* |
| Priority | 2 |
| Description | Negative response to query/request denied |

---

| OpCode | Hex: 02 Decimal 2 |
| :--- | :--- |
| Name | HLT |
| Title | Bus Halt |
| Args / data | *None* |
| Priority | 0 |
| Description | Commonly broadcasted to all nodes to indicate CBUS is not available and no further packets should be sent until a BON or ARST is received |

---

| OpCode | Hex: 03 Decimal 3 |
| :--- | :--- |
| Name | BON |
| Title | Bus On |
| Args / data | *None* |
| Priority | 1 |
| Description | Commonly broadcasted to all nodes to indicate CBUS is available following a HLT. |

---

| OpCode | Hex: 04 Decimal 4 |
| :--- | :--- |
| Name | TOF |
| Title | Track Off |
| Args / data | *None* |
| Priority | 1 |
| Description | Commonly broadcasted to all nodes by a command station to indicate track power is off and no further command packets should be sent, except inquiries.. |

---

| OpCode | Hex: 05 Decimal 5 |
| :--- | :--- |
| Name | TON |
| Title | Track On |
| Args / data | *None* |
| Priority | 1 |
| Description | Commonly broadcasted to all nodes by a command station to indicate track power is on. |

---

| OpCode | Hex: 06 Decimal 6 |
| :--- | :--- |
| Name | ERSTOP |
| Title | Emergency Stop |
| Args / data | *None* |
| Priority | 1 |
| Description | Commonly broadcase to all nodes by a command station to indicate all engines have been emergency stopped. |

---

| OpCode | Hex: 07 Decimal 7 |
| :--- | :--- |
| Name | ARST |
| Title | System Reset |
| Args / data | *None* |
| Priority | 0 |
| Description | Commonly broadcasted to all nodes to indicate a full system reset. |

---

| OpCode | Hex: 08 Decimal 8 |
| :--- | :--- |
| Name | RTOF |
| Title | Request Track Off |
| Args / data | *None* |
| Priority | 1 |
| Description | Sent to request change of track power to off. |

---

| OpCode | Hex: 09 Decimal 9 |
| :--- | :--- |
| Name | RTON |
| Title | Request Track On |
| Args / data | *None* |
| Priority | 1 |
| Description | Sent to request change of track power to on. |

---

| OpCode | Hex: 0A Decimal 10 |
| :--- | :--- |
| Name | RESTP |
| Title | Request Emergency Stop All |
| Args / data | *None* |
| Priority | 0 |
| Description | Sent to request an emergency stop to all trains . Does not affect accessory control. |

---

| OpCode | Hex: 0C Decimal 12 |
| :--- | :--- |
| Name | RSTAT |
| Title | Request Command Station Status |
| Args / data | *None* |
| Priority | 2 |
| Description | Sent to query the status of the command station. See description of (STAT) for the response from the command station. |

---

| OpCode | Hex: 0D Decimal 13 |
| :--- | :--- |
| Name | QNN |
| Title | Query node number |
| Args / data | *None* |
| Priority | 3 |
| Description | Sent by a node to elicit a PNN reply from each node on the bus that has a node number. See OpCode 0xB6 |

---

| OpCode | Hex: 10 Decimal 16 |
| :--- | :--- |
| Name | RQNP |
| Title | Request node parameters |
| Args / data | *None* |
| Priority | 3 |
| Description | Sent to a node while in ?setup?mode to read its parameter set. Used when initially configuring a node. |

---

| OpCode | Hex: 11 Decimal 17 |
| :--- | :--- |
| Name | RQMN |
| Title | Request module name |
| Args / data | *None* |
| Priority | 2 |
| Description | Sent by a node to request the name of the type of module that is in setup mode. The module in setup mode will reply with opcode NAME. See OpCode 0xE2 |

---

| OpCode | Hex: 21 Decimal 33 |
| :--- | :--- |
| Name | KLOC |
| Title | Release Engine |
| Args / data | Session |
| Priority | 2 |
| Description | Sent by a CAB to the Command Station. The engine with that Session number is removed from the active engine list. |

---

| OpCode | Hex: 22 Decimal 34 |
| :--- | :--- |
| Name | QLOC |
| Title | Query Engine |
| Args / data | Session |
| Priority | 2 |
| Description | The command station responds with PLOC if the session is assigned. Otherwise responds with ERR: engine not found. |

---

| OpCode | Hex: 23 Decimal 35 |
| :--- | :--- |
| Name | DKEEP |
| Title | Session keep alive |
| Args / data | Session |
| Priority | 2 |
| Description | The cab sends a keep alive at regular intervals for the active session. The interval between keep alive messages must be less than the session timeout implemented by the command station. |

---

| OpCode | Hex: 30 Decimal 48 |
| :--- | :--- |
| Name | DBG1 |
| Title | Debug with one data byte |
| Args / data | Status |
| Priority | 2 |
| Description | <Dat1> is a freeform status byte for debugging during CBUS module development. Not used during normal operation |

---

| OpCode | Hex: 3F Decimal 63 |
| :--- | :--- |
| Name | EXTC |
| Title | Extended op-code with no additional bytes |
| Args / data | ExtOpc |
| Priority | 3 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs |

---

| OpCode | Hex: 40 Decimal 64 |
| :--- | :--- |
| Name | RLOC |
| Title | Request engine session |
| Args / data | AddrHigh_AddrLow |
| Priority | 2 |
| Description | The command station responds with (PLOC) if engine is free and is being assigned. Otherwise responds with (ERR): engine in use or (ERR:) stack full. This command is typically sent by a cab to the command station following a change of the controlled decoder address. RLOC is exactly equivalent to GLOC with all flag bits set to zero, but command stations must continue to support RLOC for backwards compatibility. |

---

| OpCode | Hex: 41 Decimal 65 |
| :--- | :--- |
| Name | QCON |
| Title | Query Consist |
| Args / data | Consist,Index |
| Priority | 2 |
| Description | Allows enumeration of a consist. Command station responds with PLOC if an engine exists at the specified index, otherwise responds with ERR: no more engines |

---

| OpCode | Hex: 42 Decimal 66 |
| :--- | :--- |
| Name | SNN |
| Title | Set Node Number |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to assign a node number to a requesting node in response to a RQNN message. The target node must be in ?setup? mode. |

---

| OpCode | Hex: 43 Decimal 67 |
| :--- | :--- |
| Name | ALOC |
| Title | Allocate loco to activity |
| Args / data | Session,AllocCode |
| Priority | 2 |
| Description | *None* |

---

| OpCode | Hex: 44 Decimal 68 |
| :--- | :--- |
| Name | STMOD |
| Title | Set CAB session mode |
| Args / data | Session,Mode |
| Priority | 2 |
| Description | MMMMMMMM = mode bits: 0 ? 1: speed mode; 00 ? 128 speed steps; 01 ? 14 speed steps; 10 ? 28 speed steps with interleave steps; 11 ? 28 speed steps; 2: service mode; 3: sound control mode |

---

| OpCode | Hex: 45 Decimal 69 |
| :--- | :--- |
| Name | PCON |
| Title | Consist Engine |
| Args / data | Session,Consist |
| Priority | 2 |
| Description | Adds a decoder to a consist. Dat2 has bit 7 set if consist direction is reversed. |

---

| OpCode | Hex: 46 Decimal 70 |
| :--- | :--- |
| Name | KCON |
| Title | Remove Engine from consist |
| Args / data | Session,Consist |
| Priority | 2 |
| Description | Removes a loco from a consist. |

---

| OpCode | Hex: 47 Decimal 71 |
| :--- | :--- |
| Name | DSPD |
| Title | Set Engine Speed/Dir |
| Args / data | Session,SpeedDir |
| Priority | 0 |
| Description | the unsigned speed value. Sent by a CAB or equivalent to request an engine speed/dir change. |

---

| OpCode | Hex: 48 Decimal 72 |
| :--- | :--- |
| Name | DFLG |
| Title | Set Engine Flags |
| Args / data | Session,SpeedFlag |
| Priority | 2 |
| Description | Bits 0-1: Speed Mode 00 ? 128 speed steps; 01 ? 14 speed steps; 10 ? 28 speed steps with interleave steps; 11 ? 28 speed steps Bit 2: Lights On/OFF; Bit 3: Engine relative direction; Bits 4-5: Engine state (active =0 , consisted =1, consist master=2, inactive=3) Bits 6-7: Reserved.; Sent by a cab to notify the command station of a change in engine flags. |

---

| OpCode | Hex: 49 Decimal 73 |
| :--- | :--- |
| Name | DFNON |
| Title | Set Engine function on |
| Args / data | Session,Fnum |
| Priority | 2 |
| Description | Sent by a cab to turn on a specific loco function. This provides an alternative method to DFUN for controlling loco functions. A command station must implement both methods. |

---

| OpCode | Hex: 4C Decimal 76 |
| :--- | :--- |
| Name | SSTAT |
| Title | Service mode status |
| Args / data | Session,Status |
| Priority | 3 |
| Description | Status returned by command station/programmer at end of programming operation that does not return data. |

---

| OpCode | Hex: 50 Decimal 80 |
| :--- | :--- |
| Name | RQNN |
| Title | Request node number |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a node that is in setup/configuration mode and requests assignment of a node number (NN). The node allocating node numbers responds with (SNN) which contains the newly assigned node number. <NN hi> and <NN lo> are the existing node number, if the node has one. If it does not yet have a node number, these bytes should be set to zero. |

---

| OpCode | Hex: 51 Decimal 81 |
| :--- | :--- |
| Name | NNREL |
| Title | Node number release |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by node when taken out of service. e.g. when reverting to SLiM mode. |

---

| OpCode | Hex: 52 Decimal 82 |
| :--- | :--- |
| Name | NNACK |
| Title | Node number acknowledge |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a node to verify its presence and confirm its node id. This message is sent to acknowledge an SNN. |

---

| OpCode | Hex: 53 Decimal 83 |
| :--- | :--- |
| Name | NNLRN |
| Title | Set node into learn mode |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to put a specific node into learn mode. Deprecated - replaced by MODE |

---

| OpCode | Hex: 54 Decimal 84 |
| :--- | :--- |
| Name | NNULN |
| Title | Release node from learn mode |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to take node out of learn mode and revert to normal operation. |

---

| OpCode | Hex: 55 Decimal 85 |
| :--- | :--- |
| Name | NNCLR |
| Title | Clear all events from a node |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to clear all events from a specific node. Must be in learn mode first to safeguard against accidental erasure of all events. |

---

| OpCode | Hex: 56 Decimal 86 |
| :--- | :--- |
| Name | NNEVN |
| Title | Read number of events available in a node |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to read the number of available event slots in a node.Response is EVLNF (0x70) |

---

| OpCode | Hex: 57 Decimal 87 |
| :--- | :--- |
| Name | NERD |
| Title | Read back all stored events in a node |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to read all the stored events in a node. Response is 0xF2. |

---

| OpCode | Hex: 58 Decimal 88 |
| :--- | :--- |
| Name | RQEVN |
| Title | Request to read number of stored events |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a configuration tool to read the number of stored events in a node. Response is 0x74( NUMEV). |

---

| OpCode | Hex: 59 Decimal 89 |
| :--- | :--- |
| Name | WRACK |
| Title | Write acknowledge |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by a node to indicate the completion of a write to memory operation. All nodes must issue WRACK when a write operation to node variables, events or event variables has completed. This allows for teaching nodes where the processing time may be slow. Deprecated replaced by GRSP |

---

| OpCode | Hex: 5A Decimal 90 |
| :--- | :--- |
| Name | RQDAT |
| Title | Request node data event |
| Args / data | NN |
| Priority | 3 |
| Description | Sent by one node to read the data event from another node.(eg: RFID data). Response is 0xF7 (ARDAT). |

---

| OpCode | Hex: 5B Decimal 91 |
| :--- | :--- |
| Name | RQDDS |
| Title | Request device data - short mode |
| Args / data | DNHigh_DNLow |
| Priority | 3 |
| Description | To request a data set from a device using the short event method. where DN is the device number. Response is 0xFB (DDRS) |

---

| OpCode | Hex: 5C Decimal 92 |
| :--- | :--- |
| Name | BOOTM |
| Title | Put node into bootload mode |
| Args / data | NN |
| Priority | 3 |
| Description | For SliM nodes with no NN then the NN of the command must be zero. For SLiM nodes with an NN, and all FLiM nodes the command must contain the NN of the target node. Sent by a configuration tool to prepare for loading a new program. Deprecated replaced by MODE |

---

| OpCode | Hex: 5D Decimal 93 |
| :--- | :--- |
| Name | ENUM |
| Title | Force a self enumeration cyble for use with CAN |
| Args / data | NN |
| Priority | 3 |
| Description | For nodes in FLiM using CAN as transport. This OPC will force a self-enumeration cycle for the specified node. A new CAN_ID will be allocated if needed. Following the ENUM sequence, the node should issue a NNACK to confirm completion and verify the new CAN_ID. If no CAN_ID values are available, an error message 7 will be issued instead. Deprecated replaced with automatic self enumeration. |

---

| OpCode | Hex: 5F Decimal 95 |
| :--- | :--- |
| Name | EXTC1 |
| Title | Extended op-code with 1 additional byte |
| Args / data | ExtOpc,Byte1 |
| Priority | 3 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs |

---

| OpCode | Hex: 60 Decimal 96 |
| :--- | :--- |
| Name | DFUN |
| Title | Set Engine functions |
| Args / data | Session,Fn1,Fn2 |
| Priority | 2 |
| Description | <Dat2> (Fn1) is the function range. 1 is F0(FL) to F4; 2 is F5 to F8; 3 is F9 to F12; 4 is F13 to F20; 5 is F21 to F28; <Dat3> (Fn2) is the NMRA DCC format function byte for that range in corresponding bits. Sent by a CAB or equivalent to request an engine Fn state change. |

---

| OpCode | Hex: 61 Decimal 97 |
| :--- | :--- |
| Name | GLOC |
| Title | Get engine session |
| Args / data | AddrHigh_AddrLow,Flags |
| Priority | 2 |
| Description | <Dat1> and <Dat2> are [AddrH] and [AddrL] of the decoder, respectively.; 7 bit addresses have (AddrH=0).; 14 bit addresses have bits 6,7 of AddrH set to 1.; <Flags> contains flag bits as follows:Bit 0: Set for "Steal" mode; Bit 1: Set for "Share" mode; Both bits set to 0 is exactly equivalent to an RLOC request; Both bits set to 1 is invalid, because the 2 modes are mutually exclusive; The command station responds with (PLOC) if the request is successful. Otherwise responds with (ERR): engine in use. (ERR:) stack full or (ERR) no session. The latter indicates that there is no current session to steal/share depending on the flag bits set in the request. GLOC with all flag bits set to zero is exactly equivalent to RLOC, but command stations must continue to support RLOC for backwards compatibility. |

---

| OpCode | Hex: 63 Decimal 99 |
| :--- | :--- |
| Name | ERR |
| Title | Command station error report |
| Args / data | Byte1,Byte2,ErrCode |
| Priority | 2 |
| Description | Sent in response to an error situation by a command station. |

---

| OpCode | Hex: 6F Decimal 111 |
| :--- | :--- |
| Name | CMDERR |
| Title | Error messages from nodes during configuration |
| Args / data | NN,Error |
| Priority | 3 |
| Description | Sent by node if there is an error when a configuration command is sent. Deprecated replaced by GRSP. |

---

| OpCode | Hex: 70 Decimal 112 |
| :--- | :--- |
| Name | EVNLF |
| Title | Event space left reply from node |
| Args / data | NN,EVSPC |
| Priority | 3 |
| Description | EVSPC is a one byte value giving the number of available events left in that node. |

---

| OpCode | Hex: 71 Decimal 113 |
| :--- | :--- |
| Name | NVRD |
| Title | Request read of a node variable |
| Args / data | NN,NVIndex |
| Priority | 3 |
| Description | NV# is the index for the node variable value requested. Response is NVANS. VLCB also returns GRSP and support for NV#0. |

---

| OpCode | Hex: 72 Decimal 114 |
| :--- | :--- |
| Name | NENRD |
| Title | Request read of stored events by event index |
| Args / data | NN,EnIndex |
| Priority | 3 |
| Description | EN# is the index for the stored event requested. Response is 0xF2 (ENRSP) |

---

| OpCode | Hex: 73 Decimal 115 |
| :--- | :--- |
| Name | RQNPN |
| Title | Request read of a node parameter by index |
| Args / data | NN,ParaIndex |
| Priority | 3 |
| Description | Para# is the index for the parameter requested. Index 0 returns the number of available parameters, Response is 0x9B (PARAN). VLCB Para #0 returns a PARAN for each parameter |

---

| OpCode | Hex: 74 Decimal 116 |
| :--- | :--- |
| Name | NUMEV |
| Title | Number of events stored in node |
| Args / data | NN,NumEvents |
| Priority | 3 |
| Description | Response to request 0x58 (RQEVN) |

---

| OpCode | Hex: 75 Decimal 117 |
| :--- | :--- |
| Name | CANID |
| Title | Set a CAN_ID in existing FLiM node |
| Args / data | NN,CAN_ID |
| Priority | 0 |
| Description | Used to force a specified CAN_ID into a node. Value range is from 1 to 0x63 (99 decimal) This OPC must be used with care as duplicate CAN_IDs are not allowed. Values outside the permitted range will produce an error 7 message and the CAN_ID will not change. Deprecated replaced with self-enumaration. VLCB includes GRSP responses. |

---

| OpCode | Hex: 76 Decimal 118 |
| :--- | :--- |
| Name | MODE |
| Title | Request a change to a modules operating mode |
| Args / data | NN,ModeCmd |
| Priority | 0 |
| Description | Request to change the operational mode of the module. Mode cmds 0 = transition to setup mode, 1 = transition to normal mode, 16 = turn on FCU compat, 17 = turn off FCU compat. If supported then module returns GRSP. VLCB new features. |

---

| OpCode | Hex: 78 Decimal 120 |
| :--- | :--- |
| Name | RQSD |
| Title | Request service discover |
| Args / data | NN,ServiceIndex |
| Priority | 0 |
| Description | Request service data from a module if ServiceIndex is 0 then SD message sent, followed by ESD response for each services supported. VLCB new feature. |

---

| OpCode | Hex: 7F Decimal 127 |
| :--- | :--- |
| Name | EXTC2 |
| Title | Extended op-code with 2 additional bytes |
| Args / data | ExtOpc,Byte1,Byte2 |
| Priority | 0 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs |

---

| OpCode | Hex: 80 Decimal 128 |
| :--- | :--- |
| Name | RDCC3 |
| Title | Request 3-byte DCC Packet |
| Args / data | Rep,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | <Dat1(REP)> is number of repetitions in sending the packet. <Dat2>..<Dat4> 3 bytes of the DCC packet. Allows a CAB or equivalent to request a 3 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis. Note: a 3 byte DCC packet is the minimum allowed. |

---

| OpCode | Hex: 82 Decimal 130 |
| :--- | :--- |
| Name | WCVO |
| Title | Write CV (byte) in OPS mode |
| Args / data | Session,CVHigh_CVLow,CVVal |
| Priority | 2 |
| Description | <Dat1> is the session number of the loco to be written to; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the byte value to be written; Sent to the command station to write a DCC CV byte in OPS mode to specific loco.(on the main) |

---

| OpCode | Hex: 83 Decimal 131 |
| :--- | :--- |
| Name | WCVB |
| Title | Write CV (bit) in OPS mode |
| Args / data | Session,CVHigh_CVLow,CVVal |
| Priority | 2 |
| Description | <Dat1> is the session number of the loco to be written to; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the value to be written; The format for Dat4 is that specified in RP 9.2.1 for OTM bit manipulation in a DCC packet.; This is ?111CDBBB? where C is here is always 1 as only ?writes? are possible OTM. (unless some loco ACK scheme like RailCom is used). D is the bit value, either 0 or 1 and BBB is the bit position in the CV byte. 000 to 111 for bits 0 to 7.; Sent to the command station to write a DCC CV in OPS mode to specific loco.(on the main) |

---

| OpCode | Hex: 84 Decimal 132 |
| :--- | :--- |
| Name | QCVS |
| Title | Read CV |
| Args / data | Session,CVHigh_CVLow,Mode |
| Priority | 2 |
| Description | This command is used exclusively with service mode.; Sent by the cab to the command station in order to read a CV value. The command station shall respond with a PCVS message containing the value read, or SSTAT if the CV cannot be read. |

---

| OpCode | Hex: 85 Decimal 133 |
| :--- | :--- |
| Name | PCVS |
| Title | Report CV |
| Args / data | Session,CVHigh_CVLow,CVVal |
| Priority | 2 |
| Description | <Dat1> is the session number of the cab; <Dat2> is the MSB # of the CV read (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV read; <Dat4> is the read value; This command is used exclusively with service mode.; Sent by the command station to report a read CV. |

---

| OpCode | Hex: 87 Decimal 135 |
| :--- | :--- |
| Name | RDGN |
| Title | Request dianostic data |
| Args / data | NN,ServiceIndex,DiagCode |
| Priority | 0 |
| Description | Request diagnostic data from a module. If DiagCode is 0 then all data returned. If ServiceIndex 0 then send DGN message for each service, otherwise send DGN for service specified |

---

| OpCode | Hex: 8E Decimal 142 |
| :--- | :--- |
| Name | NVSETRD |
| Title | Set an NV value with read back |
| Args / data | NN,NNIndex,NVVal |
| Priority | 0 |
| Description | Sets an NV value and responds with the new value, response may not be the value requested. VLCB new feature. |

---

| OpCode | Hex: 90 Decimal 144 |
| :--- | :--- |
| Name | ACON |
| Title | Accessory ON |
| Args / data | NN,EnHigh_EnLow |
| Priority | 3 |
| Description | <Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ?ON? event using the full event number of 4 bytes. (long event) |

---

| OpCode | Hex: 91 Decimal 145 |
| :--- | :--- |
| Name | ACOF |
| Title | Accessory OFF |
| Args / data | NN,EnHigh_EnLow |
| Priority | 3 |
| Description | <Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ?OFF? event using the full event number of 4 bytes. (long event) |

---

| OpCode | Hex: 92 Decimal 146 |
| :--- | :--- |
| Name | AREQ |
| Title | Accessory Request Event |
| Args / data | NN,EnHigh_EnLow |
| Priority | 3 |
| Description | <Dat1> is the high byte of the node number (MS WORD of the full event #); <Dat2> is the low byte of the node number (MS WORD of the full event #); <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates a ?request? event using the full event number of 4 bytes. (long event); A request event is used to elicit a status response from a producer when it is required to know the state of the producer without producing an ON or OFF event and to trigger an event from a combi node |

---

| OpCode | Hex: 93 Decimal 147 |
| :--- | :--- |
| Name | ARON |
| Title | Accessory Response Event |
| Args / data | NN,EnHigh_EnLow |
| Priority | 3 |
| Description | Indicates an ?ON? response event. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: 94 Decimal 148 |
| :--- | :--- |
| Name | AROF |
| Title | Accessory Response Event |
| Args / data | NN,EnHigh_EnLow |
| Priority | 3 |
| Description | <Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; Indicates an ‘OFF’ response event. A response event is a reply to a status request; (AREQ) without producing an ON or OFF event |

---

| OpCode | Hex: 95 Decimal 149 |
| :--- | :--- |
| Name | EVULN |
| Title | Unlearn an event in learn mode |
| Args / data | NN,EnHigh_EnLow |
| Priority | 3 |
| Description | Sent by a configuration tool to remove an event from a node. VLCB also return GRSP. |

---

| OpCode | Hex: 96 Decimal 150 |
| :--- | :--- |
| Name | NVSET |
| Title | Set a node variable |
| Args / data | NN,NVIndex,NVVal |
| Priority | 3 |
| Description | Sent by a configuration tool to set a node variable. NV# is the NV index number. Deprecated replaced by NVSETRD. VLCB also return GRSP. |

---

| OpCode | Hex: 97 Decimal 151 |
| :--- | :--- |
| Name | NVANS |
| Title | Response to a request for a node variable value |
| Args / data | NN,NVIndex,NVVal |
| Priority | 3 |
| Description | Sent by node in response to request. (NVRD) |

---

| OpCode | Hex: 98 Decimal 152 |
| :--- | :--- |
| Name | ASON |
| Title | Accessory short ON |
| Args / data | NN,DNHigh_DNLow |
| Priority | 3 |
| Description | Indicates an ‘ON’ event using the short event number of 2 LS bytes. |

---

| OpCode | Hex: 99 Decimal 153 |
| :--- | :--- |
| Name | ASOF |
| Title | Accessory short OFF |
| Args / data | NN,DNHigh_DNLow |
| Priority | 3 |
| Description | Indicates an ‘OFF’ event using the short event number of 2 LS bytes. |

---

| OpCode | Hex: 9A Decimal 154 |
| :--- | :--- |
| Name | ASRQ |
| Title | Accessory Short Request Event |
| Args / data | NN,DNHigh_DNLow |
| Priority | 3 |
| Description | Indicates a ‘request’ event using the short event number of 2 LS bytes. A request event is used to elicit a response from a producer ‘device’ when it is required to know the ‘state’ of the device without producing an ON or OFF event and to trigger an event from a combi node. |

---

| OpCode | Hex: 9B Decimal 155 |
| :--- | :--- |
| Name | PARAN |
| Title | Response to request for individual node parameter |
| Args / data | NN,ParaIndex,ParaVal |
| Priority | 3 |
| Description | NN is the node number of the sending node. Para# is the index of the parameter and Para val is the parameter value. |

---

| OpCode | Hex: 9C Decimal 156 |
| :--- | :--- |
| Name | REVAL |
| Title | Request for read of an event variable |
| Args / data | NN,EnIndex,EvIndex |
| Priority | 3 |
| Description | This request differs from B2 (REQEV) as it doesn’t need to be in learn mode but does; require the knowledge of the event index to which the EV request is directed.; EN# is the event index. EV# is the event variable index. Response is B5 (NEVAL) |

---

| OpCode | Hex: 9D Decimal 157 |
| :--- | :--- |
| Name | ARSON |
| Title | Accessory short response event |
| Args / data | NN,DNHigh_DNLow |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: 9E Decimal 158 |
| :--- | :--- |
| Name | ARSOF |
| Title | Accessory short response event |
| Args / data | NN,DNHigh_DNLow |
| Priority | 3 |
| Description | ndicates an ‘OFF’ response event. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: 9F Decimal 159 |
| :--- | :--- |
| Name | EXTC3 |
| Title | Extended op-code with 3 additional bytes |
| Args / data | ExtOpc,Byte1,Byte2,Byte3 |
| Priority | 0 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs |

---

| OpCode | Hex: A0 Decimal 160 |
| :--- | :--- |
| Name | RDCC4 |
| Title | Request 4-byte DCC packet |
| Args / data | Rep,Byte1,Byte2,Byte3,Byte4 |
| Priority | 2 |
| Description | <Dat1(REP)> is number of repetitions in sending the packet.; <Dat2>..<Dat5> 4 bytes of the DCC packet.; Allows a CAB or equivalent to request a 4 byte DCC packet to be sent to the track. The; packet is sent <REP> times and is not refreshed on a regular basis. |

---

| OpCode | Hex: A2 Decimal 162 |
| :--- | :--- |
| Name | WCVS |
| Title | Write CV in Service Mode |
| Args / data | Session,CVHigh_CVLow,Mode,CVVal |
| Priority | 0 |
| Description | <Dat1> is the session number of the cab; <Dat2> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat3> is the LSB # of the CV to be written; <Dat4> is the service write mode; <Dat5> is the CV value to be written; Sent to the command station to write a DCC CV in service mode. |

---

| OpCode | Hex: AB Decimal 171 |
| :--- | :--- |
| Name | HEARTB |
| Title | Heartbeat message from module |
| Args / data | NN,Sequence,Status,StatusBits |
| Priority | 0 |
| Description | Hearbeat message from module indicating alive. Sent every 5 seconds by module. Sequence count from 0, incrementing and wrap around to 0., Statis is binary representation of diagnostic status 0x00 is normal operation. StatusBits is reserved set to 0x00. VLCB new feature. |

---

| OpCode | Hex: AC Decimal 172 |
| :--- | :--- |
| Name | SD |
| Title | Service discovery response |
| Args / data | NN,ServiceIndex,ServiceType,Version |
| Priority | 0 |
| Description | Version of service supported response to RQSD with ServiceIndex = 0. First SD response is number of following SD responses. Also see ESD. VLCB new feature. |

---

| OpCode | Hex: AF Decimal 175 |
| :--- | :--- |
| Name | GRSP |
| Title | Generic response |
| Args / data | NN,Opcode,ServiceType,Result |
| Priority | 0 |
| Description | Generic response for a config change request. Result byte indicates ok for success or error code. CMDERR codes are supported. VLCB new feature. |

---

| OpCode | Hex: B0 Decimal 176 |
| :--- | :--- |
| Name | ACON1 |
| Title | Accessory ON |
| Args / data | NN,EnHigh_EnLow,Byte1 |
| Priority | 3 |
| Description | <Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; <Dat5> is an additional data byte; Indicates an ‘ON’ event using the full event number of; 4 bytes with one additional data byte. |

---

| OpCode | Hex: B1 Decimal 177 |
| :--- | :--- |
| Name | ACOF1 |
| Title | Accessory OFF |
| Args / data | NN,EnHigh_EnLow,Byte1 |
| Priority | 3 |
| Description | <Dat1> is the high byte of the node number; <Dat2> is the low byte of the node number; <Dat3> is the high byte of the event number; <Dat4> is the low byte of the event number; <Dat5> is an additional data byte; Indicates an ‘OFF’ event using the full event number of 4 bytes with one additional data byte. |

---

| OpCode | Hex: B2 Decimal 178 |
| :--- | :--- |
| Name | REQEV |
| Title | Read event variable in learn mode |
| Args / data | NN,EnHigh_EnLow,EvIndex |
| Priority | 3 |
| Description | Allows a configuration tool to read stored event variables from a node. EV# is the EV index. Reply is (EVANS) |

---

| OpCode | Hex: B3 Decimal 179 |
| :--- | :--- |
| Name | ARON1 |
| Title | Accessory Response Event |
| Args / data | NN,EnHigh_EnLow,Byte1 |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event with one additional data byte. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: B4 Decimal 180 |
| :--- | :--- |
| Name | AROF1 |
| Title | Accessory Response Event |
| Args / data | NN,EnHigh_EnLow,Byte1 |
| Priority | 3 |
| Description | Indicates an ‘OFF’ response event with one additional data byte. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: B5 Decimal 181 |
| :--- | :--- |
| Name | NEVAL |
| Title | Response to request for read of EV value |
| Args / data | NN,EnIndex,EvIndex,EvVal |
| Priority | 3 |
| Description | NN is the node replying. EN# is the index of the event in that node. EV# is the index of the event variable. EVval is the value of that EV. This is response to 9C (REVAL) |

---

| OpCode | Hex: B6 Decimal 182 |
| :--- | :--- |
| Name | PNN |
| Title | Response to Query Node |
| Args / data | NN,ManufId,ModId,Flags |
| Priority | 3 |
| Description | <NN Hi> is the high byte of the node number; <NN Lo> is the low byte of the node number; <Manuf Id> is the Manufacturer id as defined in the node parameters; <Module Id> is the Module Type Id id as defined in the node parameters; <Flags> is the node flags as defined in the node parameters. The Flags byte contains bit flags as follows:; Bit 0: Set to 1 for consumer node; Bit 1: Set to 1 for producer node; Bit 2: Set to 1 for FLiM mode; Bit 3: Set to 1 for Bootloader compatible; If a module is both a producer and a consumer then it is referred to as a combi node and; both flags will be set.; Every node should send this message in response to a QNN message. |

---

| OpCode | Hex: B8 Decimal 184 |
| :--- | :--- |
| Name | ASON1 |
| Title | Accessory Short ON |
| Args / data | NN,DNHigh_DNLow,Byte1 |
| Priority | 3 |
| Description | Indicates an ‘ON’ event using the short event number of 2 LS bytes with one added data byte. |

---

| OpCode | Hex: B9 Decimal 185 |
| :--- | :--- |
| Name | ASOF1 |
| Title | Accessory Short OFF |
| Args / data | NN,DNHigh_DNLow,Byte1 |
| Priority | 3 |
| Description | Indicates an ‘OFF’ event using the short event number of 2 LS bytes with one added data byte. |

---

| OpCode | Hex: BD Decimal 189 |
| :--- | :--- |
| Name | ARSON1 |
| Title | Accessory Short Response Event with one data byte |
| Args / data | NN,DNHigh_DNLow,Byte1 |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event with one added data byte. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: BE Decimal 190 |
| :--- | :--- |
| Name | ARSOF1 |
| Title | Accessory short response event with one data byte |
| Args / data | NN,DNHigh_DNLow,Byte1 |
| Priority | 3 |
| Description | Indicates an ‘OFF’ response event with one added data byte. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: BF Decimal 191 |
| :--- | :--- |
| Name | EXTC4 |
| Title | Extended op-code with 4 data bytes |
| Args / data | ExtOpc,Byte1,Byte2,Byte3,Byte4 |
| Priority | 3 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs. |

---

| OpCode | Hex: C0 Decimal 192 |
| :--- | :--- |
| Name | RDCC5 |
| Title | Requst 5-byte DCC packet |
| Args / data | Rep,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 2 |
| Description | <Dat1(REP)> is # of repetitions in sending the packet.; <Dat2>..<Dat6> 5 bytes of the DCC packet.; Allows a CAB or equivalent to request a 5 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis. |

---

| OpCode | Hex: C1 Decimal 193 |
| :--- | :--- |
| Name | WCVOA |
| Title | Write CV (byte) in OPS mode by address |
| Args / data | AddrHigh_AddrLow,CVHigh_CVLow,Mode,CVVal |
| Priority | 2 |
| Description | <Dat1> and <Dat2> are [AddrH] and [AddrL] of the decoder, respectively.; 7 bit addresses have (AddrH=0).; 14 bit addresses have bits 7,8 of AddrH set to 1.; <Dat3> is the MSB # of the CV to be written (supports CVs 1 - 65536); <Dat4> is the LSB # of the CV to be written; <Dat5> is the programming mode to be used; <Dat6> is the CV byte value to be written; Sent to the command station to write a DCC CV byte in OPS mode to specific loco (on the main). Used by computer based ops mode programmer that does not have a valid throttle handle. |

---

| OpCode | Hex: C2 Decimal 194 |
| :--- | :--- |
| Name | CABDAT |
| Title | Send data to DCC CAB which is controlling loco |
| Args / data | AddrHigh_AddrLow,DataCode,Byte1,Byte2,Byte3 |
| Priority | 1 |
| Description | Send data to DCC CAB controlling particular loco. CABSIG data1 for aspect1, data2 for aspect2, data3 for speed. Defined in RFC0005. |

---

| OpCode | Hex: C7 Decimal 199 |
| :--- | :--- |
| Name | DGN |
| Title | Dianostic data resonse |
| Args / data | NN,ServiceIndex,DiagCode,DiagVal |
| Priority | 0 |
| Description | Diagnostic data value from a module sent in response to RDGN. VLCB new features |

---

| OpCode | Hex: CF Decimal 207 |
| :--- | :--- |
| Name | FCLK |
| Title | Fast Clock |
| Args / data | DateTime |
| Priority | 3 |
| Description | This addendum defines a time encoding |

---

| OpCode | Hex: D0 Decimal 208 |
| :--- | :--- |
| Name | ACON2 |
| Title | Accessory ON |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2 |
| Priority | 3 |
| Description | Indicates an ‘ON’ event using the full event number of 4 bytes with two additional data bytes. |

---

| OpCode | Hex: D1 Decimal 209 |
| :--- | :--- |
| Name | ACOF2 |
| Title | Accessory OFF |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2 |
| Priority | 3 |
| Description | ndicates an ‘OFF’ event using the full event number of 4 bytes with two additional data bytes. |

---

| OpCode | Hex: D2 Decimal 210 |
| :--- | :--- |
| Name | EVLRN |
| Title | Teach an event in learn mode |
| Args / data | NN,EnHigh_EnLow,EvIndex,EvVal |
| Priority | 3 |
| Description | A node response to a request from a configuration tool for the EVs associated with an event (REQEV). For multiple EVs, there will be one response per request. VLCB also return GRSP. |

---

| OpCode | Hex: D3 Decimal 211 |
| :--- | :--- |
| Name | EVANS |
| Title | Response to a request for an EV value in a node in learn mode |
| Args / data | NN,EnHigh_EnLow,EvIndex,EvVal |
| Priority | 3 |
| Description | A node response to a request from a configuration tool for the EVs associated with an event (REQEV). For multiple EVs, there will be one response per request. |

---

| OpCode | Hex: D4 Decimal 212 |
| :--- | :--- |
| Name | ARON2 |
| Title | Accessory Response Event |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2 |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event with two added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: D5 Decimal 213 |
| :--- | :--- |
| Name | AROF2 |
| Title | Accessory Response Event |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2 |
| Priority | 3 |
| Description | Indicates an ‘OFF’ response event with two added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: D8 Decimal 216 |
| :--- | :--- |
| Name | ASON2 |
| Title | Accessory Short ON |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2 |
| Priority | 3 |
| Description | Indicates an ‘ON’ event using the short event number of 2 LS bytes with two added data bytes. |

---

| OpCode | Hex: DD Decimal 221 |
| :--- | :--- |
| Name | ARSON2 |
| Title | Accessory Short Response Event with two bytes |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2 |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event with two added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: DE Decimal 222 |
| :--- | :--- |
| Name | ARSOF2 |
| Title | Accessory Short Response Event with two bytes |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2 |
| Priority | 3 |
| Description | Indicates an ‘OFF’ response event with two added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: DF Decimal 223 |
| :--- | :--- |
| Name | EXTC5 |
| Title | Extended op-code with 5 data bytes |
| Args / data | ExtOpc,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 3 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs |

---

| OpCode | Hex: E0 Decimal 224 |
| :--- | :--- |
| Name | RDCC6 |
| Title | Request 6 byte DCC packet |
| Args / data | Rep,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 2 |
| Description | Allows a CAB or equivalent to request a 6 byte DCC packet to be sent to the track. The packet is sent <REP> times and is not refreshed on a regular basis. |

---

| OpCode | Hex: E1 Decimal 225 |
| :--- | :--- |
| Name | PLOC |
| Title | Engine Report |
| Args / data | Session,AddrHigh_AddrLow,SpeedDir,Fn1,Fn2,Fn3 |
| Priority | 2 |
| Description | <Dat4> is the Speed/Direction value. Bit 7 is the direction bit and bits 0-6 are the speed value.; <Dat5> is the function byte F0 to F4; <Dat6> is the function byte F5 to F8; <Dat7> is the function byte F9 to F12; A report of an engine entry sent by the command station. Sent in response to QLOC or as an acknowledgement of acquiring an engine requested by a cab (RLOC or GLOC). |

---

| OpCode | Hex: E2 Decimal 226 |
| :--- | :--- |
| Name | NAME |
| Title | Response to request for node name string |
| Args / data | Char1_7 |
| Priority | 3 |
| Description | A node response while in ‘setup’ mode for its name string. Reply to (RQMN). The string for the module type is returned in char1 to char7, space filled to 7 bytes. The Module Name prefix , currently either CAN or ETH, depends on the Interface Protocol parameter, it is not included in the response, see section 12.2 for the definition of the parameters. |

---

| OpCode | Hex: E3 Decimal 227 |
| :--- | :--- |
| Name | STAT |
| Title | Command station status report |
| Args / data | NN,CSNum,Flags,MajRev,MinRev,Build |
| Priority | 2 |
| Description | <NN hi> <NN lo> Gives node id of command station, so further info can be got from parameters or interrogating NVs; <CS num> For future expansion - set to zero at present; <flags> Flags as defined below; <Major rev> Major revision number; <Minor rev> Minor revision letter; <Build no.> Build number, always 0 for a released version.; <flags> is status defined by the bits below.; bits:; 0 - Hardware Error (self test); 1 - Track Error; 2 - Track On/ Off; 3 - Bus On/ Halted; 4 - EM. Stop all performed; 5 - Reset done; 6 - Service mode (programming) On/ Off; 7 – reserved; Sent by the command station in response to RSTAT. |

---

| OpCode | Hex: E7 Decimal 231 |
| :--- | :--- |
| Name | ESD |
| Title | Extended service discovery response |
| Args / data | NN,ServiceIndex,ServiceType,Byte1,Byte2,Byte3 |
| Priority | 0 |
| Description | Detailed information about a service supported by a module. Sent in response to RQSD where ServiceIndex is not 0. VLCB new feature |

---

| OpCode | Hex: E9 Decimal 233 |
| :--- | :--- |
| Name | DTXC |
| Title | Streaming protocol |
| Args / data | StreamID,Sequence,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 0 |
| Description | Used to transport relatively large block of data. StreamID is unique layout wide (> 20). If Sequence num is 0x00 then bytes are MessageLen (2 bytes), CRC16 (2 bytes), Flags (1 byte reserved). Defined in RFC0005 |

---

| OpCode | Hex: EF Decimal 239 |
| :--- | :--- |
| Name | PARAMS |
| Title | Response to request for node parameters |
| Args / data | Para1_7 |
| Priority | 3 |
| Description | A node response while in ‘setup’ mode for its parameter string. Reply to (RQNP) |

---

| OpCode | Hex: F0 Decimal 240 |
| :--- | :--- |
| Name | ACON3 |
| Title | Accessory ON |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an ON event using the full event number of 4 bytes with three additional data bytes. |

---

| OpCode | Hex: F1 Decimal 241 |
| :--- | :--- |
| Name | ACOF3 |
| Title | Accessory OFF |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an OFF event using the full event number of 4 bytes with three additional data bytes. |

---

| OpCode | Hex: F2 Decimal 242 |
| :--- | :--- |
| Name | ENRSP |
| Title | Response to request to read node events |
| Args / data | NN,En3_0,EnIndex |
| Priority | 3 |
| Description | Where the NN is that of the sending node. EN3 to EN0 are the four bytes of the stored event. EN# is the index of the event within the sending node. This is a response to either 57 (NERD) or 72 (NENRD) |

---

| OpCode | Hex: F3 Decimal 243 |
| :--- | :--- |
| Name | ARON3 |
| Title | Acessory Response Event |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event with three added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: F4 Decimal 244 |
| :--- | :--- |
| Name | AROF3 |
| Title | Acessory Response Event |
| Args / data | NN,EnHigh_EnLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an ‘ON’ response event with three added data bytes. A response event is a reply to a status request (AREQ) without producing an ON or OFF event. |

---

| OpCode | Hex: F5 Decimal 245 |
| :--- | :--- |
| Name | EVLRNI |
| Title | Teach and event in learn mode using event indexing |
| Args / data | NN,EnHigh_EnLow,EnIndex,EvIndex,EvVal |
| Priority | 3 |
| Description | Sent by a configuration tool to a node in learn mode to teach it an event. The event index must be known. Also teaches it the associated event variables.(EVs). This command is repeated for each EV required. VLCB allow zero events and zero EVid, also return GRSP. |

---

| OpCode | Hex: F6 Decimal 246 |
| :--- | :--- |
| Name | ACDAT |
| Title | Accessory node data event |
| Args / data | NN,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 3 |
| Description | Indicates an event from this node with 5 bytes of data. For example, this can be used to send the 40 bits of an RFID tag. There is no event number in order to allow space for 5 bytes of data in the packet, so there can only be one data event per node. |

---

| OpCode | Hex: F7 Decimal 247 |
| :--- | :--- |
| Name | ARDAT |
| Title | Accessory node data response |
| Args / data | NN,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 3 |
| Description | Indicates a node data response. A response event is a reply to a status request (RQDAT) without producing a new data event. |

---

| OpCode | Hex: F8 Decimal 248 |
| :--- | :--- |
| Name | ASON3 |
| Title | Accessory Short ON |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an ON event using the short event number of 2 LS bytes with three added data bytes. |

---

| OpCode | Hex: F9 Decimal 249 |
| :--- | :--- |
| Name | ASOF3 |
| Title | Accessory Short OFF |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an OFF event using the short event number of 2 LS bytes with three added data bytes. |

---

| OpCode | Hex: FA Decimal 250 |
| :--- | :--- |
| Name | DDES |
| Title | Device data event (short mode) |
| Args / data | DNHigh_DNLow,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 3 |
| Description | Function is the same as F6 but uses device addressing so can relate data to a device attached to a node. e.g. one of several RFID readers attached to a single node. |

---

| OpCode | Hex: FB Decimal 251 |
| :--- | :--- |
| Name | DDRS |
| Title | Device data response (short mode) |
| Args / data | DNHigh_DNLow,Byte1,Byte2,Byte3,Byte4,Byte5 |
| Priority | 3 |
| Description | The response to a request for data from a device. (0x5B) |

---

| OpCode | Hex: FC Decimal 252 |
| :--- | :--- |
| Name | DDWS |
| Title | Write data |
| Args / data | DNHigh_DNLow,byte1,byte2,byte3,byte4,byte5 |
| Priority | 0 |
| Description | Used to write data to a device such as an RFID tag. For RC522 byte1 should be 0. |

---

| OpCode | Hex: FD Decimal 253 |
| :--- | :--- |
| Name | ARSON3 |
| Title | Accessory Short Response Event |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an ON response event with with three added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: FE Decimal 254 |
| :--- | :--- |
| Name | ARSOF3 |
| Title | Accessory Short Response Event |
| Args / data | NN,DNHigh_DNLow,Byte1,Byte2,Byte3 |
| Priority | 3 |
| Description | Indicates an OFF response event with with three added data bytes. A response event is a reply to a status request (ASRQ) without producing an ON or OFF event. |

---

| OpCode | Hex: FF Decimal 255 |
| :--- | :--- |
| Name | EXTC6 |
| Title | Extended op-code with 6 data bytes |
| Args / data | ExtOpc,Byte1,Byte2,Byte3,Byte4,Byte5,Byte6 |
| Priority | 3 |
| Description | Used if the basic set of 32 OPCs is not enough. Allows an additional 256 OPCs |

---

