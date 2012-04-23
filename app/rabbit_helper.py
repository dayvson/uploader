# -*- Coding: utf-8; Mode: Python -*-
#
# app/rabbit_helper.py - Part of superuploader test for soundcloud
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
This module's goal is to provide a simple way to send message
for a queue over RabbitMQ
"""
from stormed import Connection, Message


class RabbitHelper(object):

    def __init__(self, on_sent=None):
        self.conn = Connection(host='localhost')
        self.on_sent = on_sent

    def send_message(self, message, queue='', exchange='', routing_key=''):
        self.msg = Message(message, delivery_mode=2)
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.conn.connect(lambda: self.on_connect())

    def on_connect(self):
        ch = self.conn.channel()
        ch.queue_declare(queue=self.queue, durable=True)
        ch.publish(self.msg, exchange=self.exchange,
                    routing_key=self.routing_key)
        self.conn.close(callback=self.done)

    def done(self):
        if self.on_sent:
            self.on_sent()
