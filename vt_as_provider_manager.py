import re

from vt_utils_singleton import Singleton
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider


## Provider manager
#  Singleton which contains several provider
@Singleton
class ProviderManager:

    ## The Constructor
    def __init__(self):
        self.vectors = {}
        self.dem = None
        self.texture = None

    ## Add a vector provider to the manager
    #  @param p the provider to add
    def add_vector_provider(self, p):
        self.vectors[p._layer._uuid] = p

    ## Create a raster provider to the manager
    #  @param raster add to the provider
    #  @param port to define the port of the connection
    #  @param tileSize indicate the size of the tile
    #  @param zoomLevel indicate the value of zoom levels
    #  @return a raster provider
    def create_raster_provider(self, raster, port, tileSize, zoomLevel):
        name = '_'.join([raster.name(), tileSize, zoomLevel])
        httpResource = 'http://localhost:' + port + '/rasters/' + name
        return RasterProvider(name, raster.extent(), raster.crs().postgisSrid(), raster.source(), httpResource)

    ## Request a tile for all his providers
    #  @param Xmin
    #  @param Ymin
    #  @param Xmax
    #  @param Ymax
    #  @return the tile
    def request_tile(self, Xmin, Ymin, Xmax, Ymax, uuid=None):
        result = []
        if uuid is not None:
            result.append(self.vectors[uuid].request_tile(Xmin, Ymin, Xmax, Ymax))
            return result

        for (uuid, p) in self.vectors.items():
            result.append(p.request_tile(Xmin, Ymin, Xmax, Ymax))
        return result