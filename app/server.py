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
This module's goal is to provide a uploader system with progress
for soundcloud.
This file run() does this job by starting the http server (Tornado).
"""
import uuid
import tempfile
import logging
from tornado_stream import *
import tornado.ioloop
import tornado.web
import tornado.httpserver
from ConfigParser import ConfigParser


UPLOADS_KEYS = dict()
STATIC_DIR = "./static/"
TEMPLATE_DIR = "./templates/"
UPLOAD_FILES_DIR = "../data/"

@streamUpload
class UploadHandler(StreamRequestHandler):
    def post(self):
        headers = self.request.headers
        self.uuid = self.get_argument('uploadKey')
        fileName = UPLOAD_FILES_DIR + self.uuid
        self.temp_file = open(fileName, 'w')
        self.bytes_loaded = 0
        self.request.request_continue()
        self.bytes_total = self.request.content_length
        self._read()

    def _read(self):
        diff_length = self.request.content_length - self.bytes_loaded
        chunk_size = min(10000, diff_length)
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
        json_struc = {"bytes_loaded": self.bytes_loaded,
                      "bytes_total": self.bytes_total}
        UPLOADS_KEYS[self.uuid] = json_struc
        self._read()

    def _upload_complete(self):
        del UPLOADS_KEYS[self.uuid]
        self.write(self.uuid)
        self.finish()


class SaveHandler(tornado.web.RequestHandler):
    def post(self):
        uuid = self.get_argument('uploadKey')
        path = uuid
        description = self.get_argument('description')
        self.write(path + "\n" + description)
        self.render(TEMPLATE_DIR + "finish.html")


class ProgressHandler(tornado.web.RequestHandler):
    def get(self):
        if(UPLOADS_KEYS.has_key(self.get_argument('uploadKey'))):
            file_struc = UPLOADS_KEYS.get(self.get_argument('uploadKey'))
            self.write(str(file_struc))
        self.set_header("Content-Type", "application/json")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(TEMPLATE_DIR + "index.html")


def run():
    config = ConfigParser()
    config.read("../uploader.conf")
    TEMPLATE_DIR = config.get('http', 'template_dir')
    UPLOAD_FILES_DIR = config.get('http', 'upload_files_dir')
    STATIC_DIR = config.get('http', 'static_dir')
    application = tornado.web.Application([
        (r"/static/(.*)",   tornado.web.StaticFileHandler, \
                            {"path": STATIC_DIR}),
        (r"/uploader",      UploadHandler),
        (r"/progress",      ProgressHandler),
        (r"/save",          SaveHandler),
        (r"/",              MainHandler)
    ])
    http_server = StreamHTTPServer(application)
    http_server.listen(config.get('http', 'port'),config.get('http', 'host'))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run()
