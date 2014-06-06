# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 QGIS Plugin for viewing data in 3D
                              -------------------
        begin                : 2014-02-03
        copyright            : (C) 2014 by Cubee(ESIPE)
        email                : lp_vizitown@googlegroups.com
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
import sys
import subprocess
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

# add the current directory to the system include path
# this way local versions of python modules are loaded insted of the system ones

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
import vt_as_app
from vizitowndialog import VizitownDialog
from vt_as_sync import SyncManager


## Class Vizitown
#  This class manage the plugin in QGIS and instanciate the service
class Vizitown:

    ## Constructor
    #  Initialize the plugin interface and load it in QGIS.
    #  Create the reference between the canvas and the plugin to dialog
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'vizitown_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        # Create the dialog (after translation) and keep reference
        self.dlg = VizitownDialog(iface.mapCanvas().extent())
        QObject.connect(iface.mapCanvas(), SIGNAL("extentsChanged()"), self.info)
        QObject.connect(self.dlg.le_xmin, SIGNAL("valueChanged(double)"), self.dlg.calculate_size_extent)
        QObject.connect(self.dlg.le_ymin, SIGNAL("valueChanged(double)"), self.dlg.calculate_size_extent)
        QObject.connect(self.dlg.le_xmax, SIGNAL("valueChanged(double)"), self.dlg.calculate_size_extent)
        QObject.connect(self.dlg.le_ymax, SIGNAL("valueChanged(double)"), self.dlg.calculate_size_extent)

    ## initGui method
    #  Integrate the plugin starter and button in the Qgis Menu
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/vizitown/vt.png"),
            u"Des données en 3D", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&ViziTown", self.action)

    ## unload method
    #  Remove the plugin of the Qgis Menu
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&ViziTown", self.action)
        self.iface.removeToolBarIcon(self.action)
        # run method that performs all the real work

    ## info method
    #  Sent the extent of QGIS.
    #  Enables synchronization between the viewer and qgis
    def info(self):
        self.dlg.init_extent(self.iface.mapCanvas().extent())
        xMin = self.iface.mapCanvas().extent().xMinimum()
        yMin = self.iface.mapCanvas().extent().yMinimum()
        xMax = self.iface.mapCanvas().extent().xMaximum()
        yMax = self.iface.mapCanvas().extent().yMaximum()
        extent = {
            'Xmin': xMin,
            'Ymin': yMin,
            'Xmax': xMax,
            'Ymax': yMax,
        }
        SyncManager.instance().notify_extent_change(extent)

    ## run method
    #  Launch the plugin and initialize the value of fields.
    def run(self):
        self.dlg.init_extent(self.iface.mapCanvas().extent())
        self.dlg.init_tile_size()
        self.dlg.init_layers()
        self.dlg.sb_port.setValue(8888)
        self.dlg.tabWidget.setCurrentIndex(0)
        # show the dialog
        self.dlg.show()
