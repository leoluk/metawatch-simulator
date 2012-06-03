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
This is the main GUI file for MetaWatch Simulator.
It contains the core GUI logic and imports most of the other modules.

This module does not any code which is parsing or interpreting.
data from the watch, only 'glue code' and the graphic representation
of the watch state.

All processing happens in these modules:

  - serialcode: sending and receiving data from the watch (seperate thread)
  - protocol: core protocol parsing, decoupled from GUI
  - protocol_handlers: GUI specific protocol parsing

"""

import sys, os
import inspect
import logging
import datetime
import time

import serial
import wx
import wx.lib.colourdb
import wx.propgrid as wxpg
from dateutil.relativedelta import relativedelta

import wxSerialConfigDialog
import gui_metasimulator

import nval
import serialcore
import protocol
import protocol_handlers
import  protocol_constants as const

logging.basicConfig(stream=sys.stdout,
                    format="%(levelname)s - %(name)s -> %(message)s",
                    level=logging.INFO)


class MainFrame(gui_metasimulator.MainFrame, serialcore.SerialMixin):
    def __init__(self, parent):
        gui_metasimulator.MainFrame.__init__(self, parent)
        serialcore.SerialMixin.__init__(self)
        
        # The base GUI code is auto-generated using wxFormBuilder, which is
        # unable to generate code for the PropertyGrid. This means that we
        # have to do it here.
        
        pg = wxpg.PropertyGridManager(self, style=wxpg.PG_SPLITTER_AUTO_CENTER)
        self.m_pg.ContainingSizer.Replace(self.m_pg, pg)
        self.m_pg.Destroy()
        self.m_pg = pg
              
        self.m_pg.AddPage("Watch state")
        
        self.Layout()
        
        # The GUIMetaProtocolParser is strongly coupled to this class and
        # contains all reactions to incoming messages, like changing a
        # PropertyGrid entry or showing an indicator.
        
        self.parser = protocol_handlers.GUIMetaProtocolParser(self)
        self.factory = protocol_handlers.GUIMetaProtocolFactory(self)
        
        # The serial class will be accessed from the serialcore.SerialMixin.
        # The initial port is taken from the GUI code, but can be changed at
        # any time using the Setup dialog.
        
        self.serial = serial.Serial(self.m_comPort.Value)
        self.serial.close()
        self.serial.timeout = 0.5
        
        # Nice colorization for log messages in the main window. There are
        # definitely better ways to do this, like implementing a custom
        # handler, but this works fine as well.
        
        class TBStream(object):
            @staticmethod
            def write(bytes):
                if "[ERROR]" in bytes:
                    color = "red"
                elif "[DEBUG]" in bytes:
                    color = "gray"
                elif "[WARNING]" in bytes:
                    color = "blue"
                else:
                    color = "black"
                    
                self.m_log.SetDefaultStyle(wx.TextAttr(color, "white"))
                    
                self.m_log.AppendText(bytes)
        
        streamhandler = logging.StreamHandler(stream=TBStream)
        streamhandler.formatter = logging.Formatter("[%(levelname)s] - %(name)s "
                                                    "-> %(message)s")
        logging.root.addHandler(streamhandler)
        
        # Shortcut for NVAL access
        
        class NVALAccess(object):
            def __init__(self, pg):
                self.pg = pg
            def __getitem__(self, item):
                return self.pg.GetPropertyValue(item)
            def __setitem__(self, item, value):
                return self.pg.SetPropertyValue(item, value)
            
        self.nval_store = NVALAccess(self.m_pg)        

        # The SerialMixin emits a signal every time it receives a chunk of bytes.
        self.Bind(serialcore.EVT_SERIALRX, self.OnSerialRX)
        
        logging.info("GUI initialized")
        
        self.logger = logging.getLogger("main")
        
        # The real time clock is updated by a regular timer event.
        
        self.clock = wx.Timer(self)
        self.clock.Start(500)
        self.Bind(wx.EVT_TIMER, self.OnClock)
        
        for btn in ['B', 'C', 'D', 'E', 'F']:
            button = getattr(self, 'm_Side'+btn)
            button.Bind(wx.EVT_LEFT_UP, self.OnSideButtonUp )
            button.Bind(wx.EVT_LEFT_DOWN, self.OnSideButtonDown)
            
        self.btn_time = {}
        
        self.m_resetWatchOnButtonClick(None)
        self.m_openConnectionOnButtonClick()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == '--debug':
                self.m_debug.Value = True
                logging.root.setLevel(logging.DEBUG)
        
    def _reset_watch(self):
        """Resets or initializes the internal GUI representation of the
        MetaWatch to default values. Called on startup during
        initialization."""
        
        self.m_LEDNotice.Hide()
        self.m_vibrateNotice.Hide()
        
        self.m_watchMode.Selection = 0
        self.m_watchMode.Enabled = False
        self.m_manualModeSet.Value = False
        self.clock_offset = relativedelta(0)        
        
        self.parser.watch_reset()
        
        # There is no seperate internal data structure for the watch state,
        # the GUI elements *are* the internal representation. This function
        # essentially resets them to a known state.
        
        self.m_pg.ClearPage(0)  
        self.m_pg.Append(wxpg.PropertyCategory("NVAL Store"))        
        
        # All NVAL values are listed in the protocol_constants module. The
        # property grid is built by parsing that list and applying default
        # values (NVAL properties which have no default value are ignored,
        # they are marked 'reserved' in the protocol documentation).
        
        for value in nval.get_nval_list():
            args, kwargs = ([], {})
            if value.displaytype[0] and value.default:
                dest_type, value_type = value.displaytype
                kwargs = dict(value = value_type(value.default))
            elif isinstance(value.valuetype, list):
                dest_type = wxpg.EnumProperty
                args = (value.valuetype,
                        range(len(value.valuetype)), value.default)
            elif isinstance(value.valuetype, dict):
                dest_type = wxpg.EnumProperty
                args = (value.valuetype.values(),
                        value.valuetype.keys(), value.default)
            else:
                continue
                
            self.m_pg.Append(dest_type(value.name, str("nval_%04X" % value.identifier),
                                       *args, **kwargs))
                
        self.m_pg.Append(wxpg.PropertyCategory("Real Time Clock"))
        self.m_pg.Append(wxpg.DateProperty("Date"))
        self.m_pg.Append(wxpg.StringProperty("Time"))
        
        self.m_pg.SetPropertyAttribute("Date", wxpg.PG_DATE_PICKER_STYLE,
                                         wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
        
        # Call the timer function once for immediate clock update.
        self.OnClock()
        
        self.logger.info("Initialized watch to default state")
        
    def OnSideButtonDown(self, event):
        event.Skip()
        btn_id = event.GetEventObject().Label
        self.btn_time[btn_id] = time.time()
        self.parser._button_press(btn_id, 0)
        
    def OnSideButtonUp(self, event):
        event.Skip()
        btn_id = event.GetEventObject().Label
        diff = (time.time() - self.btn_time[btn_id]) * 1000
        self.logger.debug("Button %s press-release, held %f msecs", btn_id, diff)
        self.parser._button_press(btn_id, msecs=diff)

    def m_resetWatchOnButtonClick(self, event):
        self._reset_watch()
        
    def m_manualModeSetOnCheckBox(self, event):
        self.m_watchMode.Enabled = event.Checked()
        
    def MainFrameOnClose(self, event):
        if self.serial.isOpen(): 
            self.StopThread()
            self.serial.close()
            
        self.Destroy()
        
    def OnSerialRX(self, event):
        """This function is called every time a new byte chunk is received
        from the watch, representing one or more messages. This function
        passes them to the parser and handles exceptions, like not
        implemented or invalid packets thrown by the parser."""
        
        self.logger.debug("Received data: %s", ' '.join(["%02X" %
                          ord(byte) for byte in event.data]))
        
        try:
            self.parser.parse(event.data)
        except NotImplementedError, e:
            self.logger.warn("Can't parse: %s", e.message)
        except protocol.ProtocolError, e:
            self.logger.error("Protocol error: %s", e.message)
        except ValueError, e:
            self.logger.error("Invalid data: %s", e.message)
        except:
            self.logger.exception("Unexpected exception:")
            
    
    def m_openConnectionOnButtonClick(self, event=None):
        if self.serial.isOpen():
            self.logger.error("Serial port already opened")
            return
        
        try:
            if not self.serial.isOpen():
                self.serial.open()
            self.StartThread()
        except:
            self.logger.exception("Failed to open connection")
        else:
            self.logger.info("Opened serial connection")
            
    def m_closeConnectionOnButtonClick(self, event=None):
        if not self.serial.isOpen():
            self.logger.error("Serial port not opened, can't close")
            return
        
        try:
            self.StopThread()
            self.serial.close()
        except:
            self.logger.exception("Failed to close connection")
        else:
            self.logger.info("Closed serial connection")
            
    def m_debugOnCheckBox(self, event):
        logging.root.setLevel(logging.DEBUG if event.Checked() else logging.INFO)
        
    def m_serialSetupOnButtonClick(self, event=None):
        """Event handler for the serial setup button. Calls the pySerial
        setup dialog and updates the serial config. The serial connection is
        closed before displaying the dialog and re-opened once it has been
        closed, regardless of the changes made by the user."""
        
        self.m_closeConnectionOnButtonClick()
            
        ok = False
        while not ok:
            dialog_serial_cfg = wxSerialConfigDialog.SerialConfigDialog(None, -1, "",
                            show=wxSerialConfigDialog.SHOW_BAUDRATE|
                                 wxSerialConfigDialog.SHOW_FORMAT|
                                 wxSerialConfigDialog.SHOW_FLOW,
                                 
                            serial=self.serial, 
                        )
            
            result = dialog_serial_cfg.ShowModal()
            dialog_serial_cfg.Destroy()
            
            if result == wx.ID_OK:
                try:
                    self.m_openConnectionOnButtonClick()
                except serial.SerialException, e:
                    self.logger.error("Serial port configuration failed: %s", e.message)
                else:
                    ok = True
                    
            elif result == wx.ID_CANCEL:
                ok = True
                
        self.m_comPort.Value = self.serial.port
        
    def OnClock(self, event=None):
        """Clock event handler. The real-time clock on the property grid is
        kept up to date by a GUI timer which triggers every 0.5 seconds. The
        possibility to change the clock from the phone is implemented by
        storing an offset between the date set by the phone and the local
        time, which is applied every time the PG is updated."""
        
        clock = datetime.datetime.now() + self.clock_offset
        self.nval_store['Date'] = clock
        self.nval_store['Time'] = clock.strftime("%H:%M:%S")
        
    def OnDisplayPaint(self, event):
        dc = wx.PaintDC(event.GetEventObject())    
        self.parser.draw_bitmap(dc)
        
    def m_watchModeOnRadioBox(self, event):
        self.parser.refresh_bitmap()

class MetaSimApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        wx.lib.colourdb.updateColourDB()

        frame_main = MainFrame(None)
        frame_main.SetBackgroundColour(wx.NullColour)
        self.SetTopWindow(frame_main)
        frame_main.Show()

        return 1


def main():
    app = MetaSimApp(0)
    app.MainLoop()


if __name__ == '__main__':
    main()