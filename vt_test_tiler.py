import unittest
import datetime
import os
import shutil

from vt_utils_tiler import VTTiler, Extent

if __name__ == "__main__":
    originExtent = Extent(839724, 6511958, 861463, 6529147)
    sourceDem = '/Users/Louis/Desktop/Data/Mnt/MNT2009_Altitude_10m_RGF93.tif'
    sourceOrtho = '/Users/Louis/Desktop/Data/GrandLyon_L93.png'
    tiler = VTTiler(originExtent, 4096, 1, sourceDem, sourceOrtho)
    tiler.create('/Users/Louis/Documents/Cours/3eme_Annee/Last_project/Vizitown_LP/DEV/GitAppServer/rasters')