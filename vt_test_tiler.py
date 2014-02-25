import unittest
import datetime
import os
import shutil

from vt_utils_tiler import VTTiler, Extent

if __name__ == "__main__":
    originExtent = Extent(839724, 6511958, 861463, 6529147)
    tiler = VTTiler(originExtent, 4096, 1, '/Users/Gui/Documents/Plugin_ViziTown/Data/Mnt_L93.tiff', '/Users/Gui/Documents/Plugin_ViziTown/Data/GrandLyon2m_L93_RGB.tif')
    tiler.create('/Users/Gui/.qgis2/python/plugins/pluginappserver/rasters/test')