import sys
from cyclone.bottle import run, route, unrun

from PyQt4.QtCore import *

from vt_test_handlers import PingHandler, EchoHandler

class CycloneThread(QThread):
    def __init__(self, parentObject):
        QThread.__init__(self, parentObject.thread())
        self.running = False
        
    def run(self):
        self.running = True
        run(host="127.0.0.1", port=8888, log=sys.stdout, more_handlers=[(r'/echo', EchoHandler), (r'/', PingHandler)])
        self.running = False

    def stop(self):
        if self.running:
            try:
                unrun()
            except:
                self.running = False
                pass
        
    def isLaunched (self):
        return self.running