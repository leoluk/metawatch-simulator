#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

import sys, os
import struct
import datetime

import crc

from protocol_constants import MESSAGE_TYPES

class ProtocolError(Exception): pass
class InvalidMessage(ProtocolError): pass
class InvalidChecksum(ProtocolError): pass

class BaseProtocolParser(object):
    def __init__(self):
        self.crc_engine = crc.CRC_CCITT()
        
    def _not_implemented(self, msgtype, *args, **kwargs):
        raise NotImplementedError("Message type %s not implemented"
                                  % MESSAGE_TYPES[msgtype])
        
    def parse(self, message):
        message = bytearray(message)
        
        if message[0] != 1:
            raise ProtocolError("Doesn't start with 0x01")
        
        if len(message) > message[1]:
            if message[message[1]] == 1:
                self.parse(message[message[1]:])
                message = message[:message[1]]
        
        if len(message) != message[1]:
            raise ProtocolError("Length mismatch")
        
        msgtype = message[2]
        option_bits = message[3]
        payload = message[4:-2]
        checksum = message[-2:]
        
        crc_ = self.crc_engine.checksum(str(message[0:-2]))
        checksum_ = bytearray(struct.pack('<H', crc_))
        
        if checksum != checksum_:
            raise ProtocolError("Invalid checksum")
        
        getattr(self, 'handle_%s' % MESSAGE_TYPES[msgtype],
                self._not_implemented)(
            msgtype, option_bits, payload
        )
        
        
class MetaProtocolParser(BaseProtocolParser):
    def handle_setRTC(self, msgtype, option_bits, payload):
        year = struct.unpack('>h', str(payload[:2]))[0]
        
        month = payload[3]
        day = payload[4]
        week_day = payload[5]
        
        hour = payload[5]
        minute = payload[6]
        second = payload[7]
        
        if len(payload) > 8:
            hrs12 = bool(payload[8])     # undocumented - 12/24 hrs
            dayFirst = bool(payload[9])  # undocumented - DD-MM / MM-DD
        
        return datetime.datetime(
            year=year, day=day, month=month,
            hour=hour, minute=minute, second=second, 
        ), hrs12, dayFirst
        
        
        
        
def tc2ba(text_chain):
    return bytearray(int(x, 16) for x in text_chain.split())
        
def main():
    parser = MetaProtocolParser()
    
    debug_chain = "01 10 26 00 03 F2 0C 05 02 04 2E 3C 01 01 FE 49"
    print parser.parse(tc2ba(debug_chain))


if __name__ == '__main__':
    main()