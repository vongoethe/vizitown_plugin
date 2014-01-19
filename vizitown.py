# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 2D to 3D
                              -------------------
        begin                : 2014-01-09
        copyright            : (C) 2014 by Cubee
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

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
import vt_as_app
from vizitowndialog import VizitownDialog



class Vizitown:

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
        self.dlg = VizitownDialog()

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

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&ViziTown", self.action)
        self.iface.removeToolBarIcon(self.action)
        # run method that performs all the real work

    def info(self):
        xMin = self.iface.mapCanvas().extent().xMinimum()
        yMin = self.iface.mapCanvas().extent().yMinimum()
        xMax = self.iface.mapCanvas().extent().xMaximum()
        yMax = self.iface.mapCanvas().extent().yMaximum()

    def run(self): 
        dialog = self.dlg
        dialog.initExtent(self.iface.mapCanvas().extent())
        dialog.loadLayers()
        # dialog.getExtent(self.iface.mapCanvas())
        QObject.connect(self.iface.mapCanvas(), SIGNAL("extentsChanged()"), self.info)
        # show the dialog
        self.dlg.show()
