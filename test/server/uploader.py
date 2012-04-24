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


import sys
import os.path
import unittest
sys.path.insert(0, '../..')
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.util import b
from app.server import get_app as _app, MainHandler, ProgressHandler,\
                            SaveHandler, UPLOADS_KEYS

class HTTPClientApplicationsRoutes(AsyncHTTPTestCase, LogTrapTestCase):
    def get_http_client(self):
        return AsyncHTTPClient(io_loop=self.io_loop)

    def setUp(self):
        super(HTTPClientApplicationsRoutes, self).setUp()
        self.http_client = self.get_http_client()

    def get_app(self):
        return _app()

    def setUp(self):
        super(HTTPClientApplicationsRoutes, self).setUp()
        self.http_client = self.get_http_client()

    def test_home(self):
        response = self.fetch("/")
        self.assertEqual(response.code, 200)

    def test_post_message(self):
        UPLOADS_KEYS['123'] = dict()
        response = self.fetch("/save", method="POST",
                              body="uploadKey=123&description=Message")
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b("{success:true}"))
        self.assertEqual(UPLOADS_KEYS['123']['description'], "Message")

    def test_progress_route(self):
        UPLOADS_KEYS["123"] = {
            "bytes_loaded": 10,
            "bytes_total": 100
        }
        response = self.fetch("/progress?uploadKey=123", method="GET")
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, str(UPLOADS_KEYS["123"]))

        
class TestHTTPClientApplicationsRoutesSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self,map(HTTPClientApplicationsRoutes,
                                              ("test_home",
                                               "test_post_message",
                                               "test_progress_route")))


def run():
    print "Test for uploader app:\n"
    unittest.main()

if __name__ == "__main__":
    run()