#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, os

import wx
import serial
import threading
import logging
import Queue

SERIALRX = wx.NewEventType()
# bind to serial data receive events
EVT_SERIALRX = wx.PyEventBinder(SERIALRX, 0)

class SerialRxEvent(wx.PyCommandEvent):
    eventType = SERIALRX
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)
        
class SerialMixin(object):
    def __init__(self):
        self.serial = serial.Serial()
        self.serial.timeout = 0.5
        self.thread = None
        self.alive = threading.Event()
        self.logger = logging.getLogger("serial")
        #self.write_queue = Queue.Queue()
        
    def StartThread(self):
        """Start the receiver thread"""        
        self.thread = threading.Thread(target=self.ComPortThread)
        self.thread.setDaemon(1)
        self.alive.set()
        self.thread.start()
        
    def StopThread(self):
        """Stop the receiver thread, wait util it's finished."""
        if self.thread is not None:
            self.alive.clear()          #clear alive event for thread
            self.thread.join()          #wait until thread has finished
            self.thread = None
            
    def ComPortThread(self):
        """Thread that handles the incomming traffic. Does the basic input
           transformation (newlines) and generates an SerialRxEvent"""
        
        while self.alive.isSet():               #loop while alive event is true
            try:
                text = self.serial.read(1)          #read one, with timout
                if text:                            #check if not timeout
                    n = self.serial.inWaiting()     #look if there is more to read
                    if n:
                        text = text + self.serial.read(n) #get it
    
                    event = SerialRxEvent(self.GetId(), text)
                    self.GetEventHandler().AddPendingEvent(event)
            except:
                self.logger.exception("Failed to read from serial port")
                self.alive.clear()
                self.thread.stop()