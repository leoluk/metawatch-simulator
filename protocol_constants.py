#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  See MetaWatchRemoteMessageProtocolV1.0.pdf
#

from collections import defaultdict

NVAL_VALUES = [
    (0x0, 'Reserved', None, None, None),
    (0x1, 'Link key', None, None, None),
    (0x2, 'Idle buffer mode', 1, 0, ['Reserved top', 'Fullscreen']),
    (0x3, 'Idle buffer inverted', 1, 0, bool),
    (0x4, 'Idle timeout', 2, None, None),
    (0x5, 'Application timeout', 2, 600, int),
    (0x6, 'Notification timeout', 2, 30, int),
    (0x7, 'Reserved timeout', 2, None, int),
    
    # .. skipped a few ... (OLED)
    
    (0x1001, 'Sniff debug', 1, 0, bool),
    (0x1002, 'Battery debug', 1, 0, bool), 
    (0x1003, 'Connection debug', 1, None, bool),
    (0x1004, 'Reset pin enabled', 1, 0x02, {0x1: 'Enabled', 0x2: 'Disabled',}),
    (0x1005, 'Master reset', 2, None, None), 
    
    (0x2001, 'Low battery threshold', 2, 3500, int), 
    (0x2002, 'Bluetooth off threshold', 2, 3300, int), 
    (0x2003, 'Battery sense interval', 2, 8, int), 
    (0x2004, 'Light sense interval', 2, None, int), 
    (0x2005, 'Secure simple pairing', 1, 0, bool),
    (0x2006, 'Link alarm', 1, 1, bool),
    (0x2007, 'Link alarm duration', None, None, int),
    (0x2008, 'Paring mode duration', 1, 0, int),
    (0x2009, 'Time Format', 1, 0, ['12hrs', '24hrs']),
    (0x200a, 'Date Format', 1, 0, ['Month first', 'Day first']),
    (0x200b, 'Show seconds', 1, 0, bool),
    
    # ... skipped another few ... (OLED)
    
]

MESSAGE_TYPES_DICT = {
    0x01: 'getDeviceType',
    0x02: 'getDeviceTypeResponse',
    0x03: 'getInfo',
    0x04: 'getInfoResponse',
    0x05: 'loopback',
    
    0x10: 'writeOLED',
    0x12: 'changeOLED',
    0x13: 'writeOLEDScroll',
    
    0x20: 'advanceHands',
    0x23: 'setVibrate',
    0x26: 'setRTC',
    0x27: 'getRTC',
    0x28: 'getRTCResponse',
    
    0x30: 'nval',
    0x31: 'nvalResponse',
    0x33: 'statusEvent',
    0x34: 'buttonEvent',
    0x35: 'gpPhone',
    0x36: 'gpWatch',
    
    0x40: 'writeLCD',
    0x42: 'configLCD',
    0x43: 'updateLCD',
    0x44: 'loadLCDTemplate',
    
    0x46: 'enableButton',
    0x47: 'disableButton',
    
    0x53: 'batteryConfig',
    0x54: 'lowBatteryWarning',
    0x55: 'lowBatteryBluetoothWarning',
    
    0x56: 'readBatteryVoltage',
    0x57: 'readBatteryVoltageResponse',
    0x58: 'readLightSense',
    0x59: 'readLightSenseResponse',
    
    # Undocumented commands
    
    0xC0: 'setLED',
    
}

MESSAGE_TYPES = defaultdict(lambda: 'undocumentedCode')

MESSAGE_TYPES.update(MESSAGE_TYPES_DICT)