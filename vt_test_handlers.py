# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 QGIS Plugin for viewing data in 3D
                              -------------------
        begin                : 2014-02-03
        copyright            : (C) 2014 by Cubee(ESIPE)
        email                : lp_vizitown@googlegroups.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from cyclone.web import RequestHandler
from cyclone.websocket import WebSocketHandler
sys.path.pop(0)


## Ping handler
#  Basic HTTP request handler which return "pong"
#  to a GET HTTP
class PingHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    ## Handle GET HTTP
    def get(self):
        self.write("Hello, world")


## Echo handler
#  Basic HTTP request handler which return "pong"
#  to a GET HTTP
class EchoHandler(WebSocketHandler):
    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket opened"

    ## Method call when a message is received
    #  Return the message content to the sender
    def messageReceived(self, message):
        self.sendMessage(message)

    ## Method call when the websocket is closed
    def connectionLost(self, reason):
        print "WebSocket closed"
