from qgis.core import *
from qgis.gui import *


## is_raster method
#  Check if the layer is a Raster which come from a database
#  @param layer
#  @return True if the layer is a Raster which come from a database
def is_raster(layer):
    return layer.type() == QgsMapLayer.RasterLayer and layer.providerType() == "gdal" and not layer.source().startswith('dbname')


## is_dem method
#  Check if the layer is a Data Elevation Model which come from a database
#  @param layer
#  @return True if the layer is a Data Elevation Model which come from a database
def is_dem(layer):
    return is_raster(layer) and layer.bandCount() == 1


## is_texture method
#  Check if the layer is a Texture which come from a database
#  @param layer
#  @return True if the layer is a Texture which come from a database
def is_texture(layer):
    return is_raster(layer) and layer.bandCount() >= 3


## is_vector method
#  Check if the layer is a Vector which come from a database
#  @param layer
#  @return True if the layer is a Vector which come from a database
def is_vector(layer):
    return layer.type() == QgsMapLayer.VectorLayer and layer.source().startswith('dbname')
