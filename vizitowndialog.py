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
import sys
import multiprocessing as mp

from ui_vizitown import Ui_Vizitown
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from PyQt4.QtSql import *

import vt_utils_parser
from vt_utils_tiler import TileGenerator
from vt_as_app import VTAppServer
from vt_as_providers import *


## Vizitown dialog in QGIS GUI
class VizitownDialog(QtGui.QDialog, Ui_Vizitown):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.destroyed.connect(self.closeEvent)
        self.appServer = None
        self.appServerRunning = False
        self.GDALprocess = None

    ## Kill GDAL process and remove unfinished tiled files
    def killGDALProcess(self):
        if self.GDALprocess:
            self.GDALprocess.terminate()

            self.GDALprocess = None

    ## Behavior whit a close event
    def closeEvent(self, QCloseEvent):
        if self.appServer:
            self.appServer.stop()
        if self.GDALprocess:
            GDALDialog = QtGui.QMessageBox()
            GDALDialog.setIcon(QtGui.QMessageBox.Warning)
            GDALDialog.setText("The tiling process is not complete. Would you like to run the process in background to use te generated tile later ?")
            GDALDialog.setStandardButtons(QtGui.QMessageBox.Discard | QtGui.QMessageBox.Save)
            ret = GDALDialog.exec_()
            if ret == QtGui.QMessageBox.Save:
                print "GDALprocess continue"
            if ret == QtGui.QMessageBox.Discard:
                self.killGDALProcess()

    ## Set the default extent
    def initExtent(self, extent):
        self.extent = extent
        self.Xmin.setText("%.4f" % extent.xMinimum())
        self.Ymin.setText("%.4f" % extent.yMinimum())
        self.Xmax.setText("%.4f" % extent.xMaximum())
        self.Ymax.setText("%.4f" % extent.yMaximum())

    ## Set the the of the combobox
    def initComboBox(self):
        ## Set the values of the taile by default
        self.cb_tuile.clear()
        self.cb_tuile.addItem('256 x 256')
        self.cb_tuile.addItem('512 x 512')
        self.cb_tuile.addItem('1024 x 1024')
        self.cb_tuile.addItem('2048 x 2048')
        self.cb_tuile.addItem('4096 x 4096')
        self.cb_tuile.setCurrentIndex(1)

        self.Numero_Port.setText("8888")

        ## Set the value of the zoom level
        self.cb_zoom.clear()
        self.cb_zoom.addItem('1')
        self.cb_zoom.addItem('2')
        self.cb_zoom.addItem('3')
        self.cb_zoom.addItem('4')
        self.cb_zoom.addItem('5')
        self.cb_zoom.setCurrentIndex(1)

    ## Reset all widgets
    def clearListWidget(self):
        self.cb_MNT.clear()
        self.cb_Raster.clear()
        self.layerSelectionWidget.clearContents()
        self.layerSelectionWidget.setHorizontalHeaderLabels(('Display', 'Layer', 'Field'))
        self.layerSelectionWidget.setColumnWidth(0, 45)
        self.layerSelectionWidget.setColumnWidth(1, 150)
        # set column name of layerSelectionWidget
        self.progressBar.hide()

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

    ## Return true if there is a least one raster to generate
    def needGenerateRaster(self):
        return self.cb_MNT.count() > 0 or self.cb_Raster.count() > 0

    ## Add layer in combobox and listWidget
    def get_info_table(self, host, dbname, user, password, table):
        db = QSqlDatabase.addDatabase("QPSQL")
        db.setHostName(host)
        db.setDatabaseName(dbname)
        db.setUserName(user)
        db.setPassword(password)
        if db.open():
            query = QSqlQuery(db)
            st = table.split('.')
            st[0] = re.sub('"', '\'', st[0])
            st[1] = re.sub('"', '\'', st[1])
            getInfo = """
                SELECT column_name, udt_name
                FROM information_schema.columns
                WHERE table_name = {table_} AND table_schema = {schema_}
                ORDER BY column_name;
            """.format(table_=st[1], schema_=st[0])
            query.exec_(getInfo)
            result = {}
            while query.next():
                result[query.value(0)] = query.value(1)
            return result
        else:
            raise Exception('Connection to database cannot be established')

    ## Add vector layer in QTableWidget
    def addItemTableWidget(self, item, dic):
        self.layerSelectionWidget.insertRow(0)
        checkBox = QtGui.QTableWidgetItem()
        checkBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkBox.setCheckState(QtCore.Qt.Unchecked)
        comboBox = QtGui.QComboBox()
        self.addItemComboBox(comboBox, dic)
        self.layerSelectionWidget.setItem(0, 0, checkBox)
        self.layerSelectionWidget.setItem(0, 1, item)
        self.layerSelectionWidget.setCellWidget(0, 2, comboBox)

    ## Add item in a QComboBox which is in QTableWidget
    def addItemComboBox(self, comboBox, dic):
        comboBox.addItem("None")
        for nameColumn, type in dic.items():
            comboBox.addItem(nameColumn + ' - ' + type)

    ## Add layer in QCombobox and QTableWidget
    def loadLayers(self):
        self.clearListWidget()
        layerListIems = QgsMapLayerRegistry().instance().mapLayers().items()
        for id, layer in layerListIems:
            if self.isDem(layer):
                self.cb_MNT.addItem(layer.name(), layer)
            if self.isVector(layer):
                d = vt_utils_parser.parseVector(layer.source())
                dic = self.get_info_table(d['host'], d['dbname'], d['user'], d['password'], d['table'])
                name = layer.name() + ' ' + re.search("(\(.*\)+)", layer.source()).group(0)
                item = QtGui.QTableWidgetItem(name)
                item.setData(QtCore.Qt.UserRole, layer)
                self.addItemTableWidget(item, dic)
            if self.isRaster(layer):
                self.cb_Raster.addItem(layer.name(), layer)

    ## Set the tab advanced option by default
    def on_btn_defaut_released(self):
        self.Numero_Port.setText("8888")
        self.cb_tuile.setCurrentIndex(1)
        self.cb_zoom.setCurrentIndex(1)
        self.layerSelectionWidget.clear()

    ## Get the port number. If the port isn't good this function return the value by default, 8888
    def getPort(self):
        if self.Numero_Port.text().isdigit() and int(self.Numero_Port.text()) < 65536 and int(self.Numero_Port.text()) > 1024:
            return self.Numero_Port.text()
        else:
            # Maybe change for another exotic port
            return 8888

    ## Get the size tile
    def getSizeTile(self):
        index = self.cb_tuile.currentIndex()
        if index == 0:
            return 256
        if index == 1:
            return 512
        if index == 2:
            return 1024
        if index == 3:
            return 2048
        if index == 4:
            return 4096

    ## Get the intial parameter to give at the app server
    def getInitParam(self):
        return {
            'extent': {
                'Xmin': "%.4f" % self.extent.xMinimum(),
                'Ymin': "%.4f" % self.extent.yMinimum(),
                'Xmax': "%.4f" % self.extent.xMaximum(),
                'Ymax': "%.4f" % self.extent.yMaximum(),
            },
            'port': self.getPort(),
            'hasRaster': self.needGenerateRaster(),
        }

    ## Get the tiles info done by the process GDAL
    def getTilesInfo(self):
        return {
            'zoomLevel': int(self.cb_zoom.currentText()),
            'tileSize': self.getSizeTile(),
            'dem': ProviderManager.instance().dem.httpRessource,
            'texture': ProviderManager.instance().raster.httpRessource,
        }

    ## Generate and launch the rendering of the 3D scene
    def on_btn_generate_released(self):
        if self.appServerRunning:
            self.progressBar.hide()
            self.btn_generate.setText("Server is stopping")
            self.appServer.stop()
            self.btn_generate.setText("Generate")
            self.appServerRunning = False
            self.killGDALProcess()
        else:
            self.progressBar.show()
            self.createVectorProviders()
            self.createRasterProviders()
            initParam = self.getInitParam()
            if self.needGenerateRaster():
                tilesInfo = self.getTilesInfo()
                self.appServer = VTAppServer(self, initParam, self.GDALprocess, tilesInfo)
            else:
                self.appServer = VTAppServer(self, initParam)
            self.appServer.start()
            self.btn_generate.setText("Server is running")
            self.openWebBrowser(self.getPort())
            self.appServerRunning = True

    ## Open a web browser
    def openWebBrowser(self, port):
        url = 'http://localhost:' + str(port)
        webbrowser.open(url)

    ## Create all providers with the selected layers in the GUI
    def createVectorProviders(self):
        for i in range(self.layerSelectionWidget.rowCount()):
            # if the layer is checked
            if self.layerSelectionWidget.item(i, 0).checkState() == 2:
                vectorLayer = self.layerSelectionWidget.item(i, 1).data(QtCore.Qt.UserRole)
                column2 = self.layerSelectionWidget.cellWidget(i, 2).currentText()
                column2Name = "None"
                column2Type = "None"
                if not column2 == "None":
                    column2Name = column2.split(" - ")[0]
                    column2Type = column2.split(" - ")[1]
                d = vt_utils_parser.parseVector(vectorLayer.source())
                provider = PostgisProvider(d['host'], d['dbname'], d['user'], d['password'], d['srid'], d['table'], d['column'], column2Name, column2Type)
                ProviderManager.instance().addVectorProvider(provider)

    ## Create all providers for DEM and raster
    def createRasterProviders(self):
        dataSrcImg = None
        dataSrcMnt = None
        path = os.path.join(os.path.dirname(__file__), "rasters")
        extent = [self.extent.xMinimum(), self.extent.xMaximum(), self.extent.yMinimum(), self.extent.yMaximum()]
        tileSize = self.getSizeTile()
        levels = int(self.cb_zoom.currentText())
        if self.cb_MNT.count() > 0:
            mnt = self.cb_MNT.itemData(self.cb_MNT.currentIndex())
            httpRessource = 'http://localhost:' + self.getPort() + '/rasters/' + '_'.join(['dem', mnt.name(), str(tileSize), str(levels)])
            dem = RasterProvider(mnt.name(), mnt.extent(), mnt.crs().postgisSrid(), mnt.source(), httpRessource)
            ProviderManager.instance().dem = dem
            dataSrcMnt = dem.source
        if self.cb_Raster.count() > 0:
            raster = self.cb_Raster.itemData(self.cb_Raster.currentIndex())
            httpRessource = 'http://localhost:' + self.getPort() + '/rasters/' + '_'.join(['img', raster.name(), str(tileSize), str(levels)])
            texture = RasterProvider(raster.name(), raster.extent(), raster.crs().postgisSrid(), raster.source(), httpRessource)
            ProviderManager.instance().raster = texture
            dataSrcImg = texture.source
        if self.needGenerateRaster():
            if os.name is 'nt':
                pythonPath = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
                mp.set_executable(pythonPath)
                sys.argv = [None]
            self.GDALprocess = mp.Process(target=launch_process, args=(dataSrcImg, dataSrcMnt, path, extent, tileSize, levels))
            self.GDALprocess.start()


## launch_process manage the several process to generate data tiles
def launch_process(dataSrcImg, dataSrcMnt, path, extent, tileSize=512, levels=2):
    if (TileGenerator._check_existing_dir(dataSrcImg, dataSrcMnt, path, tileSize, levels) != 0):
        generator = TileGenerator(dataSrcImg, dataSrcMnt, path, extent, tileSize, levels)
        generator._create_repositories()
        generator._calculate_extent()
        generator._process_merge()
        if (generator.processChoice == 0):
            generator._process_tile_img()
            generator._process_clip_mnt(generator.dataDstImg, generator.dataDstMnt)
            generator._process_to_dim_tile(generator.dataDst, generator.tmpRepo)
        elif (generator.processChoice == 1):
            generator._process_tile_img()
            generator._process_to_dim_tile(generator.dataDst, generator.tmpRepo)
        elif (generator.processChoice == 2):
            generator._process_tile_mnt()
            generator._process_to_dim_tile(generator.dataDst, generator.tmpRepo)
        generator._clean_up()
