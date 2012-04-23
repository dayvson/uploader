# -*- Coding: utf-8; Mode: Python -*-
#
# app/worker_push_notification.py - Part of superuploader test for soundcloud
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
This module's goal is to provide a worker for push notification
with this you can add your songs to your dashboard and notify others
users sending an email or notify his devices like iphone/ipad/android.
When the audio was transcoded this worker is activate
"""
from tornado.ioloop import IOLoop
from stormed import Connection, Message


def push_connect():
    ch = conn.channel()
    ch.queue_declare(queue='push_notification', durable=True)
    ch.qos(prefetch_count=1)
    ch.consume('push_notification', on_consume)


def on_consume(msg):
    print 'File transcode: %r' % msg.body
    print """Now you can add to your dashboard and notify others
            sending an email or notify some devices like iphone/ipad/android
            using workers."""
    message_done(msg)


def message_done(msg):
    print " [x] Done"
    msg.ack()


def init_worker():
    global conn
    conn = Connection(host='localhost')
    conn.connect(push_connect)
    io_loop = IOLoop.instance()
    print '=> Waiting for push notifications to notify all devices.'
    try:
        io_loop.start()
    except KeyboardInterrupt:
        conn.close(io_loop.stop)


if __name__ == "__main__":
    init_worker()
