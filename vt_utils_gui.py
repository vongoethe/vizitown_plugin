import webbrowser

from qgis.core import *
from qgis.gui import *


## Return True if the layer is a Raster which come from a database
def is_raster(layer):
    return layer.type() == QgsMapLayer.RasterLayer and layer.providerType() == "gdal" and not layer.source().startswith('dbname')


## Return True if the layer is a Data Elevation Model which come from a database
def is_dem(layer):
    return is_raster(layer) and layer.bandCount() == 1


## Return True if the layer is a Texture which come from a database
def is_texture(layer):
    return is_raster(layer) and layer.bandCount() == 3


## Return True if the layer is a Vector which come from a database
def is_vector(layer):
    return layer.type() == QgsMapLayer.VectorLayer and layer.source().startswith('dbname')


## Get the intial parameter to give at the app server
def build_viewer_param(extent, port, hasRaster):
    return {
        'extent': {
            'xMin': "%.4f" % extent[0],
            'yMin': "%.4f" % extent[1],
            'xMax': "%.4f" % extent[2],
            'yMax': "%.4f" % extent[3],
        },
        'port': port,
        'hasRaster': hasRaster,
    }


## Get the tiles info done by the process GDAL
def build_tiling_param(zoomLevel, tileSize, dem, texture):
    return {
        'zoomLevel': zoomLevel,
        'tileSize': tileSize,
        'dem': dem,
        'texture': texture
    }


## Open a web browser at localhost address
def open_web_browser(port):
    url = 'http://localhost:' + str(port)
    webbrowser.open(url)
