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

"""This module provides helper function which interfaces between the 'raw'
NVAL list in protocol_constants and the GUI routine which populates the
PropertyGrid. """

from collections import namedtuple
import wx.propgrid as wxpg

# The current implementation somewhat messy, but works flawlessly.
# There is surely a much nicer way to implement this.

from protocol_constants import NVAL_VALUES

PROPGRID_MAPPING = {
    bool: (wxpg.BoolProperty, bool), 
    int: (wxpg.IntProperty, long), 
}

NVALClass = namedtuple('NVAL', ['identifier', 'name', 'size', 'default', 'valuetype', 'displaytype',])


def get_nval_list():
    for nval in NVAL_VALUES:
        assert len(nval) == 5
        
        if type(nval[-1]) != type:
            dty = type(nval[-1])
        else:
            dty = nval[-1]
            
        yield NVALClass(*nval, displaytype=PROPGRID_MAPPING.get(dty, (None, None)))
        
        
if __name__ == '__main__':
    print get_nval_list().next().name