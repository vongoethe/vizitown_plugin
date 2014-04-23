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
from PyQt4.QtCore import *

sys.path.insert(0, os.path.dirname(__file__))
from cyclone.bottle import run, route, unrun
sys.path.pop(0)

from vt_test_handlers import PingHandler, EchoHandler
from vt_as_handlers import *
from vt_utils_parameters import Parameters


## CycloneThread
#  A specific thread to run cyclone in it.
#  It use the QThread implementation.
class CycloneThread(QThread):

    ## Constructor
    #  @param init a dictionary with the parameters for the browser
    #  @param parentObject the parent QThread
    #  @param debug if True add two default handlers,
    #  '/test/echo' a echo server in websocket and
    #  '/test/ping' handle HTTP GET request and return "pong"
    def __init__(self, parentObject, debug=True):
        QThread.__init__(self, parentObject.thread())
        self.debug = debug
        self.parameters = Parameters.instance()

    ## run method
    #  Launch the cyclone server and create the handler
    #  @override QThread
    def run(self):
        handlers = [
            (r'/app/(.*)', CorsStaticFileHandler, {"path": self.parameters.viewerPath}),
            (r'/init', InitHandler),
            (r'/data', DataHandler),
            (r'/sync', SyncHandler),
            (r'/rasters/(.*)', CorsStaticFileHandler, {"path": self.parameters.rastersPath}),
        ]

        if self.parameters.get_viewer_param()['hasRaster']:
            handlers.append((r'/tiles_info', TilesInfoHandler))
        if self.debug:
            handlers.append((r'/test/echo', EchoHandler))
            handlers.append((r'/test/ping', PingHandler))
        run(host="127.0.0.1", port=self.parameters.port, more_handlers=handlers)

    ## stop method
    #  Stop the cyclone server
    #  @override QThread
    def stop(self):
        try:
            unrun()
        except:
            pass
