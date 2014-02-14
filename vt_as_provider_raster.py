

## Raster provider
#  Stock the attribute to use a raster resource
class RasterProvider:

    ## Constructor
    #  @param name of the raster
    #  @param extent of the raster
    #  @param srid of the raster
    #  @param source local path of the raster
    #  @param httpResource URL location
    def __init__(self, name, extent, srid, source, httpResource):
        self.name = name
        self.extent = extent
        self.srid = srid
        self.source = source
        self.httpResource = httpResource