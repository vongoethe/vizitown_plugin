import os

from vt_utils_singleton import Singleton
from multiprocessing import Queue


@Singleton
class Parameters:
    def __init__(self):
        self.rastersPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "rasters")
        self.viewerPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "vt_viewer")
        self.GDALqueue = Queue()
        self.dem = None
        self.texture = None

    def set_viewer_param(self, extent, port, hasRaster):
        self.extent = extent
        self.port = port
        self.hasRaster = hasRaster

    ## Get the intial parameter to give at the app server
    def get_viewer_param(self):
        return {
            'extent': {
                'xMin': str(self.extent[0]),
                'yMin': str(self.extent[1]),
                'xMax': str(self.extent[2]),
                'yMax': str(self.extent[3]),
            },
            'port': self.port,
            'hasRaster': self.hasRaster,
            'vectors': self.all_uuids,
        }

    def set_resources_dem(self, dem):
        self.dem = dem
    
    def set_resources_texture(self, texture):
        self.texture = texture

    def set_all_uuids(self, arrayUuid):
        self.all_uuids = arrayUuid

    def set_tiling_param(self, zoomLevel, tileSize):
        self.zoomLevel = zoomLevel
        self.tileSize = tileSize

    ## Get the tiles info done by the process GDAL
    def get_tiling_param(self):
        return {
            'zoomLevel': self.zoomLevel,
            'tileSize': self.tileSize,
            'dem': self.dem,
            'texture': self.texture
        }
