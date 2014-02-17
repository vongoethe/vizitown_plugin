import unittest

from PyQt4 import QtCore

from vt_as_provider_manager import ProviderManager
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider


class TestProviderManager(unittest.TestCase):
    def setUp(self):
        self.pm = ProviderManager.instance()

    def test_singleton(self):
        self.pm.vectors.append("test")
        self.assertEqual(ProviderManager.instance(), self.pm, "ProviderManager is not a singleton")


class TestPostgisProvider(unittest.TestCase):
    def setUp(self):
        self.host = "37.58.147.68"
        self.dbname = "data"
        self.user = "lecture"
        self.password = "viziRead"
        self.srid = "2154"
        self.table = "test"
        self.column = "geom"
        self.p = PostgisProvider(self.host, self.dbname, self.user, self.password, self.srid, self.table, self.column)

    def test_connection(self):
        assert self.p.db.open()

    def test_request(self):
        result = self.p.request_tile(0, 0, 50, 50)
        print result
        self.assertNotEqual(result, [], "Result empty")


class TestRasterProvider(unittest.TestCase):
    def setUp(self):
        self.name = "test"
        self.extent = ""
        self.srid = "2154"
        self.source = "/sample/file"
        self.httpRessource = "http://localhost/raster/file"
        self.p = RasterProvider(self.name, self.extent, self.srid, self.source, self.httpRessource)

    def test_init(self):
        self.assertEqual(self.name, self.p.name, "RasterProvider init fail")
        self.assertEqual(self.extent, self.p.extent, "RasterProvider init fail")
        self.assertEqual(self.srid, self.p.srid, "RasterProvider init fail")
        self.assertEqual(self.source, self.p.source, "RasterProvider init fail")
        self.assertEqual(self.httpRessource, self.p.httpRessource, "RasterProvider init fail")

if __name__ == "__main__":
    app = QtCore.QCoreApplication([])
    unittest.main()
    app.exec_()
