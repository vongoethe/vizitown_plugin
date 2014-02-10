import sys
from PyQt4.QtCore import *

import cyclone.web
from cyclone.bottle import run, route, unrun

from vt_test_handlers import PingHandler, EchoHandler


class MainHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
    

class CycloneThread(QThread):
    def __init__(self, parentObject):
        QThread.__init__(self, parentObject.thread())
        
    def run(self):
        run(host="127.0.0.1", port=8888, more_handlers=[(r'/echo', EchoHandler), (r'/', PingHandler)])

    def stop(self):
        try:
            unrun()
        except:
            pass