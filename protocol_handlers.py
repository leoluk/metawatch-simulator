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

"""This file contains the GUI protocol parser, which is """

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
    """This class has direct access to the main GUI and subclasses the
    protocol parser. This is the 'glue code' between the protocol layer and
    the GUI representation - this class takes the parsed values and updates
    the GUI accordingly."""
    
    def __init__(self, window):
        MetaProtocolParser.__init__(self)
        self.window = window
        self.logger = logging.getLogger('parser')
        
        self.vibrate = threading.Event()
        
        if 0:
            # Wing IDE type hints
            import metasimulator
            isinstance(self.window, metasimulator.MainFrame)
            
    def watch_reset(self):
        """Called when internal watch state is reset
        and on initialization.
        
        Anything that represents a certain state
        should be reset here (registers etc.)."""
        
        self.vibrate.clear()
        self.button_mapping = {}
    
    def handle_setRTC(self, *args, **kwargs):
        date, hrs12, dayFirst = \
            MetaProtocolParser.handle_setRTC(self, *args, **kwargs)
        
        self.window.clock_offset = relativedelta(date, datetime.now())
        
        if hrs12 != NotImplemented:
            # Inofficial protocol extension, see protocol parser
            self.window.m_pg.SetPropertyValue('nval_2009', int(not hrs12))
            self.window.m_pg.SetPropertyValue('nval_200A', int(dayFirst))
        
        self.logger.info("RTC time set (offset %d secs)",
                         self.window.clock_offset.seconds)
        
        # Update live clock
        self.window.OnClock()
        
    def handle_setLED(self, *args, **kwargs):
        state = MetaProtocolParser.handle_setLED(self, *args, **kwargs)
        
        if state:
            self.window.m_LEDNotice.Show()
        else:
            self.window.m_LEDNotice.Hide()
            
        self.logger.info("Changed LED state to %d", state)
        
    def _vibrateTimer(self, cycles_left, on_time, off_time, state):
        """Recursive timer. The vibration, which usually consists of multiple
        cycles, is handled using GUI events, i.e. timers.
        
        The timer sets itself until there are no more cycles left. It can
        be interrupted by clearing the vibrate flag."""
        
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
            self.logger.info("Vibrate %d times for %d/%d msecs" %
                             (cycles, on_time, off_time))
            
            self._vibrateTimer(cycles+2, on_time, off_time, 1)
        else:
            self.window.m_vibrateNotice.Hide()
            self.vibrate.clear()
        
        
        
    