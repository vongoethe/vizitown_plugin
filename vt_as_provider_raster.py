from vt_utils_parameters import Parameters


## Raster provider
#  Stock the attribute to use a raster resource
class RasterProvider:

    ## Constructor
    #  @param raster A Qgsmaplayer
    def __init__(self, raster):
        parameters = Parameters.instance()
        self.name = '_'.join([raster.name(), parameters.tileSize, parameters.zoomLevel])
        self.extent = raster.extent()
        self.srid = raster.crs().postgisSrid()
        self.source = raster.source()
        self.httpResource = 'http://localhost:' + Parameters.instance().port + '/rasters/' + self.name
