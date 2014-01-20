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

import os
import webbrowser
import re

from ui_vizitown import Ui_Vizitown
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *

import vt_utils_parser
from vt_as_app import VTAppServer
from vt_as_providers import ProviderManager, PostgisProvider


## Vizitown dialog in QGIS GUI
class VizitownDialog(QtGui.QDialog, Ui_Vizitown):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.destroyed.connect(self.closeEvent)
        self.appServer = None
        self.appServerRunning = False

    ## Behavior whit a close event
    def closeEvent(self, QCloseEvent):
        if self.appServer:
            self.appServer.stop()

    ## Set the default extent
    def initExtent(self, extent):
        self.extent = extent
        self.Xmin.setText("%.4f" % extent.xMinimum())
        self.Ymin.setText("%.4f" % extent.yMinimum())
        self.Xmax.setText("%.4f" % extent.xMaximum())
        self.Ymax.setText("%.4f" % extent.yMaximum())

        ## Set the values of the taile by default
        self.cb_tuile.clear()
        self.cb_tuile.addItem('256 x 256')
        self.cb_tuile.addItem('512 x 512')
        self.cb_tuile.addItem('1024 x 1024')
        self.cb_tuile.addItem('2048 x 2048')
        self.cb_tuile.addItem('4096 x 4096')
        self.cb_tuile.setCurrentIndex(1)

    ## Reset all widgets
    def clearListWidget(self):
        self.cb_MNT.clear()
        self.cb_Raster.clear()
        self.listWidget_Left.clear()
        self.listWidget_Right.clear()

    ## Get the geometry of the layer
    def getGeometry(self, layer):
        if layer.wkbType() == QGis.WKBPoint:
            return 'Point'
        if layer.wkbType() == QGis.WKBPolygon:
            return 'Polygon'
        if layer.wkbType() == QGis.WKBLineString:
            return 'LineString'
        if layer.wkbType() == QGis.WKBMultiPolygon:
            return 'Multipolygon'

    ## Return True if the layer is a Data Elevation Model which come from a database
    def isDem(self, layer):
        return (layer.type() == QgsMapLayer.RasterLayer and
                layer.providerType() == "gdal" and
                layer.bandCount() == 1) and not layer.source().startswith('dbname')

    ## Return True if the layer is a Raster which come from a database
    def isRaster(self, layer):
        return (layer.type() == QgsMapLayer.RasterLayer and
                layer.providerType() == "gdal" and
                layer.bandCount() >= 3) and not layer.source().startswith('dbname')

    ## Return True if the layer is a Vector which come from a database
    def isVector(self, layer):
        return (layer.type() == QgsMapLayer.VectorLayer) and layer.source().startswith('dbname')

    ## Add layer in combobox and listWidget
    def loadLayers(self):
        self.clearListWidget()
        layerListIems = QgsMapLayerRegistry().instance().mapLayers().items()
        for id, layer in layerListIems:
            if self.isDem(layer):
               # item = QtGui.QAbstractItemModel(self.cb_MNT)
               # item.setData(id, layer, QtCore.Qt.UserRole)
                self.cb_MNT.addItem(layer.name(), id)
            if self.isVector(layer):
                name = layer.name() + ' ' + re.search("(\(.*\)+)", layer.source()).group(0)
                item = QtGui.QListWidgetItem(name, self.listWidget_Left)
                item.setData(QtCore.Qt.UserRole, layer)
            if self.isRaster(layer):
                self.cb_Raster.addItem(layer.name(), id)

    ## Add vector layer in a right listView
    def on_but_Add_released(self):
        self.listWidget_Right.addItem(self.listWidget_Left.takeItem(self.listWidget_Left.currentRow()))

    ## Remove vector layer in a right listView
    def on_but_Supp_released(self):
        self.listWidget_Left.addItem(self.listWidget_Right.takeItem(self.listWidget_Right.currentRow()))

    ## Set the tab advanced option by default
    def on_but_defaut_released(self):
        self.Numero_Port.setText("8888")
        self.cb_tuile.setCurrentIndex(1)

    ## Get the port number. If the port isn't good this function return the value by default, 8888
    def getPort(self):
        if self.Numero_Port.text().isdigit() and int(self.Numero_Port.text()) < 65536 and int(self.Numero_Port.text()) > 1024 :
            return self.Numero_Port.text()
        else:
            return 8888

    ## Get the size tile
    def getSizeTile(self):
        index = self.cb_tuile.currentIndex()
        if index==0:
            return 256
        if index==1:
            return 512
        if index==2:
            return 1024
        if index==3:
            return 2048
        if index==4:
            return 4096

    ## Generate and launch the rendering of the 3D scene
    def on_btnGenerate_released(self):
        if self.appServerRunning:
            self.btnGenerate.setText("Server is stopping")
            self.appServer.stop()
            self.btnGenerate.setText("Generate")
            self.appServerRunning = False
        else:
            self.createProviders()
            initParam = self.getInitParam()
            self.appServer = VTAppServer(self, initParam)
            self.appServer.start()
            self.btnGenerate.setText("Server is running")
            self.openWebBrowser(self.getPort())
            self.appServerRunning = True

    ## Open a web browser
    def openWebBrowser(self, port):
        url = 'http://localhost:' + str(port)
        webbrowser.open(url)

    ## Create all providers with the selected layers in the GUI
    def createProviders(self):
        for i in range(self.listWidget_Right.count()):
            vectorLayer = self.listWidget_Right.item(i).data(QtCore.Qt.UserRole)
            d = vt_utils_parser.parseVector(vectorLayer.source())
            provider = PostgisProvider(d['host'], d['dbname'], d['user'], d['password'], d['srid'], d['table'], d['column'])
            ProviderManager.instance().addVectorProvider(provider)

    #def createRasterProviders(self):
        #dem = RasterProvider(name, extent, srid, source, httpRessource)
        #ProviderManager.instance().dem = dem
        #texture = RasterProvider(name, extent, srid, source, httpRessource)
        #ProviderManager.instance().raster = texture

    def getInitParam(self):
        return {
            'tileSize': self.getSizeTile(),
            'images': ['img_name_1'],
            'rootImgUrl': "http://localhost:" + self.getPort() + "/rasters",
            'extent': {
                'Xmin': self.Xmin.setText("%.4f" % self.extent.xMinimum()),
                'Ymin': self.Ymin.setText("%.4f" % self.extent.yMinimum()),
                'Xmax': self.Xmax.setText("%.4f" % self.extent.xMaximum()),
                'Ymax': self.Ymax.setText("%.4f" % self.extent.yMaximum()),
            },
            'port' : self.getPort()
        }
