# -*- coding: utf-8 -*-
#
# app/tornado_stream.py - Part of superuploader test for soundcloud
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

"""
This module's goal is to provide a uploader system with progress
for soundcloud challenge.
This file run() does this job by starting the http server (Tornado).
"""
import logging
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
from tornado.web import asynchronous
from tornado.escape import utf8, native_str, parse_qs_bytes
from tornado.httpserver import _BadRequestException, HTTPRequest
from tornado.util import b


class StreamHTTPServer(tornado.httpserver.HTTPServer):
    def handle_stream(self, stream, address):
        StreamHTTPConnection(stream, address, self.request_callback, \
                            self.no_keep_alive, self.xheaders)


class StreamHTTPConnection(tornado.httpserver.HTTPConnection):
    def __init__(self, stream, address, request_callback, no_keep_alive=False,
                 xheaders=False):
        super(StreamHTTPConnection, self).__init__(
            stream, address, request_callback, no_keep_alive, xheaders)

        # Just read the comments on `_on_handlers' method and
        # realize why I created such an attribute
        self.readed_data = ''
        self.chunk_size = 4096
        self.content_length = 0

    def _on_headers(self, data):
        try:
            data = native_str(data.decode('latin1'))
            eol = data.find("\r\n")
            start_line = data[:eol]
            try:
                method, uri, version = start_line.split(" ")
            except ValueError:
                raise _BadRequestException("Malformed HTTP request line")
            if not version.startswith("HTTP/"):
                raise _BadRequestException(
                        "Malformed HTTP version in HTTP Request-Line")
            headers = tornado.httputil.HTTPHeaders.parse(data[eol:])
            self._request = HTTPRequest(
                connection=self, method=method, uri=uri, version=version,
                headers=headers, remote_ip=self.address[0])
            content_type = headers.get("Content-Type", "")
            print method,  content_type
            if method in ("POST", "PUT"):
                content_length = int(self._request.headers\
                                        .get("Content-Length") or 0)
                if content_type.startswith(
                    "application/x-www-form-urlencoded"):
                    if content_length:
                        content_length = int(content_length)
                        if content_length > self.stream.max_buffer_size:
                            raise _BadRequestException(
                                "Content-Length too long")
                        if headers.get("Expect") == "100-continue":
                            self.stream.write(
                                b("HTTP/1.1 100 (Continue)\r\n\r\n"))
                        self.stream.read_bytes(content_length,
                                            self._on_request_body)
                        return
                    self.request_callback(self._request)
                else:
                    # The code above was taken from the tornado.httpserver
                    # module. It's perfect till now. My problem starts on the
                    # next lines when our very smart async framework just tries
                    # to read the whole content of received request, instead of
                    # reading chunks.
                    self.content_length = content_length
                    if self.content_length:
                        self.read_chunk()
                    else:
                        self.request_callback(self._request)
            else:
                self.request_callback(self._request)

        except _BadRequestException, e:
            logging.info("Malformed HTTP request from %s: %s",
                         self.address[0], e)
            self.stream.close()
            return

    def read_chunk(self):
        # To fix this problem I have an attribute that holds the size
        # of data readed and I'll compare this size with content-length
        # and I'll return the 100-continue http status until this
        # readed size becomes the same as content-length.
        chunk_size = min(
            self.chunk_size,
            self.content_length - len(self.readed_data))
        if chunk_size > 0:
            self.stream.read_bytes(chunk_size, self._on_read_chunk)
            self.stream.write(b("HTTP/1.1 100 (Continue)\r\n\r\n"))
            self.request_callback(self._request)
        else:
            self._on_request_body(self.readed_data)

    def _on_read_chunk(self, data):
        # It is a design decision to save the current data in an
        # attribute and thus in the memory. The readed data object could
        # be a data handler instance that knows when to save in memory
        # and when to save on the disk, based for example in the upload
        # size.
        self.readed_data += data

        # I don't need to read the whole buffer to realize that it's
        # bigger than the size tornado expects by default
        # if len(data) > self.stream.max_buffer_size:
        #     logging.info("Malformed HTTP request from %s: %s",
        #                  self.address[0], e)
        #     self.stream.close()
        #     return
        self.read_chunk()
