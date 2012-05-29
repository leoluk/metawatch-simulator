#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Code from pyMetaWatch
#

class CRC_CCITT:
    """Performs CRC_CCITT"""

    def __init__(self, inverted=True):
        self.inverted=inverted;
        self.tab=256*[[]]
        for i in xrange(256):
            crc=0
            c = i << 8
            for j in xrange(8):
                if (crc ^ c) & 0x8000:
                    crc = ( crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
                c = c << 1
                crc = crc & 0xffff
            self.tab[i]=crc;

    def update_crc(self, crc, c):
        c=0x00ff & (c % 256)
        if self.inverted: c=self.flip(c);
        tmp = ((crc >> 8) ^ c) & 0xffff
        crc = (((crc << 8) ^ self.tab[tmp])) & 0xffff
        return crc;

    def checksum(self,str):
        """Returns the checksum of a string.""";
        #crcval=0;
        crcval=0xFFFF;
        for c in str:
            crcval=self.update_crc(crcval, ord(c));
        return crcval;

    def flip(self,c):
        """Flips the bit order, because that's what Fossil wants."""
        l=[0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15];
        return ((l[c&0x0F]) << 4) + l[(c & 0xF0) >> 4];

    def test(self):
        return True;