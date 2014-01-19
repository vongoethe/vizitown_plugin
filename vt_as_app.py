import sys
import os

from PyQt4.QtCore import *
from pprint import pprint


## RollbackImporter.
# RollbackImporter instances install themselves as a proxy for the built-in
# :func:`__import__` function that lies behind the 'import' statement. Once
# installed, they note all imported modules, and when uninstalled, they
# delete those modules from the system module list; this ensures that the
# modules will be freshly loaded from their source code when next imported.
#
# Usage::
#
#     if self.rollbackImporter:
#         self.rollbackImporter.uninstall()
#     self.rollbackImporter = RollbackImporter()
#     # import some modules
class RollbackImporter(object):

    def __init__(self):
        """Init the RollbackImporter and setup the import proxy."""
        self.oldmodules = sys.modules.copy()

    def uninstall(self):
        """Unload all modules since __init__ and restore the original import."""
        for module in sys.modules.keys():
            if module not in self.oldmodules:
                del sys.modules[module]


## ViziTown Application Server
#  Use a cyclone server as backend
class VTAppServer(QObject):

    ## Constructor.
    #  @param parent  the QObject parent
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.rollbackImporter = None
        self.appThread = None
        self.timer = None

    ## Start the application server
    def start(self):
        # Unload cyclone
        self.stop()

        self.rollbackImporter = RollbackImporter()
        from cyclone_thread import CycloneThread

        self.appThread = CycloneThread(self.parent())

        # Use this signal from the thread to indicate the thread exited
        QObject.connect(self.appThread, SIGNAL("runFinished(PyQt_PyObject)"),
                        self.stop)
        QObject.connect(self.appThread, SIGNAL("runStatus(PyQt_PyObject)"),
                        self.stop)
        QObject.connect(self.appThread, SIGNAL("runError(PyQt_PyObject)"),
                        self.stop)

        self.appThread.start()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"),
                        self.yieldAppThread)
        self.timer.start(10)

    ## Stop the application server
    def stop(self):
        if self.appThread:
            while (self.appThread.isRunning()):
                self.appThread.stop()
                self.thread().msleep(10)
                QCoreApplication.instance().processEvents()
            del self.appThread
            self.appThread = None
        if self.rollbackImporter:
            self.rollbackImporter.uninstall()
        if self.timer:
            self.timer.stop()

    ## Yied application server thread to not hang the GUI
    def yieldAppThread(self):
        if self.appThread:
            self.appThread.msleep(1)
