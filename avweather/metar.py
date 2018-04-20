#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aviation Weather

Copyright (C) 2018  Pedro Rodrigues <prodrigues1990@gmail.com>

This file is part of Aviation Weather.

Aviation Weather is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

Aviation Weather is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Aviation Weather.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

def _recompile(pattern):
    return re.compile(pattern, re.I | re.X)

def _research(pattern, string):
    string = string.strip().upper()
    items = pattern.search(string)

    if items is None:
        return None
    else:
        return items.groupdict(), items.end()

TYPE_RE = _recompile(r"""
    (?P<type>METAR|SPECI)
""")

LOCATION_RE = _recompile(r"""
    (?P<location>[A-Z][A-Z0-9]{3})
""")

def _parsetype(string):
    match = _research(TYPE_RE, string)
    if match is None:
        return None, string

    metartype, tail = match

    if 'type' in metartype:
        return metartype['type'], tail

    return None, tail

def _parselocation(string):
    match = _research(LOCATION_RE, string)
    if match is None:
        return None, string

    location, tail = match

    if 'location' in location:
        return location['location'], tail

    return None, tail
