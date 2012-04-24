#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# app/__init__.py - Part of superuploader test for soundcloud
#
# Copyright (C) 2012  Maxwell Dayvson <dayvson@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from splinter.browser import Browser


class AcceptanceUploader(unittest.TestCase):
    def setUp(self):
        self.browser = Browser()

    def tearDown(self):
        self.browser.quit()

    def test_max(self):
        self.assertTrue(True)
        
    def test_upload_from_localfile(self):
        self.browser.visit('http://localhost:8888/')
        self.browser.attach_file('datafile', '/Users/dayvson/rio_trip.jpg')
        self.browser.fill('description', 'Uploading file simulate clientside navigation')
        while not self.browser.is_text_present('Uploaded to Here'):
            pass
        button = self.browser.find_by_id('savebutton').first
        button.click()
        self.assertTrue(self.browser.is_text_present('Super Upload Detail Page'))
        self.assertTrue(self.browser.is_text_present('Uploading file simulate clientside navigation'))


class TestAcceptanceUploaderSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self,map(AcceptanceUploader, ("test_upload_from_localfile")))

def run():
    unittest.main()


if __name__ == "__main__":
    run()
