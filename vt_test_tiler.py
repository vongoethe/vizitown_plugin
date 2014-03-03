import unittest
import datetime
import os
import shutil
from multiprocessing import Queue

from vt_utils_tiler import VTTiler, Extent

## Test is the VTTiler class apply process on image data
if __name__ == "__main__":
    originExtent = Extent(839724, 6511958, 861463, 6529147)
    sourceDem = 'MNT2009_Altitude_10m_RGF93.tif'
    sourceOrtho = 'GrandLyon2m_L93_RGB.tif'
    tiler = VTTiler(originExtent, 1024, 1, sourceDem, sourceOrtho)
    tiler.create('rasters', Queue())