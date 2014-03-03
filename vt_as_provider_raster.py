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
from vt_utils_parameters import Parameters


## Raster provider
#  Stock the attribute to use a raster resource
class RasterProvider:

    ## Constructor
    #  @param raster A Qgsmaplayer
    def __init__(self, raster):
        parameters = Parameters.instance()
        self.name = '_'.join([raster.name(), str(parameters.tileSize), parameters.zoomLevel])
        self.extent = raster.extent()
        self.srid = raster.crs().postgisSrid()
        self.source = raster.source()
        self.httpResource = 'http://localhost:' + str(Parameters.instance().port) + '/rasters/' + self.name
