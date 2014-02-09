import sys
from cyclone.bottle import run, route, unrun

from PyQt4.QtCore import *

from vt_test_handlers import PingHandler, EchoHandler

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