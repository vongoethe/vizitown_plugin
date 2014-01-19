import unittest
import datetime
import os

from vt_utils_tiler import TileGenerator


class TestTiler(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "rasters", "test")
        self.srcImg = os.path.join(self.path, "GrandLyon2m_L93_RGB.tif")
        self.srcMnt = os.path.join(self.path, "Mnt_L93.tiff")
        self.extent = ["829889.029", "868878.498", "6495517.459", "6539503.016"]
        self.tileSize = 4096
        print self.srcImg

    def test_nominal_case(self):
        testNominal = TileGenerator(self.srcImg, self.srcMnt, self.path, self.extent, self.tileSize, 2)
        print testNominal
        testNominal.launch_process()

    # def test_mnt_only(self):
    #     testNominal = TileGenerator(None, self.srcMnt, self.path, self.extent, self.tileSize, 2)
    #     testNominal.launch_process()

    # def test_img_only(self):
    #     testNominal = TileGenerator(self.srcImg, None, self.path, self.extent, self.tileSize, 2)
    #     testNominal.launch_process()

    # def test_unknown_path(self):
    #     testNominal = TileGenerator(self.srcImg, self.srcMnt, None, self.extent, self.tileSize, 2)
    #     testNominal.launch_process()

if __name__ == "__main__":
    unittest.main()
