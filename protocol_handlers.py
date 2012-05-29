#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, os
import logging
import struct
import threading

from datetime import datetime
from dateutil.relativedelta import relativedelta

import wx
import wx.propgrid as wxpr

import protocol_constants
import protocol

from protocol import MetaProtocolParser


class GUIMetaProtocolParser(MetaProtocolParser):
    def __init__(self, window):
        MetaProtocolParser.__init__(self)
        self.window = window
        self.logger = logging.getLogger('parser')
        
        self.vibrate = threading.Event()
        
        if 0:
            # Wing IDE hints
            import metasimulator
            isinstance(self.window, metasimulator.MainFrame)
    
    def handle_setRTC(self, *args, **kwargs):
        date, hrs12, dayFirst = \
            MetaProtocolParser.handle_setRTC(self, *args, **kwargs)
        
        self.window.clock_offset = relativedelta(date, datetime.now())
        
        if hrs12 != NotImplemented:
            self.window.m_pg.SetPropertyValue('nval_2009', int(not hrs12))
            self.window.m_pg.SetPropertyValue('nval_200A', int(dayFirst))
        
        self.logger.info("Time changed")
        self.window.OnClock()
        
    def handle_setLED(self, *args, **kwargs):
        state = MetaProtocolParser.handle_setLED(self, *args, **kwargs)
        
        if state:
            self.window.m_LEDNotice.Show()
        else:
            self.window.m_LEDNotice.Hide()
            
        self.logger.info("Changed LED state")
        
    def _vibrateTimer(self, cycles_left, on_time, off_time, state):
        if not self.vibrate.is_set():
            return  # cancelled
        
        if state:
            self.window.m_vibrateNotice.Show()
        else:
            self.window.m_vibrateNotice.Hide()
                        
        if cycles_left:
            wx.CallLater(on_time if state else off_time,
                         self._vibrateTimer,
                         cycles_left-1, on_time, off_time, not state)
        else:
            self.vibrate.clear()
        
        
    def handle_setVibrate(self, *args, **kwargs):
        action, on_time, off_time, cycles = \
            MetaProtocolParser.handle_setVibrate(self, *args, **kwargs)
        
        if action:
            self.vibrate.set()
            self._vibrateTimer(cycles+2, on_time, off_time, 1)
        else:
            self.window.m_vibrateNotice.Hide()
            self.vibrate.clear()
        
        
        
    