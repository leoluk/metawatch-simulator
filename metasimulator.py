#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

import sys, os
import inspect
import logging
import datetime

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

logging.basicConfig(stream=sys.stdout,
                    format="%(levelname)s - %(name)s -> %(message)s",
                    level=logging.INFO)


class MainFrame(gui_metasimulator.MainFrame, serialcore.SerialMixin):
    def __init__(self, parent):
        gui_metasimulator.MainFrame.__init__(self, parent)
        serialcore.SerialMixin.__init__(self)
        
        pg = wxpg.PropertyGridManager(self, style=wxpg.PG_SPLITTER_AUTO_CENTER)
        self.m_pg.ContainingSizer.Replace(self.m_pg, pg)
        self.m_pg.Destroy()
        self.m_pg = pg
              
        self.m_pg.AddPage("Watch state")
        
        self.Layout()
        
        self.parser = protocol_handlers.GUIMetaProtocolParser(self)
        
        self.serial = serial.Serial(self.m_comPort.Value)
        self.serial.close()
        self.serial.timeout = 0.5
        
        class TBStream(object):
            @staticmethod
            def write(bytes):
                # yeah, I could write a custom handler instead...
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
        streamhandler.formatter = logging.Formatter("[%(levelname)s] - %(name)s -> %(message)s")
        
        logging.root.addHandler(streamhandler)
        self.Bind(serialcore.EVT_SERIALRX, self.OnSerialRX)
        logging.info("GUI initialized")
        self.logger = logging.getLogger("main")
        
        self.clock = wx.Timer(self)
        self.clock.Start(1000)
        self.Bind(wx.EVT_TIMER, self.OnClock)        
        
        self.m_resetWatchOnButtonClick(None)
        self.m_openConnectionOnButtonClick()
        
    def _reset_watch(self):
        """Resets or initializes the internal GUI representation
        of the MetaWatch to default values.
        Called on startup during initialization."""
        
        self.m_pg.ClearPage(0)  
        self.m_pg.Append(wxpg.PropertyCategory("NVAL Store"))
        
        self.m_LEDNotice.Hide()
        self.m_vibrateNotice.Hide()
        
        self.parser.watch_reset()
        
        # Filling in the PropertyGrid this way is somewhat, um, ugly.
        # TODO: use function prototypes instead
        
        for value in nval.get_nval_list():
            args, kwargs = ([], {})
            if value.displaytype[0] and value.default:
                dest_type, value_type = value.displaytype
                kwargs = dict(value = value_type(value.default))
            elif isinstance(value.valuetype, list):
                dest_type = wxpg.EnumProperty
                args = (value.valuetype, range(len(value.valuetype)), value.default)
            elif isinstance(value.valuetype, dict):
                dest_type = wxpg.EnumProperty
                args = (value.valuetype.values(), value.valuetype.keys(), value.default)
            else:
                continue
                
            self.m_pg.Append(dest_type(value.name, str("nval_%04X" % value.identifier),
                                       *args, **kwargs))
                
        self.m_pg.Append(wxpg.PropertyCategory("Real Time Clock"))
        self.m_pg.Append(wxpg.DateProperty("Date"))
        self.m_pg.Append(wxpg.StringProperty("Time"))
        
        self.m_pg.SetPropertyAttribute("Date", wxpg.PG_DATE_PICKER_STYLE,
                                         wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
        self.OnClock(0)
        
        self.logger.info("Initialized watch to default state")

    def m_resetWatchOnButtonClick(self, event):
        self.m_watchMode.Selection = 0
        self.m_watchMode.Enabled = False
        self.m_manualModeSet.Value = False
        self.clock_offset = relativedelta(0)
        self._reset_watch()
        
    def m_manualModeSetOnCheckBox(self, event):
        self.m_watchMode.Enabled = event.Checked()
        
    def MainFrameOnClose(self, event):
        if self.serial.isOpen(): 
            self.StopThread()
            self.serial.close()
            
        self.Destroy()
        
    def OnSerialRX(self, event):
        self.logger.debug("Received data: %s", ' '.join(["%02X" % ord(byte) for byte in event.data]))
        
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
                    self.serial.close()
                    self.serial.open()
                except serial.SerialException, e:
                    self.logger.error("Serial port configuration failed: %s", e.message)
                else:
                    self.m_openConnectionOnButtonClick()
                    ok = True
            elif result == wx.ID_CANCEL:
                ok = True
                
        self.m_comPort.Value = self.serial.port
        
    def OnClock(self, event=None):
        clock = datetime.datetime.now() + self.clock_offset
        self.m_pg.GetProperty('Date').SetValue(clock)
        self.m_pg.GetProperty('Time').SetValue(clock.strftime("%H:%M:%S"))
        pass
        

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