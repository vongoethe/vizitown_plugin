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

    ## Request a tile for all his providers
    #  @param Xmin
    #  @param Ymin
    #  @param Xmax
    #  @param Ymax
    #  @return the tile
    def request_tile(self, Xmin, Ymin, Xmax, Ymax, uuid=None):
        result = []
        if uuid is not None:
            self.vectors[uuid]._layer.update_color()
            result.append(self.vectors[uuid].request_tile(Xmin, Ymin, Xmax, Ymax))
            return result

        for (uuid, p) in self.vectors.items():
            result.append(p.request_tile(Xmin, Ymin, Xmax, Ymax))
        return result

    def clear(self):
        self.vectors = {}
        self.dem = None
        self.texture = None

    def add_rasters(self, demProvider=None, textureProvider=None):
        self.dem = demProvider
        self.texture = textureProvider

    def get_all_uuids(self):
        return self.vectors.keys()
