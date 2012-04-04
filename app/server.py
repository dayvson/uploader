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
import os.path
import uuid
import logging
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.web import asynchronous, StaticFileHandler
from ConfigParser import ConfigParser
from tornado_stream import StreamHTTPServer


UPLOADS_KEYS = dict()


class Configuration:
    STATIC_DIR = "./static/"
    TEMPLATE_DIR = "./templates/"
    UPLOAD_FILES_DIR = "../data/"
    SERVER_PORT = "8888"
    SERVER_HOST = "0.0.0.0"


class UploadHandler(tornado.web.RequestHandler):

    @property
    def content_length(self):
        return int(self.request.headers['Content-Length'])

    @asynchronous
    def post(self):
        uuid = self.get_argument('uploadKey')
        UPLOADS_KEYS[uuid] = {
            "bytes_loaded": len(self.request.connection.readed_data),
            "bytes_total": self.content_length
        }
        bytes_loaded = len(self.request.connection.readed_data)
        if  bytes_loaded == self.content_length:
            name = self.request.files['datafile'][0].filename or ""
            fileName = uuid + name
            UPLOADS_KEYS[uuid]['fileName'] = fileName
            self.write("/download/" + fileName)
            output = open(os.path.join(Configuration.UPLOAD_FILES_DIR,
                            fileName), 'w')
            output.write(self.request.files['datafile'][0].body)
            output.close()
            print "FINISH UPLOAD"
            self.finish()


class SaveHandler(tornado.web.RequestHandler):
    def post(self):
        uuid = self.get_argument('uploadKey', None)
        description = unicode(self.get_argument('description', ""))
        if uuid in UPLOADS_KEYS:
            UPLOADS_KEYS[uuid]['description'] = unicode(description)
            self.write("{success:true}")
        else:
            self.write("{success:false}")

    def get(self):
        uuid = self.get_argument('uploadKey', None)
        data_result = None
        if uuid in UPLOADS_KEYS:
            data_result = UPLOADS_KEYS[uuid]
        self.render(Configuration.TEMPLATE_DIR + "finish.html",
                    item=data_result)


class ProgressHandler(tornado.web.RequestHandler):
    def get(self):
        result = "{}"
        uuid = unicode(self.get_argument('uploadKey'))
        if uuid in UPLOADS_KEYS:
            result = str(UPLOADS_KEYS[uuid])
        self.write(result)
        self.set_header("Content-Type", "application/json")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(Configuration.TEMPLATE_DIR + "index.html")


def load_config():
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "..", "uploader.conf"))
    Configuration.TEMPLATE_DIR = config.get('http', 'template_dir')
    Configuration.UPLOAD_FILES_DIR = config.get('http', 'upload_files_dir')
    Configuration.STATIC_DIR = config.get('http', 'static_dir')
    Configuration.SERVER_PORT = config.get('http', 'port')
    Configuration.SERVER_HOST = config.get('http', 'host')


def run():
    load_config()
    application = tornado.web.Application([
        (r"/static/(.*)",   StaticFileHandler,
                            {"path": Configuration.STATIC_DIR}),
        (r"/uploader",      UploadHandler),
        (r"/progress",      ProgressHandler),
        (r"/save",          SaveHandler),
        (r"/download/(.*)", StaticFileHandler,
                            {"path": Configuration.UPLOAD_FILES_DIR}),
        (r"/",              MainHandler)
    ])
    http_server = StreamHTTPServer(application)
    http_server.listen(Configuration.SERVER_PORT, Configuration.SERVER_HOST)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run()
