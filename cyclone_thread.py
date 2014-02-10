import sys
from PyQt4.QtCore import *

import cyclone.web
from cyclone.bottle import run, route, unrun

from vt_test_handlers import PingHandler, EchoHandler
from vt_as_handlers import DataHandler, SyncHandler


class MainHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class CycloneThread(QThread):
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

    def stop(self):
        try:
            unrun()
        except:
            pass
