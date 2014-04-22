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

## classFactory load Vizitown class from file Vizitown
def classFactory(iface):
    from vizitown import Vizitown
    return Vizitown(iface)
