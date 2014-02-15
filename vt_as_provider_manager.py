import re

from vt_utils_singleton import Singleton
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider


## Provider manager
#  Singleton which contains several provider
@Singleton
class ProviderManager:
    def __init__(self):
        self.vectors = []
        self.dem = None
        self.texture = None

    ## Add a vector provider to the manager
    #  @param p the provider to add
    def add_vector_provider(self, p):
        self.vectors.append(p)

    ## Add a DEM raster provider to the manager
    #  @param p the provider to add
    def create_raster_provider(self, raster, port, tileSize, zoomLevel):
        httpResource = 'http://localhost:' + port + '/rasters/' + '_'.join(['img', raster.name(), tileSize, zoomLevel])
        return RasterProvider(raster.name(), raster.extent(), raster.crs().postgisSrid(), raster.source(), httpResource)

    ## Request a tile for all his providers
    def request_tile(self, Xmin, Ymin, Xmax, Ymax):
        result = []
        for p in self.vectors:
            result.append(p.request_tile(Xmin, Ymin, Xmax, Ymax))
        return result