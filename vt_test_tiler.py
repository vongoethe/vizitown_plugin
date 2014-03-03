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
import unittest
import datetime
import os
import shutil

from vt_utils_tiler import VTTiler, Extent

## Test is the VTTiler class apply process on image data
if __name__ == "__main__":
    originExtent = Extent(839724, 6511958, 861463, 6529147)
    sourceDem = '/Users/Louis/Desktop/Data/Mnt/MNT2009_Altitude_10m_RGF93.tif'
    sourceOrtho = '/Users/Louis/Desktop/Data/GrandLyon_L93.png'
    tiler = VTTiler(originExtent, 4096, 1, sourceDem, None)
    tiler.create('/Users/Louis/Documents/Cours/3eme_Annee/Last_project/Vizitown_LP/DEV/GitAppServer/rasters')