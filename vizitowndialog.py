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
import re
import sys
import multiprocessing as mp
import shutil

from ui_vizitown import Ui_Vizitown
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *

from vt_as_app import AppServer
from vt_as_provider_manager import ProviderManager
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider

import vt_utils_parser
from vt_utils_tiler import TileGenerator
from vt_utils_gui import *


## A intermediate method too launch process without import issue on windows
def launch_gdal_process(dataSrcImg, dataSrcMnt, path, extent, tileSize=512, levels=2):
    TileGenerator.launch_process(dataSrcImg, dataSrcMnt, path, extent, tileSize, levels)


## Vizitown dialog in QGIS GUI
class VizitownDialog(QtGui.QDialog, Ui_Vizitown):

    ## The Constructor
    def __init__(self, extent):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.destroyed.connect(self.closeEvent)
        self.appServer = None
        self.appServerRunning = False
        self.GDALprocess = None

    ## Set the default extent
    #  @param extent the extent to init the parameter
    def init_extent(self, extent):
        self.extent = extent
        self.le_xmin.setText("%.4f" % extent.xMinimum())
        self.le_ymin.setText("%.4f" % extent.yMinimum())
        self.le_xmax.setText("%.4f" % extent.xMaximum())
        self.le_ymax.setText("%.4f" % extent.yMaximum())

    ## Set the the of the combobox
    def init_tile_size(self):
        ## Set the values of the taile by default
        self.cb_tile.clear()
        self.cb_tile.addItem('256 x 256')
        self.cb_tile.addItem('512 x 512')
        self.cb_tile.addItem('1024 x 1024')
        self.cb_tile.addItem('2048 x 2048')
        self.cb_tile.addItem('4096 x 4096')
        self.cb_tile.setCurrentIndex(1)

    ## Set the the of the combobox
    def init_zoom_level(self):
        ## Set the value of the zoom level
        self.cb_zoom.clear()
        self.cb_zoom.addItem('1')
        self.cb_zoom.addItem('2')
        self.cb_zoom.addItem('3')
        self.cb_zoom.addItem('4')
        self.cb_zoom.addItem('5')
        self.cb_zoom.setCurrentIndex(1)

    ## Init combobox and table layers
    def init_layers(self):
        self.reset_all_fields()
        layerListIems = QgsMapLayerRegistry().instance().mapLayers().items()
        for id, layer in layerListIems:
            if is_dem(layer):
                self.cb_dem.addItem(layer.name(), layer)
            if is_vector(layer):
                d = vt_utils_parser.parse_vector(layer.source())
                dic = PostgisProvider.get_columns_info_table(d['host'], d['dbname'], d['user'], d['password'], d['table'])
                name = layer.name() + ' ' + re.search("(\(.*\)+)", layer.source()).group(0)
                item = QtGui.QTableWidgetItem(name)
                item.setData(QtCore.Qt.UserRole, layer)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.add_vector_layer(item, dic)
            if is_texture(layer):
                self.cb_texture.addItem(layer.name(), layer)

    ## Reset all widgets
    def reset_all_fields(self):
        self.cb_dem.clear()
        self.cb_texture.clear()
        self.tw_layers.setRowCount(0)
        self.tw_layers.setHorizontalHeaderLabels(('Display', 'Layer', 'Field'))
        self.tw_layers.setColumnWidth(0, 45)
        self.tw_layers.setColumnWidth(1, 150)
        # set column name of tw_layers
        self.pb_loading.hide()

    ## Return true if there is a DEM to generate
    def has_dem(self):
        return self.cb_dem.count() > 0

    ## Return true if there is a texture to generate
    def has_texture(self):
        return self.cb_texture.count() > 0

    ## Return true if there is a least one raster to generate
    def has_raster(self):
        return self.has_dem() or self.has_texture()

    ## Add vector layer in QTableWidget
    #  @param item the new layer to add in the dic
    #  @param dic the dic with the existant data
    def add_vector_layer(self, item, dic):
        self.tw_layers.insertRow(0)
        checkBox = QtGui.QTableWidgetItem()
        checkBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkBox.setCheckState(QtCore.Qt.Unchecked)
        comboBox = QtGui.QComboBox()
        comboBox.addItem("None")
        for nameColumn, type in dic.items():
            comboBox.addItem(nameColumn + ' - ' + type)
        self.tw_layers.setItem(0, 0, checkBox)
        self.tw_layers.setItem(0, 1, item)
        self.tw_layers.setCellWidget(0, 2, comboBox)

    ## Get the port number. If the port isn't good this function return the value by default, 8888
    def get_port(self):
        if self.le_port.text().isdigit() and int(self.le_port.text()) < 65536 and int(self.le_port.text()) > 1024:
            return self.le_port.text()
        else:
            # Maybe change for another exotic port
            return 8888

    ## Get the size tile
    def get_size_tile(self):
        index = self.cb_tile.currentIndex()
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

    ## Get the extent specified in the GUI
    def get_gui_extent(self):
        return [float(self.le_xmin.text()), float(self.le_ymin.text()), float(self.le_xmax.text()), float(self.le_ymax.text())]

    ## Set the tab advanced option by default
    #  @override QtGui.QDialog
    def on_btn_default_released(self):
        self.le_port.setText("8888")
        self.cb_tile.setCurrentIndex(1)
        self.cb_zoom.setCurrentIndex(1)
        self.tw_layers.clear()

    ## Generate and launch the rendering of the 3D scene
    def on_btn_generate_released(self):
        if self.appServerRunning:
            self.closeEvent(None)
        else:
            self.pb_loading.show()
            self.create_vector_providers()
            self.create_raster_providers()
            viewerParam = build_viewer_param(self.get_gui_extent(), self.get_port(), self.has_raster())
            if self.has_raster():
                demResource = ProviderManager.instance().dem.httpResource
                textureResource = ProviderManager.instance().dem.httpResource
                tilingParam = build_tiling_param(int(self.cb_zoom.currentText()), self.get_size_tile(), demResource, textureResource)
                self.appServer = AppServer(self, viewerParam, self.GDALprocess, tilingParam)
            else:
                self.appServer = AppServer(self, viewerParam)
            self.appServer.start()
            self.btn_generate.setText("Server is running")
            open_web_browser(self.get_port())
            self.appServerRunning = True

    ## Create all providers with the selected layers in the GUI
    def create_vector_providers(self):
        for row_index in range(self.tw_layers.rowCount()):
            # if the layer is checked
            if self.tw_layers.item(row_index, 0).checkState() == QtCore.Qt.Checked:
                vectorLayer = self.tw_layers.item(row_index, 1).data(QtCore.Qt.UserRole)
                connection_info = vt_utils_parser.parse_vector(vectorLayer.source())
                column2 = self.tw_layers.cellWidget(row_index, 2).currentText()
                if column2 == "None":
                    provider = PostgisProvider(**connection_info)
                else:
                    connection_info['column2'] = column2.split(" - ")[0]
                    connection_info['column2Type'] = column2.split(" - ")[1]
                    provider = PostgisProvider(**connection_info)
                ProviderManager.instance().add_vector_provider(provider)

    ## Create all providers for DEM and raster
    def create_raster_providers(self):
        dataSrcImg = None
        dataSrcMnt = None
        path = os.path.join(os.path.dirname(__file__), "rasters")
        extent = self.get_gui_extent()
        tileSize = self.get_size_tile()
        zoomLevel = self.cb_zoom.currentText()
        if self.has_dem():
            dem = self.cb_dem.itemData(self.cb_dem.currentIndex())
            demProvider = ProviderManager.instance().create_raster_provider(dem, self.get_port(), 'dem', str(tileSize), zoomLevel)
            ProviderManager.instance().dem = demProvider
            dataSrcMnt = demProvider.source
        if self.has_texture():
            texture = self.cb_texture.itemData(self.cb_texture.currentIndex())
            textureProvider = ProviderManager.instance().create_raster_provider(texture, self.get_port(), 'img', str(tileSize), zoomLevel)
            ProviderManager.instance().texture = textureProvider
            dataSrcImg = textureProvider.source
        if self.has_raster():
            if os.name is 'nt':
                pythonPath = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
                mp.set_executable(pythonPath)
                sys.argv = [None]
            self.GDALprocess = mp.Process(target=launch_gdal_process, args=(dataSrcImg, dataSrcMnt, path, extent, tileSize, int(zoomLevel)))
            self.GDALprocess.start()

    ## Behavior whit a close event
    #  @override QtGui.QDialog
    def closeEvent(self, QCloseEvent):
        if self.appServer:
            self.pb_loading.hide()
            self.btn_generate.setText("Server is stopping")
            self.appServer.stop()
            self.btn_generate.setText("Generate")
            self.appServerRunning = False
        if self.GDALprocess:
            GDALDialog = QtGui.QMessageBox()
            GDALDialog.setIcon(QtGui.QMessageBox.Warning)
            GDALDialog.setText("The tiling process is not complete. Would you like to run the process in background to use the generated tile later ?")
            GDALDialog.setStandardButtons(QtGui.QMessageBox.Discard | QtGui.QMessageBox.Save)
            ret = GDALDialog.exec_()
            if ret == QtGui.QMessageBox.Save:
                print "GDALprocess continue"
            if ret == QtGui.QMessageBox.Discard:
                self.kill_gdal_process()

    ## Kill GDAL process and remove unfinished tiled files
    def kill_gdal_process(self):
        if self.GDALprocess and self.GDALprocess.is_alive():
            self.GDALprocess.terminate()
            self.GDALprocess = None
            mergeSuffix = '_merge.tif'
            demLocation = os.path.join(os.path.dirname(__file__), 'rasters', os.path.basename(ProviderManager.instance().dem.httpResource))
            textureLocation = os.path.join(os.path.dirname(__file__), 'rasters', os.path.basename(ProviderManager.instance().texture.httpResource))
            print demLocation
            shutil.rmtree(demLocation, True)
            shutil.rmtree(textureLocation, True)
            try:
                os.remove(textureLocation + mergeSuffix)
                os.remove(demLocation + mergeSuffix)
            except OSError:
                pass
