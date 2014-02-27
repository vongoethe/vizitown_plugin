import math
try:
    from osgeo import gdal
except:
    import gdal
from gdalconst import *
from multiprocessing import Queue
import os
import math
import sys


class Extent:
    def __init__(self, minX, minY, maxX, maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    def width(self):
        return self.maxX - self.minX

    def height(self):
        return self.maxY - self.minY


class Raster(object):
    def __init__(self, path, size, isDem=False):
        self.size = size
        self.basename = os.path.splitext(os.path.basename(os.path.abspath(path)))[0] + "_" + str(size) + "_1_{zoom}_{x}_{y}.png"
        self.dataSource = gdal.Open(path, GA_ReadOnly)
        self.geoTransform = self.dataSource.GetGeoTransform()
        self.isDem = isDem
        self.path = path

    ## formatRasterName format the name of the raster like this : nameWithoutExtension_zoomLevel_tileX_tileY
    #  @param tileZoomLevelthe zoomLevel of the tile
    #  @param tileX the X value of the tile
    #  @param tileY the Y value of the tile
    #  @return the new formatted name of the raster
    def rasterName(self, destDir, zoom, x, y):
        return destDir + os.sep + self.basename.format(zoom=zoom, x=x, y=y)

    def pixelSizeX(self):
        # GDAL constant specified in the API
        return self.geoTransform[1]

    def initialTileSize(self):
        return self.size * self.pixelSizeX()

    def pixelSizeXForSize(self, size):
        return size / float(self.size)

    ## demElevation provides the min and max data contained by the raster
    #  @return tuple (minimum value, maximum value)
    def demElevation(self):
        nBand = self.dataSource.RasterCount
        # suppose that there is only one band (e.g DEM)
        currentBand = self.dataSource.GetRasterBand(1)
        stats = currentBand.GetStatistics(True, True)
        # GDal constants
        return (stats[0], stats[1])

    ## getNbTilesByZoomLevel provides the number of tiles for each zoom level
    #  @param globalExtent the extent provided
    #  @param dicSizes a dictionnary of {zoomLevel : size of the tiles in meters for this zoom level}
    #  @return nbTilesByZoomLevel a dictionnary of {zoomLevel : number of tiles for this zoomLevel}
    def getNbTilesByZoomLevel(self, globalExtent, dicSizes):
        # origin = lower left
        extentWidth = globalExtent.width()
        extentHeight = globalExtent.height()

        nbTilesByZoomLevel = {}
        for zoomLevel in dicSizes.keys():
            # in meters
            sizeTile = dicSizes[zoomLevel]
            # tilewidth = tileHeight
            nbTilesX = math.ceil(float(extentWidth) / float(sizeTile))
            nbTilesY = math.ceil(float(extentHeight) / float(sizeTile))
            nbTilesByZoomLevel[zoomLevel] = nbTilesX * nbTilesY

        return nbTilesByZoomLevel

    def sizes(self, extent, zoomLevel):
        initialTileSize = self.initialTileSize()
        sizes = {}
        # First zoom level doesn't change the pixel size
        sizes[0] = self.initialTileSize()
        if (zoomLevel == 1):
            return sizes

        # Last zoom level covers the all area
        zoomInterval = zoomLevel - 1
        sizes[zoomInterval] = extent.width() if extent.width() > extent.height() else extent.height()
        if (zoomLevel == 2):
            return sizes

        # Create a step to go from minPixelSize to maxPixelSize
        # It will create intermidiate zoom level
        minPixelSize = pixelSizeXForSize(sizes['first'])
        maxPixelSize = pixelSizeXForSize(sizes['last'])
        pixelSizeStep = (maxPixelSize - minPixelSize) / zoomInterval

        for i in range(1, zoomInterval):
            sizes[i] = self.size * (minPixelSize + pixelSizeStep)

        return sizes

    def createForExtent(self, extent, outFilename):
        nBand = self.dataSource.RasterCount
        band = self.dataSource.GetRasterBand(1)
        # Dem don't have values between 0 and 255
        if (self.isDem):
            demElevation = self.demElevation()
            dfScale = (255 - 0) / (demElevation[1] - demElevation[0])
            dfOffset = -1 * demElevation[0] * dfScale
            band.SetScale(dfScale)
            band.SetOffset(dfOffset)

        pixelSizeX = self.pixelSizeXForSize(extent.width())
        pixelSizeY = self.pixelSizeXForSize(extent.height())
        newGeoTransform = (extent.minX, pixelSizeX, 0, extent.maxY, 0, -pixelSizeY)

        driver = gdal.GetDriverByName("MEM")
        dataDest = driver.Create('', self.size, self.size, nBand)
        dataDest.SetProjection(self.dataSource.GetProjectionRef())
        dataDest.SetGeoTransform(newGeoTransform)

        gdal.ReprojectImage(self.dataSource, dataDest)

        pngDriver = gdal.GetDriverByName("PNG")
        pngDriver.CreateCopy(outFilename, dataDest, 0)

    def createForSizes(self, extent, sizes, baseDestPath, tileSize, zoom):
        minX = extent.minX
        maxX = extent.maxX
        minY = extent.minY
        maxY = extent.maxY

        fileName = os.path.splitext(os.path.basename(self.path))[0] + "_" + str(tileSize) + "_" + str(zoom)
        destPath = os.path.join(baseDestPath, fileName)
        print "Destination folder:"
        print destPath
        os.mkdir(destPath)

        # Foreach zoom level
        for (zoom, size) in sizes.items():
            x = 0
            y = 0
            tileMinX = minX
            tileMinY = minY
            # foreach tile covering the extent
            while tileMinY < maxY:
                tileMaxY = tileMinY + size
                tileMinX = minX
                x = 0
                while tileMinX < maxX:
                    tileMaxX = tileMinX + size
                    outFilename = self.rasterName(destPath, zoom, x, y)
                    print outFilename
                    self.createForExtent(Extent(tileMinX, tileMinY, tileMaxX, tileMaxY), outFilename)
                    #Next x tile
                    x += 1
                    tileMinX += size
                #Next y tile
                y += 1
                tileMinY += size

    def alreadyCreated(self, baseDestPath, tileSize, zoom):
        fileName = os.path.splitext(os.path.basename(self.path))[0]
        destPath = os.path.join(baseDestPath, fileName + "_" + str(tileSize) + "_" + str(zoom))
        return os.path.exists(destPath)


class VTTiler(object):

    def __init__(self, extent, tileSize, zoom, dem=None, ortho=None):
        self.extent = extent
        self.tileSize = tileSize
        self.zoom = int(zoom)
        self.dem = dem
        self.ortho = ortho
        self.RDem = None
        self.ROrtho = None

    def create(self, baseDestPath, queue):
        sys.stderr = open(os.path.join(os.path.dirname(__file__), "GDAL_Process.err"), "w")
        sys.stdout = open(os.path.join(os.path.dirname(__file__), "GDAL_Process.out"), "w")
        if self.dem is not None and self.ortho is not None:
            self.ROrtho = Raster(self.ortho, self.tileSize)
            self.RDem = Raster(self.dem, self.tileSize, True)

            sizes = self.ROrtho.sizes(self.extent, self.zoom)
            if self.RDem.pixelSizeX() < self.ROrtho.pixelSizeX():
                sizes = self.RDem.sizes(self.extent, self.zoom)
            if not self.RDem.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                self.RDem.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)
            if not self.ROrtho.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                self.ROrtho.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)

            elevation = self.RDem.demElevation()
            queue.put([self.ROrtho.pixelSizeX(), elevation[0], elevation[1]])

        elif self.dem is not None:
            self.RDem = Raster(self.dem, self.tileSize, True)
            sizes = self.RDem.sizes(self.extent, self.zoom)
            if not self.RDem.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                self.RDem.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)

            elevation = self.RDem.demElevation()
            queue.put([self.RDem.pixelSizeX(), elevation[0], elevation[1]])

        elif self.ortho is not None:
            self.ROrtho = Raster(self.ortho, self.tileSize)
            sizes = self.ortho.sizes(self.extent)
            if not self.ROrtho.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                self.ROrtho.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)

            queue.put([self.ROrtho.pixelSizeX()])