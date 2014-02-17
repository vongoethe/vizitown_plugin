# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 ViziTown
                             -------------------
        begin                : 2014-02-03
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
 This script initializes the plugin, making it known to QGIS.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))


## classFactory load Vizitown class from file Vizitown
def classFactory(iface):
    from vizitown import Vizitown
    return Vizitown(iface)
