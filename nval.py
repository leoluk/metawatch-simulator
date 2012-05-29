#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from collections import namedtuple
import wx.propgrid as wxpg

### This file is kind of a mess. There is surely a much nicer way to implement this.

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