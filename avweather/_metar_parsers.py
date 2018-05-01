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
from collections import namedtuple
from avweather._parsers import search, occurs

@search(r"""
    (?P<type>METAR|SPECI|METAR\sCOR|SPECI\sCOR)
""")
def ptype(metartype):
    """Returns a string with the METAR type or None"""
    return metartype['type']

@search(r"""
    (?P<location>[A-Z][A-Z0-9]{3})
""")
def plocation(location):
    """Retuns a string with the METAR location ICAO code or None"""
    return location['location']

@search(r"""
    (?P<time>[0-9]{6})Z
""")
def ptime(time):
    """Returns a tuple with (day, hour, minute) with the METAR observation
    time or (None, None, None) if time pattern not found
    """
    tmetar_obs_time = namedtuple('MetarObsTime', 'day hour minute')
    time = time['time']
    day = int(time[:2])
    hour = int(time[2:4])
    minute = int(time[4:])

    return tmetar_obs_time(day, hour, minute)

@search(r"""
    (?P<reporttype>AUTO|NIL)?
""")
def preporttype(reporttype):
    """Retuns a string with the METAR report type or None"""
    return reporttype['reporttype']

@search(r"""
    (?P<direction>[0-9]{2}0|VRB|///)
    P?(?P<speed>[0-9]{2,3}|//)
    (GP?(?P<gust>[0-9]{2,3}))?
    (?P<unit>KT|KMH)
    (\s(
        (?P<variable_from>[0-9]{2}0)
        V(?P<variable_to>[0-9]{2}0)
    ))?
""")
def pwind(wind):
    """Returns a (direction, speed, gust, unit, variable_from, variable_to) of
    (int, int, int, string, int, int) or (None*6) for any matching wind report
    information.
    """
    twind = namedtuple('Wind', 'direction speed gust unit variable_from variable_to')
    direction = wind['direction']
    if direction.isnumeric():
        direction = int(direction)
    speed = wind['speed']
    if speed.isnumeric():
        speed = int(speed)
    gust = wind['gust']
    if gust and gust.isnumeric():
        gust = int(gust)
    unit = wind['unit']
    variable_from = wind['variable_from']
    if variable_from and variable_from.isnumeric():
        variable_from = int(variable_from)
    variable_to = wind['variable_to']
    if variable_to and variable_to.isnumeric():
        variable_to = int(variable_to)
    return twind(
        direction,
        speed,
        gust,
        unit,
        variable_from,
        variable_to,
    )

@search(r"""
    (?P<distance>[\d]{4})
    (?P<ndv>NDV)?
    (\s
        (?P<min_distance>[\d]{4})\s
        (?P<min_direction>N|NE|E|SE|S|SW|W|NW)
    )?
""")
def pvis(item):
    """Returns (distance, ndv, min_distance, min_direction) of
    (int, bool, int, int) or (None*4) for the visibility information in the
    METAR report.
    """
    tvisibility = namedtuple('Visibility', 'distance ndv min_distance min_direction')

    ndv = item['ndv'] is not None
    min_distance = item['min_distance']
    if min_distance is not None:
        min_distance = int(min_distance)
    return tvisibility(
        int(item['distance']),
        ndv,
        min_distance,
        item['min_direction'],
    )

@occurs(10)
@search(r"""
    (
        R(?P<rwy>[\d]{2}(L|C|R)?)
        /(?P<rvrmod>P|M)?(?P<rvr>[\d]{4})
        (V(?P<varmod>P|M)?(?P<var>[\d]{4}))?
        (?P<tend>U|D|N)?
    )?
""")
def prvr(rvr):
    """Returns ((distance, modifier, variation, variation_modifier, tendency),)
    of ((int, string, int, string, string),) or () for runway visual range
    information in the METAR report.
    """
    trvr = namedtuple('Rvr', 'distance modifier variation variation_modifier tendency')
    if None in (rvr['rwy'], rvr['rvr']):
        return None
    return rvr['rwy'], trvr(
        int(rvr['rvr']),
        rvr['rvrmod'],
        int(rvr['var']) if rvr['var'] is not None else None,
        rvr['varmod'],
        rvr['tend'],
    )

@search(r'(?P<intensity>\+|-)?')
def pintensity(item):
    """Returns a string matching a '-' or '='"""
    return item['intensity']

def ppercipitation(string):
    """Returns (intensity, (phenomena,)) of (string, (string,)) where phenomena is a
    string for each percipitation reported in the METAR report.
    """
    tpercipitation = namedtuple('Percipitation', 'intensity phenomena')

    @occurs(10)
    @search(r"""(?P<phenomena>
        DZ|RA|SN|SG|PL|DS|SS|FZDZ|FZRA|FZUP|SHGR|SHGS|SGRA|SHSN|TSGR|TSGS|TSPL|
        TSRA|TSSN|UP
    )""")
    def pphenomena(item):
        """Returns the phenomena tuple"""
        return item['phenomena']

    intensity, tail = pintensity(string)
    if intensity is None:
        intensity = ''
    phenomena, tail = pphenomena(tail)

    if not phenomena:
        return None, tail
    return tpercipitation(intensity, phenomena), tail

