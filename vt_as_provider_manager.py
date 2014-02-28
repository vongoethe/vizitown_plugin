import re

from vt_utils_singleton import Singleton
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider


## Provider manager
#  Singleton which contains several provider
@Singleton
class ProviderManager:

    ## Constructor
    def __init__(self):
        self.vectors = {}
        self.dem = None
        self.texture = None

    ## add_vector_provider method
    #  Add a vector provider to the manager
    #  @param p the provider to add
    def add_vector_provider(self, p):
        self.vectors[p._layer._uuid] = p

    ## request_tile method
    #  Request a tile for all his providers
    #  @param Xmin
    #  @param Ymin
    #  @param Xmax
    #  @param Ymax
    #  @param uuid
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

    ## clear method
    #  clean all field of the provider to the manager
    def clear(self):
        self.vectors = {}
        self.dem = None
        self.texture = None

    ## add_rasters method
    #  Add a raster in demProvider or in textureProvider to the manager
    #  @param demProvider
    #  @param textureProvider
    def add_rasters(self, demProvider=None, textureProvider=None):
        self.dem = demProvider
        self.texture = textureProvider

    ## get_all_vectors method
    #  Access to all vector in the provider
    #  @return a list with the vectors uuid and name
    def get_all_vectors(self):
        vectors = []
        for (uuid, p) in self.vectors.items():
            vectors.append({'uuid': uuid, 'name': p._layer._displayName})
        return vectors
