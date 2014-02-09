# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VizitownDialog
                                 A QGIS plugin
 2D to 3D
                             -------------------
        begin                : 2014-01-09
        copyright            : (C) 2014 by Cubee(ESIPE)
        email                : vizitown@gmail.com
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

from multiprocessing import Process, Queue
from PyQt4 import QtCore, QtGui
from qgis.core import *
import os
import re
import vt_as_app
from ui_vizitown import Ui_Vizitown
from vt_as_app import VTAppServer

class VizitownDialog(QtGui.QDialog, Ui_Vizitown):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.destroyed.connect(self.closeEvent)
        self.appServer = None
        self.appServerRunning = False

    def closeEvent(self, QCloseEvent):
        self.appServer.stop()

    # Set the default extent
    def initExtent(self, extent):
        self.Xmin.setText("%.4f" % extent.xMinimum())
        self.Ymin.setText("%.4f" % extent.yMinimum())
        self.Xmax.setText("%.4f" % extent.xMaximum())
        self.Ymax.setText("%.4f" % extent.yMaximum())
        
    def clearListWidget (self):
        self.cb_MNT.clear()
        self.cb_Raster.clear()
        self.listWidget_Left.clear()
        self.listWidget_Right.clear()
        
    def isDem (self, layer):
        return (layer.type() == QgsMapLayer.RasterLayer and
                layer.providerType() == "gdal" and
                layer.bandCount() == 1)
    
    def isRaster (self, layer):
        return (layer.type() == QgsMapLayer.RasterLayer and
                layer.providerType() == "gdal" and
                layer.bandCount() >= 3)
    
    def isVector (self, layer):
        return (layer.type() == QgsMapLayer.VectorLayer)
    
    # Add layer in combobox and listWidget
    def loadLayers(self):
        self.clearListWidget()
        layerListIems = QgsMapLayerRegistry().instance().mapLayers().items()
        for id, layer in layerListIems:
            if self.isDem(layer):
                self.cb_MNT.addItem(layer.name(), id)
            if self.isVector(layer):
                self.listWidget_Left.addItem(layer.name())
            if self.isRaster(layer):
                self.cb_Raster.addItem(layer.name(), id)

    # Add vector layer in a right listView
    def add(self):
        self.listWidget_Right.addItem(self.listWidget_Left.takeItem(self.listWidget_Left.currentRow()))

    # Remove vector layer in a right listView
    def suppr(self):
        self.listWidget_Left.addItem(self.listWidget_Right.takeItem(self.listWidget_Right.currentRow()))

    # Set the tab advanced option by default
    def defaut(self):
        self.Numero_Port.setText("1042")
        self.Haut_Tuile.setText("")
        self.Larg_Tuile.setText("")
        
    # Run the 3D scene
    def on_btnGenerate_released(self):
        if self.appServerRunning:
            self.btnGenerate.setText("Server is stopping")
            self.appServer.stop()
            self.btnGenerate.setText("Generate")
            self.appServerRunning = False
        else:
            
            self.appServer = VTAppServer(self)
            self.appServer.start()
            self.btnGenerate.setText("Server is running")
            self.appServerRunning = True
        
