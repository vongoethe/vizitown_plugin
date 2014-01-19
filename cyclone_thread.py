import sys
from PyQt4.QtCore import *

import cyclone.web
from cyclone.bottle import run, route, unrun

from vt_test_handlers import PingHandler, EchoHandler
from vt_as_handlers import DataHandler, SyncHandler


## CycloneThread
#  A specific thread to run cyclone in it.
#  It use the QThread implementation.
class CycloneThread(QThread):

    ## Constructor
    #  @param parentObject the parent QObject
    #  @param debug if True add two default handlers,
    #  '/test/echo' a echo server in websocket and
    #  '/test/ping' handle HTTP GET request and return "pong"
    def __init__(self, parentObject, debug=True):
        QThread.__init__(self, parentObject.thread())
        self.debug = debug

    def run(self):
        handlers = [
            (r'/data', DataHandler),
            (r'/sync', SyncHandler),
        ]
        if self.debug:
            handlers.append((r'/test/echo', EchoHandler))
            handlers.append((r'/test/ping', PingHandler))
        run(host="127.0.0.1", port=8888, more_handlers=handlers)

    ## Stop the cyclone server
    def stop(self):
        try:
            unrun()
        except:
            pass
