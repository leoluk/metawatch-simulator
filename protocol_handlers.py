#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, os
import logging
import struct
from datetime import datetime
from dateutil.relativedelta import relativedelta

import wx
import wx.propgrid as wxpr

import protocol_constants
import protocol


class GUIMetaProtocolParser(protocol.MetaProtocolParser):
    def __init__(self, window):
        protocol.MetaProtocolParser.__init__(self)
        self.window = window
        self.logger = logging.getLogger('parser')
    
    def handle_setRTC(self, *args, **kwargs):
        date, hrs12, dayFirst = \
            protocol.MetaProtocolParser.handle_setRTC(self, *args, **kwargs)
        
        self.window.clock_offset = relativedelta(date, datetime.now())
        
        self.window.m_pg.SetPropertyValue('nval_2009', int(not hrs12))
        self.window.m_pg.SetPropertyValue('nval_200A', int(dayFirst))
        
        self.logger.info("Time changed")
        self.window.OnClock()
    