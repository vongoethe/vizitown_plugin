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
from multiprocessing import Queue
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
from vt_utils_provider_factory import ProviderFactory

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
        self.providerManager = ProviderManager.instance()
        self.zoomLevel = "1"

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
        for id, qgisLayer in layerListIems:
            if is_dem(qgisLayer):
                self.cb_dem.addItem(qgisLayer.name(), qgisLayer)

            if is_vector(qgisLayer):
                vLayer = Layer(qgisLayer)
                columnInfoLayer = PostgisProvider.get_columns_info_table(vLayer)
                item = QtGui.QTableWidgetItem(vLayer._displayName)
                item.setData(QtCore.Qt.UserRole, vLayer)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.add_vector_layer(item, columnInfoLayer)

            if is_texture(qgisLayer):
                self.cb_texture.addItem(qgisLayer.name(), qgisLayer)

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

    def has_vector(self):
        for row_index in range(self.tw_layers.rowCount()):
            if self.tw_layers.item(row_index, 0).checkState() == QtCore.Qt.Checked:
                return True
        return False

    def has_data(self):
        if self.has_raster() or self.has_vector():
            return True
        return False

    ## Add vector layer in QTableWidget
    #  @param item the new layer
    #  @param dic the dic with the fields and their types
    def add_vector_layer(self, item, columnInfoLayer):
        self.tw_layers.insertRow(0)
        checkBox = QtGui.QTableWidgetItem()
        checkBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkBox.setCheckState(QtCore.Qt.Unchecked)
        comboBox = QtGui.QComboBox()
        comboBox.addItem("None")
        for nameColumn, type in columnInfoLayer.items():
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
            return

        if not self.hasData:
            QtGui.QMessageBox.warning(self, "Warning", ("No data !"), QtGui.QMessageBox.Ok)
            return
        self.pb_loading.show()

        self.instantiate_providers()

        viewerParam = build_viewer_param(self.get_gui_extent(), str(self.sb_port.value()), self.has_raster())
        if self.has_raster():
            demResource = None
            textureResource = None
            if self.has_dem():
                demResource = self.providerManager.dem.httpResource
            if self.has_texture():
                textureResource = self.providerManager.texture.httpResource
            tilingParam = build_tiling_param(self.zoomLevel, self.get_size_tile(), demResource, textureResource)
            self.appServer = AppServer(self, viewerParam, self.GDALprocess, tilingParam, self.queue)
        else:
            self.appServer = AppServer(self, viewerParam)
        self.appServer.start()
        self.btn_generate.setText("Server is running")
        open_web_browser(self.sb_port.value())
        self.appServerRunning = True

    def instantiate_providers(self):
        factory = ProviderFactory()

    ## Calculate the width and the height in kilometers
    def calculate_size_extent(self):
        extent2 = self.get_gui_extent()
        width = extent2[2] - extent2[0]
        height = extent2[3] - extent2[1]
        self.lb_width.setValue(width / 1000)
        self.lb_height.setValue(height / 1000)

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
            self.providerManager.clear()

    def clear_rasters_directory(self, path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                shutil.rmtree(os.path.join(root, name))
