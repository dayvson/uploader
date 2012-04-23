# -*- Coding: utf-8; Mode: Python -*-
#
# app/worker_transcode.py - Part of superuploader test for soundcloud
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
This module's goal is to provide a worker for transcode audio files
When the user finish the upload this worker will receive a message
and start to transcode the audio from diferrent container/codec
to aac using FFMPEG
"""
from tornado.ioloop import IOLoop
from rabbit_helper import RabbitHelper
from stormed import Connection, Message
import logging
import time
import os
import ast
import subprocess


class AudioTranscode(object):
    """This is a auxiliary class to transcode audio to final format
    using a subprocess call
    """
    def __init__(self, audio_id):
        self.audio_id = audio_id
        path = '/Users/dayvson/uploader/'
        self.path_absolute_audio = path + 'transcoded/%s.mp4' % self.audio_id
        self.path_absolute_temp = path + 'data/%s' % self.audio_id

    def start(self, on_complete=None, on_error=None):
        self._on_complete = on_complete
        self._on_error = on_error
        command_convert = ["ffmpeg", "-i", self.path_absolute_temp,\
                    "-f", "mp4", "-acodec", "libfaac",\
                    "-aq", "128", "-ar", "44100",  self.path_absolute_audio]
        p = subprocess.call(command_convert, shell=False)
        if p == 0:
            self.on_complete()
        else:
            self.on_error()

    def on_complete(self):
        try:
            os.remove(self.path_absolute_temp)
        except:
            pass
        if self._on_complete:
            self._on_complete(self.audio_id)
        print "Transcode complete OUTPUT:%s" % self.path_absolute_audio

    def on_error(self):
        print "Transcode Error OUTPUT expected:%s" % self.path_absolute_audio


def send_push_notification(metadata):
    print "send_push_notification"
    rabbit = RabbitHelper()
    rabbit.send_message(metadata, queue='push_notification',
                        routing_key='push_notification')


def transcode_connect():
    ch = conn.channel()
    ch.queue_declare(queue='uploaded', durable=True)
    ch.qos(prefetch_count=1)
    ch.consume('uploaded', on_consume)


def on_consume(msg):
    print "=> Prepare to start transcoding process %r" % msg.body
    file_info = ast.literal_eval(msg.body)
    audioTask = AudioTranscode(file_info['fileName'])
    audioTask.start(send_push_notification)
    message_done(msg)


def message_done(msg):
    print "This message was processed..."
    print '=> Waiting for audio to transcode and disptach messages after task complete.'
    msg.ack()


def init_worker():
    logging.basicConfig()
    global conn
    conn = Connection(host='localhost')
    conn.connect(transcode_connect)
    io_loop = IOLoop.instance()
    print '=> Waiting for audio to transcode and disptach messages after task complete.'
    try:
        io_loop.start()
    except KeyboardInterrupt:
        conn.close(io_loop.stop)


if __name__ == "__main__":
    init_worker()
