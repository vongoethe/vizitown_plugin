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

from PyQt4 import QtCore

from vt_as_provider_manager import ProviderManager
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider


## Test if the ProviderManager class can be instantiated
# Test is the ProviderManager class can add a vector provider to the manager
class TestProviderManager(unittest.TestCase):
    def setUp(self):
        self.pm = ProviderManager.instance()

    def test_singleton(self):
        self.pm.vectors.append("test")
        self.assertEqual(ProviderManager.instance(), self.pm, "ProviderManager is not a singleton")


## Test if the PostgisProvider class can connect to a postGis database
# and if they can request the database
class TestPostgisProvider(unittest.TestCase):
    def setUp(self):
        self.host = "37.58.147.68"
        self.dbname = "data"
        self.port = 5432
        self.user = "lecture"
        self.password = "viziRead"
        self.srid = "2154"
        self.table = "test"
        self.column = "geom"
        self.color = "#000000"
        self.p = PostgisProvider(self.host, self.dbname, self.port, self.user, self.password, self.srid, self.table, self.column, self.color)

    def test_connection(self):
        assert self.p.db.open()

    def test_request(self):
        result = self.p.request_tile(0, 0, 50, 50)
        print result
        self.assertNotEqual(result, [], "Result empty")


## Test if the RasterProvider class can stock the attribute to use a raster resource
class TestRasterProvider(unittest.TestCase):
    def setUp(self):
        self.name = "test"
        self.extent = ""
        self.srid = "2154"
        self.source = "/sample/file"
        self.httpResource = "http://localhost/raster/file"
        self.p = RasterProvider(self.name, self.extent, self.srid, self.source, self.httpResource)

    def test_init(self):
        self.assertEqual(self.name, self.p.name, "RasterProvider init fail")
        self.assertEqual(self.extent, self.p.extent, "RasterProvider init fail")
        self.assertEqual(self.srid, self.p.srid, "RasterProvider init fail")
        self.assertEqual(self.source, self.p.source, "RasterProvider init fail")
        self.assertEqual(self.httpResource, self.p.httpResource, "RasterProvider init fail")

if __name__ == "__main__":
    unittest.main()
