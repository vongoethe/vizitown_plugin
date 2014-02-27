import sys
import os
from PyQt4.QtCore import *

import cyclone.web
from cyclone.bottle import run, route, unrun

from vt_test_handlers import PingHandler, EchoHandler
from vt_as_handlers import *
from vt_utils_parameters import Parameters


## CycloneThread
#  A specific thread to run cyclone in it.
#  It use the QThread implementation.
class CycloneThread(QThread):

    ## Constructor
    #  @param parentObject the parent QObject
    #  @param init a dictionary with the parameters for the browser
    #  @param debug if True add two default handlers,
    #  '/test/echo' a echo server in websocket and
    #  '/test/ping' handle HTTP GET request and return "pong"
    def __init__(self, parentObject, debug=True):
        QThread.__init__(self, parentObject.thread())
        self.debug = debug
        self.parameters = Parameters.instance()

    ## run method launch the cyclone server
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

    ## stop method stop the cyclone server
    def stop(self):
        try:
            unrun()
        except:
            pass
