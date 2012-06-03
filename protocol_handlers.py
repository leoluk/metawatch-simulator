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
import numpy

import protocol_constants as const
import protocol

from protocol import MetaProtocolParser, MetaProtocolFactory


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
        self.active_timeout = None
        
        if 0:
            # Wing IDE type hints
            import metasimulator
            isinstance(self.window, metasimulator.MainFrame)
            
    @property
    def active_buffer(self):
        return self.window.m_watchMode.Selection
    
    @active_buffer.setter
    def active_buffer(self, value):
        self.window.m_watchMode.Selection = value
        self.refresh_bitmap(value)
        self.update_button_colors()
        
    @property
    def display_buffer(self):
        return self.display_buffers[self.active_buffer]
    
    @display_buffer.setter
    def display_buffer(self, value):
        self.display_buffers[self.active_buffer] = value
            
    def watch_reset(self):
        """Called when internal watch state is reset
        and on initialization.
        
        Anything that represents a certain state
        should be reset here (registers etc.)."""
        
        self.vibrate.clear()
        self.button_mapping = {}
        
        self.display_buffers = [
            numpy.zeros( (96, 96, 3),'uint8'),  # Idle
            numpy.zeros( (96, 96, 3),'uint8'),  # Application
            numpy.zeros( (96, 96, 3),'uint8'),   # Notification
        ]
        
        self.active_buffer = 0
        
        for buffer in self.display_buffers:
            buffer[:,:,] = 255
            
        #template = wx.Image("template.bmp").GetData()
        #self.display_buffer = numpy.fromstring(template,
                            #dtype='uint8').reshape((96, 96, 3))
            
        if self.active_timeout:
            self.active_timeout.Stop()
        
        self.refresh_bitmap()
        
    def refresh_bitmap(self, buffer_id=None):
        if not buffer_id:
            buffer_id = self.active_buffer
            
        image = wx.EmptyImage(96, 96)
        image.SetData(self.display_buffer.tostring())
        
        self.bitmap = wx.BitmapFromImage(image)
        
        if buffer_id == self.active_buffer:
            self.window.m_display.Refresh()
        
    def draw_bitmap(self, dc):
        dc.Clear()
        dc.DrawBitmap(self.bitmap, 0, 0, True)
        
    def handle_setRTC(self, *args, **kwargs):
        date, hrs12, dayFirst = \
            MetaProtocolParser.handle_setRTC(self, *args, **kwargs)
        
        self.window.clock_offset = relativedelta(date, datetime.now())
        
        if hrs12 != NotImplemented:
            # Inofficial protocol extension, see protocol parser
            self.window.nval_store['nval_2009'] = int(not hrs12)
            self.window.nval_store['nval_200A'] = int(dayFirst)
        
        self.logger.info("RTC time set (offset %d secs)",
                         self.window.clock_offset.seconds)
        
        # Update live clock
        self.window.OnClock()
        
    def handle_setLED(self, *args, **kwargs):
        state = MetaProtocolParser.handle_setLED(self, *args, **kwargs)
        
        if state:
            self.window.m_LEDNotice.Show()
            # Hardcoded, what does a real watch do?
            wx.CallLater(const.LED_TIMEOUT, self.window.m_LEDNotice.Hide)
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
            
    def _button_press(self, btn, msecs):
        if msecs == 0:
            ptype = const.BUTTON_TYPE_IMMEDIATE
        elif msecs > const.BUTTON_LONG_HOLD_TIME:
            ptype = const.BUTTON_TYPE_LONG_HOLD
        elif msecs > const.BUTTON_HOLD_TIME:
            ptype = const.BUTTON_TYPE_HOLD
        else:
            # No hold-press, IMMEDIATE triggered anyway
            ptype = 0
            
        self._send_button_response(btn, ptype)
            
    def _send_button_response(self, btn, ptype):
        btn_hash = (self.active_buffer,
                    const.BUTTON_ALPHA.index(btn), ptype)
        
        if not btn_hash in self.button_mapping:
            # Button not registered
            return
        
        cb, cb_data = self.button_mapping[btn_hash]
        
        assert cb == 0x34
        
        self.window.factory.send_buttonEvent(
            btn_alpha=btn,
            option_bits=cb_data, 
        )
            
    def _button_hash_repr(self, req_hash):
        """Helper function which returns a human-readable
        representation of a (mode, btn_id, btn_type) message."""
        
        mode = const.TEXT_DISPLAY_MODE[req_hash[0]]
        btn_id = const.BUTTON_ALPHA[req_hash[1]]
        btn_type = const.TEXT_BUTTON_TYPE[req_hash[2]]
        
        return ("button {btn_id} for "
                "{mode} mode ({btn_type})".format(**locals()))
            
    def handle_enableButton(self, *args, **kwargs):
        mode, btn_id, btn_type, cb, cb_data = \
            MetaProtocolParser.handle_enableButton(self, *args, **kwargs)
        
        req_hash = (mode, btn_id, btn_type)
        
        if req_hash in self.button_mapping:
            self.logger.info("Re-registered %s", self._button_hash_repr(req_hash))
        else:
            self.logger.info("Registered %s", self._button_hash_repr(req_hash))
            
        data = self._init_option_bits(True)
        data.fromstring(chr(cb_data))
            
        self.button_mapping[req_hash] = (cb, data)
        self.update_button_colors()
        
    def handle_disableButton(self, *args, **kwargs):
            button_config = MetaProtocolParser.handle_disableButton(self, *args, **kwargs)
            
            if button_config in self.button_mapping:
                self.button_mapping.pop(button_config)
                self.update_button_colors()
                self.logger.info("Button mapping %r removed", [button_config])
            else:
                self.logger.debug("Button mapping %r does not exist", [button_config])
                
    def _button_by_name(self, btn_id):
        """Returns the button object given its protocol ID."""
        
        btn_alpha = const.BUTTON_ALPHA[btn_id]
        control = getattr(self.window, 'm_Side%s' % btn_alpha)        

        return control
                
    def update_button_colors(self):
        # TODO: different colors for different action types
        
        for btn_id in const.BUTTON_REAL_IDS:
            self._button_by_name(btn_id).SetBackgroundColour(None)
        
        for mapping in self.button_mapping:
            if mapping[0] == self.active_buffer:
                self._button_by_name(mapping[1]).SetBackgroundColour('gray')
                
    def _reset_mode(self, last=0):
        self.active_buffer = last
        self.window.logger.info("Buffer timeout, reset to [%d] %s", last, 
                             self.window.m_watchMode.GetItemLabel(last))
        
    def handle_updateLCD(self, *args, **kwargs):
            mode = MetaProtocolParser.handle_updateLCD(self, *args, **kwargs)
            
            self.logger.info("Active buffer set to [%d] %s", mode, 
                             self.window.m_watchMode.GetItemLabel(mode))

            if mode > 0:
                timeout = 'nval_0005' if mode == 1 else 'nval_0006'
                if self.active_timeout:
                    self.active_timeout.Stop()
                self.active_timeout = wx.CallLater(self.window.nval_store[timeout]*1000,
                                                   self._reset_mode, 0)
                
                # TODO: correct buffer reset
                # TODO: interaction between timer and 'Manual mode' checkbox
            
            self.active_buffer = mode
    
    def handle_writeLCD(self, *args, **kwargs):
        mode, two_lines, line1, line2, index = \
            MetaProtocolParser.handle_writeLCD(self, *args, **kwargs)
        
        lines = (line1, line2) if two_lines else (line1, )
        
        # TODO: pass entire row to numpy
        
        for i, line1 in enumerate(lines):
            for n, byte in enumerate(line1.unpack(zero='\xff', one='\x00')):
                self.display_buffers[mode][index[i]][n] = ord(byte)

        # This will refresh the current view 'live' as data arrives,
        # not sure if the real watch does this as well.
        
        if (mode == self.active_buffer) and self.window.m_liveView.Value:
            self.refresh_bitmap(mode)
            
    def handle_getDeviceType(self, *args, **kwargs):
        if self.window.m_blockIdle.Value:
            self.logger.info("Denied device type request")
            return
        
        self.window.factory.send_getDeviceTypeResponse(
            const.DEVICE_TYPE_DIGITAL
        )
        
        self.logger.info("Responded to device type query: DEVICE_TYPE_DIGITAL")
                      
                      
class GUIMetaProtocolFactory(MetaProtocolFactory):
    def __init__(self, window):
        MetaProtocolFactory.__init__(self)
        self.window = window
        self.logger = logging.getLogger('factory')
        
        if 0:
            # Wing IDE type hints
            import metasimulator
            isinstance(self.window, metasimulator.MainFrame)        
        
    def _compose_message(self, option_bits=None, payload=None, msgtype=None):
        message = MetaProtocolFactory._compose_message(self, option_bits,
                                                         payload, msgtype)
        
        self.window.write_queue.put(message)
        self.logger.debug("Sent data: %s", ' '.join(["%02X" %
                                  byte for byte in message]))
        
        