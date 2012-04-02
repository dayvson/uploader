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

import logging
import tornado.ioloop, tornado.web, tornado.httpserver, tornado.httputil
from tornado.web import asynchronous
from tornado.escape import utf8, native_str, parse_qs_bytes
from tornado.httpserver import _BadRequestException
from tornado.util import b

class StreamHTTPServer(tornado.httpserver.HTTPServer):
    def handle_stream(self, stream, address):
        StreamHTTPConnection(stream, address, self.request_callback, self.no_keep_alive, self.xheaders)
    
class StreamHTTPRequest(tornado.httpserver.HTTPRequest):
    def request_continue(self):
        logging.warning("REQUEST CONTINUE")
        if self.headers.get("Expect") == "100-continue":
            self.connection.stream.write(b("HTTP/1.1 100 (Continue)\r\n\r\n"))

    def _read_body(self, exec_req_cb):
        self.request_continue()
        logging.warning( "READ BODY")
        self.connection.stream.read_bytes(self.content_length,\
            lambda data: self._on_request_body(data, exec_req_cb))

    def _on_request_body(self, data, exec_req_cb):
        logging.warning( " _on_request_body READ BODY")
        self.body = data
        content_type = self.headers.get("Content-Type", "")
        if self.method in ("POST", "PUT"):
            if content_type.startswith("application/x-www-form-urlencoded"):
                arguments = parse_qs_bytes(native_str(self.body))
                for name, values in arguments.iteritems():
                    values = [v for v in values if v]
                    if values:
                        self.arguments.setdefault(name, []).extend(values)
            elif content_type.startswith("multipart/form-data"):
                fields = content_type.split(";")
                for field in fields:
                    logging.warning( "FIELD >>> %s" % field)
                    k, sep, v = field.strip().partition("=")
                    if k == "boundary" and v:
                        tornado.httputil.parse_multipart_form_data(utf8(v), data,\
                        self.arguments, self.files)
                        break
                else:
                    logging.warning("Invalid multipart/form-data")
        exec_req_cb()

class StreamHTTPConnection(tornado.httpserver.HTTPConnection):
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
                raise _BadRequestException("Malformed HTTP version in HTTP Request-Line")
            headers = tornado.httputil.HTTPHeaders.parse(data[eol:])
            self._request = StreamHTTPRequest(
                connection=self, method=method, uri=uri, version=version,
                headers=headers, remote_ip=self.address[0])

            content_length = headers.get("Content-Length")
            if content_length:
                content_length = int(content_length)
                if content_length > self.stream.max_buffer_size:
                    raise _BadRequestException("Content-Length too long")
                self._request.content_length = content_length
                
            self.request_callback(self._request)
        except _BadRequestException, e:
            logging.info("Malformed HTTP request from %s: %s",
                         self.address[0], e)
            self.stream.close()
            return

class StreamRequestHandler(tornado.web.RequestHandler):      
    def _execute(self, transforms, *args, **kwargs):
        self._transforms = transforms
        try:
            logging.warning(self.request)
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
            exec_req_cb = lambda: super(StreamRequestHandler,self)._execute(transforms, *args, **kwargs)
            if (getattr(self, '_read_body', True) and
                hasattr(self.request, 'content_length')):
                logging.warning("CALL READ BODY DO REQUEST >>> %s" % self.request)
                self.request._read_body(exec_req_cb)
            else:
                exec_req_cb()
        except Exception, e:
            self._handle_request_exception(e)


def streamUpload(cls):
    class StreamUpload(cls):
        def __init__(self, *args, **kwargs):
            if args[0]._wsgi:
                raise Exception("@streamUpload is not supported for WSGI apps")
            self._read_body = False
            if hasattr(cls, 'post'):
                cls.post = asynchronous(cls.post)
            if hasattr(cls, 'put'):
                cls.put = asynchronous(cls.put)
            cls.__init__(self, *args, **kwargs)
    return StreamUpload