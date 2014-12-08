# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 QGIS Plugin for viewing data in 3D
                              -------------------
        begin                : 2014-02-03
        copyright            : (C) 2014 by Cubee(ESIPE)
        email                : lp_vizitown@googlegroups.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import math
import time
import numpy
try:
    from osgeo import gdal
    from osgeo.gdalconst import *
except:
    import gdal
    from gdalconst import *

from multiprocessing import Queue
import os
import sys


## Class Extent
#  Manage the extent
class Extent:

    ## Constructor
    #  @param minX
    #  @param minY
    #  @param maxX
    #  @param maxY
    def __init__(self, minX, minY, maxX, maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    ## width method
    #  Calculate the width of the extent
    #  @return the width
    def width(self):
        return self.maxX - self.minX

    ## height method
    #  Calculate the height of the extent
    #  @return the height
    def height(self):
        return self.maxY - self.minY


## Class Raster
#  Unherited object class
class Raster(object):

    ## Constructor
    #  @param path the path where the data are stock
    #  @param size the size of the tile
    #  @param isDem if a dem exists
    def __init__(self, path, size, isDem=False):
        self.size = size
        self.basename = os.path.splitext(os.path.basename(os.path.abspath(path)))[0] + "_" + str(size) + "_1_{zoom}_{x}_{y}.png"
        self.dataSource = gdal.Open(path, GA_ReadOnly)
        self.geoTransform = self.dataSource.GetGeoTransform()
        self.isDem = isDem
        self.path = path
        self.dem = None

    ## rasterName method
    #  Format the name of the raster like this : nameWithoutExtension_zoomLevel_tileX_tileY
    #  @param tileZoomLevelthe zoomLevel of the tile
    #  @param tileX the X value of the tile
    #  @param tileY the Y value of the tile
    #  @return the new formatted name of the raster
    def rasterName(self, destDir, zoom, x, y):
        return destDir + os.sep + self.basename.format(zoom=zoom, x=x, y=y)

    ## pixelSizeX method
    #  Get the X pixel size
    #  @return the x pixel size
    def pixelSizeX(self):
        # GDAL constant specified in the API
        return self.geoTransform[1]

    ## initialTileSize method
    #  Get the initial tile size
    #  @return the initial tile size
    def initialTileSize(self):
        return self.size * self.pixelSizeX()

    ## pixelSizeXForSize method
    #  Calculate the new pixel size
    #  @param size the size demand by the user
    #  @return the new pixel size
    def pixelSizeXForSize(self, size):
        return size / float(self.size)

    ## demElevation method
    #  Provides the min and max data contained by the raster
    #  @return tuple (minimum value, maximum value)
    def demElevation(self):
        nBand = self.dataSource.RasterCount
        # suppose that there is only one band (e.g DEM)
        currentBand = self.dataSource.GetRasterBand(1)
        stats = currentBand.GetStatistics(True, True)
        # GDal constants
        return (stats[0], stats[1])

    ## getNbTilesByZoomLevel method
    #  Provides the number of tiles for each zoom level
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

    ## sizes method
    #  Calculate the size of the pixel size for each zoom level
    #  @param extent the extent of the view
    #  @param zoomLevel the zoom level
    #  @return the array of pixel size for each zoom level
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

    def _normalizeDEM(self):
        nBand = self.dataSource.RasterCount
        demElevation = self.demElevation()
        scaleSrcMax = demElevation[1]
        scaleSrcMin = demElevation[0]
        scaleDstMax = 255.999
        scaleDstMin = 0.0

        data = self.dataSource.ReadAsArray(0, 0, self.dataSource.RasterXSize, self.dataSource.RasterYSize)
        data = ((scaleDstMax - scaleDstMin) * ((data - scaleSrcMin) / (scaleSrcMax - scaleSrcMin))) + scaleDstMin
        data = data.astype(numpy.uint8)

        driver = gdal.GetDriverByName("MEM")

        dem = driver.Create('', self.dataSource.RasterXSize, self.dataSource.RasterYSize, nBand, gdal.GDT_Byte)
        dem.SetProjection(self.dataSource.GetProjectionRef())
        dem.SetGeoTransform(self.dataSource.GetGeoTransform())

        for i in range(1, nBand + 1):
            dem.GetRasterBand(i).WriteArray(data)

        return dem

    ## createForExtent method
    #  Produce the tile of data about the extent and reproject it if necessary
    #  The result is png image
    #  @param extent the extent of the image
    #  @param outFilename the name of the tile
    def createForExtent(self, extent, outFilename):
        if (self.isDem):
            if self.dem is None:
                self.dem = self._normalizeDEM()
            self._createForExtent(self.dem, extent, outFilename)
        else:
            self._createForExtent(self.dataSource, extent, outFilename)

    ## createForExtent method
    #  Produce the tile of data about the extent and reproject it if necessary
    #  The result is png image
    #  @param extent the extent of the image
    #  @param outFilename the name of the tile
    def _createForExtent(self, ds, extent, outFilename):
        nBand = ds.RasterCount
        pixelSizeX = self.pixelSizeXForSize(extent.width())
        pixelSizeY = self.pixelSizeXForSize(extent.height())
        newGeoTransform = (extent.minX, pixelSizeX, 0, extent.maxY, 0, -pixelSizeY)

        driver = gdal.GetDriverByName("MEM")
        dataDest = driver.Create('', self.size, self.size, nBand, gdal.GDT_Byte)
        dataDest.SetProjection(ds.GetProjectionRef())
        dataDest.SetGeoTransform(newGeoTransform)

        gdal.ReprojectImage(ds, dataDest)

        pngDriver = gdal.GetDriverByName("PNG")
        pngDriver.CreateCopy(outFilename, dataDest, 0)

    ## createForSizes method
    #  Create data about the array of pixel size
    #  @param extent the extent to produce data
    #  @param sizes the array of pixel size to produce data
    #  @param baseDestPath the directory to stock the produce data
    #  @param tileSize the tile size of the data
    #  @param zoom the number of zoom level
    def createForSizes(self, extent, sizes, baseDestPath, tileSize, zoom):
        minX = extent.minX
        maxX = extent.maxX
        minY = extent.minY
        maxY = extent.maxY

        fileName = os.path.splitext(os.path.basename(self.path))[0] + "_" + str(tileSize) + "_" + str(zoom)
        destPath = os.path.join(baseDestPath, fileName)
        print "Destination folder:"
        print destPath
        if not os.path.isdir(destPath):
            os.makedirs(destPath)

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


## Class VTTiler
#  Produce the tile
#  Unherited object class
class VTTiler(object):

    ## Constructor
    #  @param extent the extent of the view
    #  @param tileSize the size of the tile
    #  @param zoom the zoom level to produce the data
    #  @param dem if a dem exists
    #  @param ortho if a ortho exists
    def __init__(self, extent, tileSize, zoom, dem=None, ortho=None):
        self.extent = extent
        self.tileSize = tileSize
        self.zoom = int(zoom)
        self.dem = dem
        self.ortho = ortho
        self.RDem = None
        self.ROrtho = None

    ## create method
    #  Produce the tile for the data exists
    #  @param baseDestPath the repository where the data is produce
    #  @param queue the list where the name of data is stock
    def create(self, baseDestPath, queue):
        sys.stderr = open(os.path.join(os.path.dirname(__file__), "GDAL_Process.err"), "w", 0)
        sys.stdout = open(os.path.join(os.path.dirname(__file__), "GDAL_Process.out"), "w", 0)

        if self.dem is not None and self.ortho is not None:
            self.ROrtho = Raster(self.ortho, self.tileSize)
            self.RDem = Raster(self.dem, self.tileSize, True)

            sizes = self.ROrtho.sizes(self.extent, self.zoom)
            if self.RDem.pixelSizeX() < self.ROrtho.pixelSizeX():
                sizes = self.RDem.sizes(self.extent, self.zoom)
            self.RDem.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)
            self.ROrtho.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)

            elevation = self.RDem.demElevation()
            queue.put([self.ROrtho.pixelSizeX(), elevation[0], elevation[1]])

        elif self.dem is not None:
            self.RDem = Raster(self.dem, self.tileSize, True)
            sizes = self.RDem.sizes(self.extent, self.zoom)
            self.RDem.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)

            elevation = self.RDem.demElevation()
            queue.put([self.RDem.pixelSizeX(), elevation[0], elevation[1]])

        elif self.ortho is not None:
            self.ROrtho = Raster(self.ortho, self.tileSize)
            sizes = self.ROrtho.sizes(self.extent, self.zoom)
            self.ROrtho.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)

            queue.put([self.ROrtho.pixelSizeX()])

        # Close log files
        sys.stderr.close()
        sys.stdout.close()

        # GDAL's readAsArray makes python crash when the script ends
        # We sleep so the calling process have time to kill us
        # Killing the process prevents the system from raising an error
        # about pythonw.exe crashing
        time.sleep(60000)
