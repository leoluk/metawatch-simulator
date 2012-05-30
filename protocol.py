#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   This file is part of MetaWatch Simulator.
#
#   This software is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by the
#   Free Software Foundation, either version 3 of the License, or (at your
#   option) any later version.
#

"""
This module contains all the byte-level protocol parsing.
It is completely independant from the GUI and can be re-used.

The protocol parser is subclassed in procotol_handlers,
which is where all the GUI updates happen.
"""

import sys, os
import struct
import datetime

import crc
import bitarray

from protocol_constants import MESSAGE_TYPES

class ProtocolError(Exception): pass
class InvalidMessage(ProtocolError): pass
class InvalidChecksum(ProtocolError): pass

class BaseProtocolParser(object):
    def __init__(self):
        """This class parses incoming watch messages, checks their integrity
        and dissects them. All the message types are defined in the module
        protocol_constants. Every message type has its own handler
        function."""
        
        self.crc_engine = crc.CRC_CCITT()
        
    def _not_implemented(self, msgtype, *args, **kwargs):
        """Dummy handler which raises an exception every time an unknown
        message type is encountered."""
        
        raise NotImplementedError("Message type %s not implemented"
                                  % MESSAGE_TYPES[msgtype])
        
    def parse(self, message):
        """Parses one or more watch messages, checks their integrity, splits\
        them and forwards them to a handler function. The mapping between\
        message types and handler functions is done using the translation\
        table in the protocol constant definitions. The message type 0x26 has\
        the name 'setRTC', so the handler function must be named\
        'handler_setRTC'."""
        
        message = bytearray(message)
        
        if message[0] != 1:
            raise ProtocolError("Doesn't start with 0x01")
        
        # If the packet is longer than declared, it will be truncated.
        # Everything above the limit will be copied into a new message in
        # order to parse it as well. Usually, this shouldn't happen: the
        # phone is supposed to pause between different packets.
        
        if len(message) > message[1]:
            if message[message[1]] == 1:
                self.parse(message[message[1]:])
                message = message[:message[1]]
                
        # If the packet is shorter than declared, it is obviously damaged.
        
        if len(message) != message[1]:
            raise ProtocolError("Length mismatch")
        
        # Different parts of the message:
        
        msgtype = message[2]
        option_bits = bitarray.bitarray(endian='little')
        option_bits.fromstring(chr(message[3]))
        payload = message[4:-2]
        checksum = message[-2:]
        
        # Verify the checksum:
        
        crc_ = self.crc_engine.checksum(str(message[0:-2]))
        checksum_ = bytearray(struct.pack('<H', crc_))
        
        if checksum != checksum_:
            raise ProtocolError("Invalid checksum")
        
        # Pass to handler function using some black magic:
        
        getattr(self, 'handle_%s' % MESSAGE_TYPES[msgtype],
                self._not_implemented)(
            msgtype, option_bits, payload
        )
        
        
class MetaProtocolParser(BaseProtocolParser):
    """The actual message processing happens in this subclass. On the
    MetaProtocol layer (this class!), every handler should return the plain
    information fetched from the payload. The GUIMetaProtocolParser will
    override these functions.
    
    Packer parsing should be pretty obvious, so no further documentation on this.
    Note that most values are either unsigned chars or big-endian unsigned shorts.
    
    Data should be passed using bytearray's, not binary strings.
    
    """
    
    def handle_setRTC(self, msgtype, option_bits, payload):
        year = unpack(payload[:2], mode='>h')
        
        month = payload[4]
        day = payload[3]
        week_day = payload[5]
        
        hour = payload[5]
        minute = payload[6]
        second = payload[7]
        
        # There seems to be an undocumented protocol extension which permits
        # to set these NVAL properties without issuing an NVAL message. Has
        # to be verified on an actual watch. The MWM doesn't use this, but
        # the time set application for PC does.
        
        if len(payload) > 8:
            hrs12 = bool(payload[8])     # undocumented? - 12/24 hrs
            dayFirst = bool(payload[9])  # undocumented? - DD-MM / MM-DD
        else:
            hrs12 = NotImplemented
            dayFirst = NotImplemented
        
        return datetime.datetime(
            year=year, day=day, month=month,
            hour=hour, minute=minute, second=second, 
        ), hrs12, dayFirst
    
    def handle_setLED(self, msgtype, option_bits, payload):
        return option_bits[0]
        
    def handle_setVibrate(self, msgtype, option_bits, payload):
        action = payload[0]
        on_time = unpack(payload[1:3])
        off_time = unpack(payload[3:5])
        cycles = payload[5]
        
        return action, on_time, off_time, cycles
    
    def handle_disableButton(self, msgtype, option_bits, payload):
        mode, index, press_type = payload
        return mode, index, press_type
    
    def handle_writeLCD(self, msgtype, option_bits, payload):
        mode = ord(option_bits[0:3].tobytes())
        two_lines = (not option_bits[4]) and (len(payload) > 13)
        
        # At the moment, there are some hard-coded checks
        # for two_lines. This introduces some redundant code.
        
        line1 = bitarray.bitarray(endian='little')
        line2 = bitarray.bitarray(endian='little')
        
        line1.frombytes(str(payload[1:13]))
        
        if two_lines:
            line2.frombytes(str(payload[14:26]))
            
        if two_lines:
            index = payload[0], payload[13]
        else:
            index = (payload[0], )
        
        return mode, two_lines, line1, line2, index
    
    def handle_updateLCD(self, msgtype, option_bits, payload):
        # TODO: implement undocumented 'activate' flag
        return ord(option_bits[0:3].tobytes())
        
def unpack(bytestr, mode='<h'):
    """Unpacks the binary representation of an unsigned short."""
    return struct.unpack(mode, str(bytestr))[0]
        
def tc2ba(text_chain):
    """Debug helper: Turns a hex character list into a bytearray."""
    return bytearray(int(x, 16) for x in text_chain.split())
        
def main():
    parser = MetaProtocolParser()
    
    debug_chain = "01 10 26 00 03 F2 0C 05 02 04 2E 3C 01 01 FE 49"
    print parser.parse(tc2ba(debug_chain))


if __name__ == '__main__':
    main()