import os

from vt_utils_singleton import Singleton
from multiprocessing import Queue


## Class Parameters
#  Singleton which define the parameters
@Singleton
class Parameters:

    ## Constructor
    def __init__(self):
        self.rastersPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "rasters")
        self.viewerPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "vt_viewer")
        self.GDALqueue = Queue()
        self.dem = None
        self.texture = None
        self.GDALprocess = None

    ## set_viewer_param method
    #  Define the parameters of the viewer at the launch of this
    #  @param extent the initial extent
    #  @param port the port to launch the app server
    #  @param hasRaster to indicate if the raster exists
    def set_viewer_param(self, extent, port, hasRaster):
        self.extent = extent
        self.port = port
        self.hasRaster = hasRaster

    ## get_viewer_param method
    #  Get the intial parameter to give at the app server
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
            'vectors': self.all_vectors,
        }

    ## set_resources_dem method
    #  Define the data elevation model
    #  @param dem the new dem
    def set_resources_dem(self, dem):
        self.dem = dem

    ## set_resources_texture method
    #  Define the texture
    #  @param texture the new texture
    def set_resources_texture(self, texture):
        self.texture = texture

    ## set_all_vectors method
    #  Define the data elevation model
    #  @param arrayVectors the array of vectors
    def set_all_vectors(self, arrayVectors):
        self.all_vectors = arrayVectors

    ## set_tiling_param method
    #  Define the parameters of the tiles
    #  @param zoomLevel the zoom level of the tile
    #  @param tileSize the tile size of the tile in pixel
    def set_tiling_param(self, zoomLevel, tileSize):
        self.zoomLevel = zoomLevel
        self.tileSize = tileSize

    ## get_tiling_param method
    #  Get the tiles info done by the process GDAL
    def get_tiling_param(self):
        return {
            'zoomLevel': self.zoomLevel,
            'tileSize': self.tileSize,
            'dem': self.dem,
            'texture': self.texture
        }

    ## clear method
    #  Clean the value of the parameters
    def clear(self):
        self.dem = None
        self.texture = None
        self.extent = None
        self.port = None
        self.hasRaster = None
        self.all_vectors = None
        self.zommLevel = None
        self.tileSize = None
        if self.GDALprocess and self.GDALprocess.is_alive():
            self.GDALprocess.terminate()
