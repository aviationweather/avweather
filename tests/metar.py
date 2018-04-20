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
import unittest
from ddt import ddt
from ddt import data

from avweather import metar

@ddt
class MetarTests(unittest.TestCase):

    @data(
        '',
        'METAR A000',
        'SPECI A000',
        'METAR value'
    )
    def test_parsetype(self, string):
        test, tail = metar._parsetype(string)

        if test is not None:
            self.assertIn(test, ('METAR', 'SPECI'))
        else:
            self.assertEqual(string.strip().upper(), tail)

    @data(
        '',
    )
    @unittest.expectedFailure
    def test_parselocation(self, string):
        test, tail = metar._parselocation(string)

        if test is not None:
            self.assertIsInstance(test, str)
            self.assertEqual(len(test), 4)
            self.assertTrue(test[0].isalpha())
            for char in test[1:]:
                self.assertTrue(char.isalpha() or char.isnumber())
            self.assertEqual(test, test.upper())
        else:
            self.assertEqual(string.strip(), tail)
