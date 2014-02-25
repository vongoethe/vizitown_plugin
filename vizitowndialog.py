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
from vt_as_sync import SyncManager
from vt_utils_layer import Layer


import vt_utils_parser
from vt_utils_tiler import VTTiler, Extent
from vt_utils_gui import *


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
        self.hasData = False
        self.zoomLevel = 1

    ## Set the default extent
    #  @param extent the extent to init the parameter
    def init_extent(self, extent):
        self.extent = extent
        self.set_limit_sb()
        self.le_xmin.setValue(extent.xMinimum())
        self.le_ymin.setValue(extent.yMinimum())
        self.le_xmax.setValue(extent.xMaximum())
        self.le_ymax.setValue(extent.yMaximum())
        self.calculate_size_extent()

    ## Set the limit of the doublespinbox in the tab extent
    def set_limit_sb(self):
        self.le_xmin.setMaximum(sys.maxint)
        self.le_xmin.setMinimum(-sys.maxint)
        self.le_ymin.setMaximum(sys.maxint)
        self.le_ymin.setMinimum(-sys.maxint)
        self.le_xmax.setMaximum(sys.maxint)
        self.le_xmax.setMinimum(-sys.maxint)
        self.le_ymax.setMaximum(sys.maxint)
        self.le_ymax.setMinimum(-sys.maxint)

    ## Set the values of the taile by default
    def init_tile_size(self):
        self.cb_tile.clear()
        self.cb_tile.addItem('256 x 256')
        self.cb_tile.addItem('512 x 512')
        self.cb_tile.addItem('1024 x 1024')
        self.cb_tile.addItem('2048 x 2048')
        self.cb_tile.addItem('4096 x 4096')
        self.cb_tile.setCurrentIndex(1)

    ## Init combobox and table layers
    def init_layers(self):
        self.reset_all_fields()
        layerListIems = QgsMapLayerRegistry().instance().mapLayers().items()
        for id, layer in layerListIems:
            if is_dem(layer):
                self.cb_dem.addItem(layer.name(), layer)
            if is_vector(layer):
                colorType = layer.rendererV2().type()
                srid = layer.crs().postgisSrid()
                d = vt_utils_parser.parse_vector(layer.source(), srid, colorType)
                vLayer = Layer(**d)
                dic = PostgisProvider.get_columns_info_table(vLayer)
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
        self.cb_dem.addItem("None")
        self.cb_texture.addItem("None")
        self.tw_layers.setRowCount(0)
        self.tw_layers.setColumnWidth(0, 45)
        self.tw_layers.setColumnWidth(1, 150)
        self.pb_loading.hide()

    ## Return true if there is a DEM to generate
    def has_dem(self):
        return self.cb_dem.currentIndex() != 0

    ## Return true if there is a texture to generate
    def has_texture(self):
        return self.cb_texture.currentIndex() != 0

    ## Return true if there is a least one raster to generate
    def has_raster(self):
        return self.has_dem() or self.has_texture()

    ## Add vector layer in QTableWidget
    #  @param item the new layer
    #  @param dic the dic with the fields and their types
    def add_vector_layer(self, item, dic):
        self.tw_layers.insertRow(0)
        checkBox = QtGui.QTableWidgetItem()
        checkBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkBox.setCheckState(QtCore.Qt.Unchecked)
        comboBox = QtGui.QComboBox()
        comboBox.addItem("None")
        for nameColumn, type in dic.items():
            comboBox.addItem(nameColumn + ' - ' + type)
        comboBox.model().sort(0)
        self.tw_layers.setItem(0, 0, checkBox)
        self.tw_layers.setItem(0, 1, item)
        self.tw_layers.setCellWidget(0, 2, comboBox)

    ## Get the size tile selected by the user
    #  @return the size tile
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

    ## Get the extent specified in the GUI or if the fields filled by the user are incoherent it's the extent of current view of QGIS
    #  @return the extent
    def get_gui_extent(self):
        xmin = self.le_xmin.value()
        xmax = self.le_xmax.value()
        ymin = self.le_ymin.value()
        ymax = self.le_ymax.value()
        if float(xmin) < float(xmax) and float(ymin) < float(ymax):
            return [float(xmin), float(ymin), float(xmax), float(ymax)]
        return [float(self.extent.xMinimum()), float(self.extent.yMinimum()), float(self.extent.xMaximum()), float(self.extent.yMaximum())]

    ## Set the tab advanced option by default
    #  @override QtGui.QDialog
    def on_btn_default_released(self):
        self.sb_port.setValue(8888)
        self.cb_tile.setCurrentIndex(1)
        self.tw_layers.clear()
        self.tw_layers.setHorizontalHeaderLabels(('Display', 'Layer', 'Field'))

    ## Generate and launch the rendering of the 3D scene
    def on_btn_generate_released(self):
        if self.appServerRunning:
            self.closeEvent(None)
        else:
            self.create_vector_providers()
            self.create_raster_providers()
            if not self.hasData:
                QtGui.QMessageBox.warning(self, "Warning", ("No data !"), QtGui.QMessageBox.Ok)
                return
            self.pb_loading.show()
            viewerParam = build_viewer_param(self.get_gui_extent(), str(self.sb_port.value()), self.has_raster())
            if self.has_raster():
                demResource = None
                textureResource = None
                if self.has_dem():
                    demResource = ProviderManager.instance().dem.httpResource
                if self.has_texture():
                    textureResource = ProviderManager.instance().texture.httpResource
                tilingParam = build_tiling_param(self.zoomLevel, self.get_size_tile(), demResource, textureResource)
                self.appServer = AppServer(self, viewerParam, self.GDALprocess, tilingParam)
            else:
                self.appServer = AppServer(self, viewerParam)
            self.appServer.start()
            self.btn_generate.setText("Server is running")
            open_web_browser(self.sb_port.value())
            self.appServerRunning = True

    ## Calculate the width and the height in kilometers
    def calculate_size_extent(self):
        extent2 = self.get_gui_extent()
        width = extent2[2] - extent2[0]
        height = extent2[3] - extent2[1]
        self.lb_width.setValue(width / 1000)
        self.lb_height.setValue(height / 1000)

    ## Create all providers with the selected layers in the GUI
    def create_vector_providers(self):
        for row_index in range(self.tw_layers.rowCount()):
            # if the layer is checked
            if self.tw_layers.item(row_index, 0).checkState() == QtCore.Qt.Checked:
                self.hasData = True
                vectorLayer = self.tw_layers.item(row_index, 1).data(QtCore.Qt.UserRole)

                colorType = vectorLayer.rendererV2().type()
                columnColor = get_column_color(vectorLayer)
                layerColor = get_color(vectorLayer)
                srid = vectorLayer.crs().postgisSrid()
                info = vt_utils_parser.parse_vector(vectorLayer.source(), srid, colorType)
                column2 = self.tw_layers.cellWidget(row_index, 2).currentText()

                if column2 == "None":
                    vLayer = Layer(**info)
                    vLayer.add_color(columnColor, layerColor)
                    provider = PostgisProvider(vLayer)
                else:
                    info['column2'] = column2.split(" - ")[0]
                    info['typeColumn2'] = column2.split(" - ")[1]
                    vLayer = Layer(**info)
                    vLayer.add_color(columnColor, layerColor)
                    provider = PostgisProvider(vLayer)
                ProviderManager.instance().add_vector_provider(provider)

    ## Create all providers for DEM and raster
    def create_raster_providers(self):
        dataSrcImg = None
        dataSrcMnt = None
        path = os.path.join(os.path.dirname(__file__), "rasters")
        extent = self.get_gui_extent()
        tileSize = self.get_size_tile()
        if self.has_dem():
            self.hasData = True
            dem = self.cb_dem.itemData(self.cb_dem.currentIndex())
            demProvider = ProviderManager.instance().create_raster_provider(dem, str(self.sb_port.value()), 'dem', str(tileSize), self.zoomLevel)
            ProviderManager.instance().dem = demProvider
            dataSrcMnt = demProvider.source
        if self.has_texture():
            self.hasData = True
            texture = self.cb_texture.itemData(self.cb_texture.currentIndex())
            textureProvider = ProviderManager.instance().create_raster_provider(texture, str(self.sb_port.value()), 'img', str(tileSize), self.zoomLevel)
            ProviderManager.instance().texture = textureProvider
            dataSrcImg = textureProvider.source
        if self.has_raster():
            if os.name is 'nt':
                pythonPath = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
                mp.set_executable(pythonPath)
                sys.argv = [None]
            originExtent = Extent(extent[0], extent[1], extent[2], extent[3])
            tiler = VTTiler(originExtent, tileSize, self.zoomLevel, dataSrcMnt, dataSrcImg)
            self.GDALprocess = mp.Process(target=tiler.create(path))
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
            SyncManager.instance().remove_all_listener()
        if self.GDALprocess and self.GDALprocess.is_alive():
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
            shutil.rmtree(demLocation, True)
            shutil.rmtree(textureLocation, True)
            try:
                os.remove(textureLocation + mergeSuffix)
                os.remove(demLocation + mergeSuffix)
            except OSError:
                pass
