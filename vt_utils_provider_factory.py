import os
import sys
import shutil
import multiprocessing as mp

from vt_utils_tiler import VTTiler, Extent
from vt_as_provider_manager import ProviderManager
from vt_utils_parameters import Parameters
from vt_as_provider_postgis import PostgisProvider
from vt_as_provider_raster import RasterProvider


class ProviderFactory():
    def __init__(self):
        self.providerManager = ProviderManager.instance()
        self.parameters = Parameters.instance()

    ## Create all providers with the selected layers in the GUI
    def create_vector_providers(self, arrayLayer):
        for layer in arrayLayer:
            layer.update_color()
            provider = PostgisProvider(layer)
            self.providerManager.add_vector_provider(provider)

    ## Create all providers for DEM and raster
    def create_raster_providers(self, dem, texture):
        dataSrcImg = None
        dataSrcMnt = None
        extent = self.parameters.extent
        originExtent = Extent(extent[0], extent[1], extent[2], extent[3])
        tileSize = self.parameters.tileSize
        zoomLevel = self.parameters.zoomLevel
        path = self.parameters.rastersPath
        if dem is not None:
            demProvider = RasterProvider(dem)
            dataSrcMnt = demProvider.source
            self.parameters.set_resources_dem(demProvider.httpResource)
            self.providerManager.dem = demProvider
        if texture is not None:
            textureProvider = RasterProvider(texture)
            dataSrcImg = textureProvider.source
            self.parameters.set_resources_texture(textureProvider.httpResource)
            self.providerManager.texture = textureProvider

        if os.name is 'nt':
            pythonPath = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
            mp.set_executable(pythonPath)
            sys.argv = [None]

        tiler = VTTiler(originExtent, tileSize, zoomLevel, dataSrcMnt, dataSrcImg)
        self.parameters.GDALprocess = mp.Process(target=tiler.create, args=(path, self.parameters.GDALqueue))
        self.parameters.GDALprocess.start()

    def clear_rasters_directory(self, path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                shutil.rmtree(os.path.join(root, name))
