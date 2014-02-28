import sys
import os

from PyQt4.QtCore import *


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

    ## Constructor
    def __init__(self):
        """Init the RollbackImporter and setup the import proxy."""
        self.oldmodules = sys.modules.copy()

    ## uninstall method
    #  unload all the module
    def uninstall(self):
        """Unload all modules since __init__ and restore the original import."""
        for module in sys.modules.keys():
            if module not in self.oldmodules:
                del sys.modules[module]


## ViziTown Application Server
#  Use a cyclone server as backend
#  Unherited QObject
class AppServer(QObject):

    ## Constructor.
    #  @param parent  the QObject parent
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.rollbackImporter = None
        self.appThread = None
        self.timer = None
        self.saveStdout = sys.stdout
        self.saveStderr = sys.stderr

    ## start method
    #  Launch the application server
    #  @override QObject
    def start(self):
        # Unload cyclone
        self.stop()

        # Stock the current state of python import and rollback it if try to restart the AppServer
        self.rollbackImporter = RollbackImporter()
        from vt_as_cyclone import CycloneThread

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
                        self.yield_thread)
        self.timer.start(10)

    ## stop method
    #  Stop the application server and clean the import modules
    #  @override QObject
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
        sys.stdout = self.saveStdout
        sys.stderr = self.saveStderr

    ## yield_thread method
    #  Yied application server thread to not hang the GUI
    #  @override QObject
    def yield_thread(self):
        if self.appThread:
            self.appThread.msleep(1)