@occurs(10)
@search(r"""
    (?P<obscuration>
        IC|FG|BR|SA|DU|HZ|FU|VA|SQ|PO|FC|TS|BCFG|BLDU|BLSA|BLSN|DRDU|DRSA|
        DRSN|FZFG|MIFG|PRFG
    )?
""")
def pobscuration(obscuration):
    """Returns (obscuration,) of (string,) for all obscuration phenomena
    report in the METAR report.
    """
    return obscuration['obscuration']

def potherphenomena(string):
    """Returns (intensity, (phenomena,)) of (string, (string,)) where
    phenomena is a string for every other phenomena that is not percipitation
    or obscuration reported in the METAR report.
    """
    tother_phenomena = namedtuple('OtherPhenomena', 'intensity phenomena')

    @occurs(10)
    @search(r"""(?P<phenomena>
        FG|PO|FC|DS|SS|TS|SH|BLSN|BLSA|BLDU|VA
    )""")
    def pphenomena(item):
        """Returns the phenomena tuple"""
        return item['phenomena']

    intensity, tail = pintensity(string)
    phenomena, tail = pphenomena(tail)

    if not phenomena:
        return None, tail

    return tother_phenomena(intensity, phenomena), tail

def pcloudsverticalvis(string):
    """Returns tuple for clouds if reported, or int for vertical visibility if
    reported instead, or 'skyclear' if any of skyclear indications is found.
    """
    @occurs(4)
    @search(r"""
        (?P<amount>FEW|SCT|BKN|OVC)
        (?P<height>[\d]{3}|///)
        (?P<type>CB|TCU|///)?
    """)
    def pclouds(item):
        """Returns ((amount, height, type),) of ((string, int, string),) for
        clouds or ()"""
        tcloud = namedtuple('Cloud', 'amount height type')
        height = item['height']
        if height == '///':
            height = -1
        else:
            height = int(height)
        return tcloud(item['amount'], height, item['type'])
    clouds, tail = pclouds(string)
    if clouds:
        return clouds, tail

    @search(r"""
        VV(?P<verticalvis>[\d]{3}|///)
    """)
    def pverticalvis(item):
        """Returns int for the vertical visibility, -1 for unavailable or None
        """
        verticalvis = item['verticalvis']
        if verticalvis == '///':
            return -1
        return int(verticalvis)
    verticalvis, tail = pverticalvis(string)
    if verticalvis is not None:
        return verticalvis, tail

    @search(r'(?P<skyclear>SKC|NSC|NCD)')
    def pskyclear(item):
        """Returns 'skyclear' or None"""
        return item['skyclear']
    skyclear, tail = pskyclear(string)
    return skyclear, tail

def psky(string):
    """Returns (visibility rvr weather clouds) for all the function returns
    above.
    """
    tsky_conditions = namedtuple('SkyConditions', 'visibility rvr weather clouds')

    @search(r'(?P<cavok>CAVOK)?')
    def pcavok(item):
        """Returns CAVOK or None"""
        return item['cavok']

    cavok, string = pcavok(string)

    if cavok is not None:
        return None, string

    visibility, string = pvis(string)
    rvr, string = prvr(string)

    tweather = namedtuple('Weather', 'precipitation obscuration other')
    precipitation, string = ppercipitation(string)
    obscuration, string = pobscuration(string)
    other, string = potherphenomena(string)
    current_weather = tweather(precipitation, obscuration, other)

    clouds, string = pcloudsverticalvis(string)

    return tsky_conditions(visibility, rvr, current_weather, clouds), string

@search(r"""
    (?P<air_signal>M)?
    (?P<air>[\d]{2})/
    (?P<dewpoint_signal>M)?
    (?P<dewpoint>[\d]{2})
""")
def ptemperature(item):
    """Returns (air, dewpoint) as (int, int) for air and dewpoint temperatures
    """
    ttemperature = namedtuple('Temperature', 'air dewpoint')

    air = int(item['air'])
    if item['air_signal'] is not None:
        air = 0 - air
    dewpoint = int(item['dewpoint'])
    if item['dewpoint_signal'] is not None:
        dewpoint = 0 - dewpoint

    return ttemperature(air, dewpoint)

@search(r'Q(?P<pressure>[\d]{4})')
def ppressure(item):
    """Returns pressure as int in hectopascals"""
    return int(item['pressure'])
