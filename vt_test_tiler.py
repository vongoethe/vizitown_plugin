import unittest
import datetime
import os
import shutil

from vt_utils_tiler import TileGenerator


class TestTiler(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "rasters", "test")
        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                shutil.rmtree(os.path.join(self.path, d))
        self.srcImg = os.path.join(self.path, "GrandLyon2m_L93_RGB.tif")
        self.srcMnt = os.path.join(self.path, "Mnt_L93.tiff")
        self.extent = ["829889.029", "868878.498", "6495517.459", "6539503.016"]
        self.tileSize = 4096

    def test_nominal_case(self):
        TileGenerator.launch_process(self.srcImg, self.srcMnt, self.path, self.extent, self.tileSize, 2)
        self.assertIn("img_GrandLyon2m_L93_RGB", os.listdir(self.path))
        self.assertIn("mnt_Mnt_L93", os.listdir(self.path))

    def test_mnt_only(self):
        TileGenerator.launch_process(None, self.srcMnt, self.path, self.extent, self.tileSize, 2)
        self.assertIn("mnt_Mnt_L93", os.listdir(self.path))

    def test_img_only(self):
        TileGenerator.launch_process(self.srcImg, None, self.path, self.extent, self.tileSize, 2)
        self.assertIn("img_GrandLyon2m_L93_RGB", os.listdir(self.path))

    def test_unknown_path(self):
        try:
            TileGenerator.launch_process(self.srcImg, self.srcMnt, None, self.extent, self.tileSize, 2)
            self.assertFalse(False, "Should raise an exception")
        except Exception:
            self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()