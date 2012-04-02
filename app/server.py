# -*- Coding: utf-8; Mode: Python -*-
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

"""Entry point file for the superuploader.

This module's goal is to provide a uploader system with progress for soundcloud challenge. 
This file run() does this job by starting the http server (Tornado).
"""
import uuid, tempfile
import logging
from tornado_stream import *
import tornado.ioloop, tornado.web, tornado.httpserver

def get_uuid():
    return str(uuid.uuid1().hex)

class FileCache:
    FILES = dict()
    @classmethod
    def push(cls, uuid, value):
        cls.FILES[uuid] = value
        return True
    @classmethod
    def delete(cls, uuid):
        del cls.FILES[uuid]
        return True
    @classmethod
    def get(cls, uuid):
        if cls.FILES.has_key(uuid):
            return cls.FILES[uuid]
        return None

@streamUpload
class UploadHandler(StreamRequestHandler):
    def post(self):
        headers = self.request.headers
        self.uuid = self.get_argument('uploadKey')
        fileName = self.uuid;
        self.temp_file = open(fileName, 'w')
        self.bytes_loaded = 0
        self.request.request_continue()
        self.bytes_total = self.request.content_length
        self._read()

    def _read(self):
        chunk_size = min(10000, self.request.content_length - self.bytes_loaded)
        if chunk_size > 0:
            self.request.connection.stream.read_bytes(chunk_size, self._increase)
        else:
            self.temp_file.close()
            self._upload_complete()

    def _increase(self, chunk):
        if chunk:
            self.temp_file.write(chunk)
            self.bytes_loaded += len(chunk)
        else:
            self.content_length = self.bytes_loaded
        json_struc = {"bytes_loaded": self.bytes_loaded, "bytes_total":self.bytes_total}
        FileCache.push(self.uuid, json_struc)
        self._read()

    def _upload_complete(self):
        self.write(self.uuid)
        self.finish()
    def get(self):
        self.render("templates/index.html")

class SaveHandler(tornado.web.RequestHandler):
    def post(self):
        uuid = self.get_argument('uploadKey')
        path = uuid
        description = self.get_argument('description')
        self.write(path + "\n" + description)
        self.render("templates/finish.html")
        
class ProgressHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(str(FileCache.get(self.get_argument('uploadKey'))))
        self.set_header("Content-Type", "application/json")
        
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")

def run():
    application = tornado.web.Application([
        (r"/static/(.*)",   tornado.web.StaticFileHandler, {"path": "/Users/dayvson/uploader/app/static/"}),
        (r"/uploader",      UploadHandler),
        (r"/progress",      ProgressHandler),
        (r"/save",          SaveHandler),
        (r"/",              MainHandler)
    ])
    http_server = StreamHTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()

