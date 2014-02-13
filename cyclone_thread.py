import sys
import os
from PyQt4.QtCore import *

import cyclone.web
from cyclone.bottle import run, route, unrun

from vt_test_handlers import PingHandler, EchoHandler
from vt_as_handlers import DataHandler, SyncHandler, InitHandler, TilesInfoHandler


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
    def __init__(self, parentObject, initParam, GDALprocess, tilesInfo, debug=True):
        QThread.__init__(self, parentObject.thread())
        self.debug = debug
        self.initParam = initParam
        self.GDALprocess = GDALprocess
        self.tilesInfo = tilesInfo

    def run(self):
        rastersPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "rasters")
        handlers = [
            (r'/init', InitHandler, dict(initParam=self.initParam)),
            (r'/data', DataHandler),
            (r'/sync', SyncHandler),
            (r'/tiles_info', TilesInfoHandler, dict(GDALprocess=self.GDALprocess, tilesInfo=self.tilesInfo)),
            (r'/rasters/(.*)', cyclone.web.StaticFileHandler, {"path": rastersPath}),
        ]
        if self.debug:
            handlers.append((r'/test/echo', EchoHandler))
            handlers.append((r'/test/ping', PingHandler))
        run(host="127.0.0.1", port=int(self.initParam['port']), more_handlers=handlers)

    ## Stop the cyclone server
    def stop(self):
        try:
            unrun()
        except:
            pass
