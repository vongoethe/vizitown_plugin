import os
import math
import gdal
from gdalconst import *

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
    def clone(self):
        return Extent(self.minX, self.minY, self.maxX, self.maxY)
            
class Raster(object):
    def __init__(self, path, size):
        self.size = size
        self.path = path
        self.dataSource = gdal.Open(path, GA_ReadOnly)
        self.geoTransform = self.dataSource.GetGeoTransform()
    
    def pixelSizeX(self):
        # GDAL constant specified in the API
        return self.geoTransform[1];
    
    def initialTileSize (self):
        return self.size * self.pixelSizeX()
        
    def pixelSizeXForSize(self, size):
        print "pixel size", size, self.size, size / self.size
        return size / float(self.size)
            
    def sizes(self, extent, zoomLevel):
        initialTileSize = self.initialTileSize()
        sizes = {}
        sizes[0] = self.initialTileSize()
        if (zoomLevel == 1):
            return sizes
        
        zoomInterval = zoomLevel - 1
        sizes[zoomInterval] = extent.width() if extent.width() > extent.height() else extent.height()
        if (zoomLevel == 2):
            return sizes
            
        minPixelSize = pixelSizeXForSize(sizes['first'])
        maxPixelSize = pixelSizeXForSize(sizes['last'])
        
        pixelSizeStep = (maxPixelSize - minPixelSize) / zoomInterval
        for i in range(1, zoomInterval):
            sizes[i] = self.size * (minPixelSize + pixelSizeStep)
            
        return sizes
        
    def createForExtent(self, extent, destFile):

        nBand = self.dataSource.RasterCount
        band = self.dataSource.GetRasterBand(1)
        
        pixelSizeX = self.pixelSizeXForSize(extent.width())
        pixelSizeY = self.pixelSizeXForSize(extent.height())
        newGeoTransform = (extent.minX, pixelSizeX, 0, extent.maxY, 0, -pixelSizeY)
        
        print extent.width(), extent.height(), pixelSizeX, pixelSizeY
        
        driver = gdal.GetDriverByName("MEM")
        dataDest = driver.Create(destFile, self.size, self.size, nBand, band.DataType)
        dataDest.SetProjection(self.dataSource.GetProjectionRef())
        dataDest.SetGeoTransform(newGeoTransform)
        
        gdal.ReprojectImage(self.dataSource, dataDest)
        
        pngDriver = gdal.GetDriverByName("PNG")
        pngDriver.CreateCopy(destFile+".png", dataDest, 0)
     
    def createForSizes(self, extent, sizes, baseDestPath, tileSize, zoom):
        minX = extent.minX
        maxX = extent.maxX
        minY = extent.minY
        maxY = extent.maxY
        
        print "origin", minX, minY, maxX, maxY
        
        fileName = os.path.splitext(os.path.basename(self.path))[0]
        destPath = os.path.join(baseDestPath, fileName + "_" + str(tileSize) + "_" + str(zoom))
        print "Destination folder:"
        print destPath
        os.mkdir(destPath)
        baseDestFile = os.path.join(destPath, fileName)
        print baseDestFile
        for (zoom, size) in sizes.items():
            i = 0
            j = 0
            tileMinX = minX
            tileMinY = minY
            while tileMinY < maxY:
                tileMaxY = tileMinY + size
                while tileMinX < maxX:
                    tileMaxX = tileMinX + size
                    destFile = baseDestFile +"_"+str(zoom)+"_"+str(j)+"_"+str(i)+".tiff"
                    print "Destination file:"
                    print destFile
                    
                    print self.path, size, tileMinX, tileMinY, tileMaxX, tileMaxY
                    self.createForExtent(Extent(tileMinX, tileMinY, tileMaxX, tileMaxY), destFile)
                    
                    j += 1
                    tileMinX += size
                    
                i += 1
                tileMinY += size
    def alreadyCreated(self, baseDestPath, tileSize, zoom):
        fileName = os.path.splitext(os.path.basename(self.path))[0]
        destPath = os.path.join(baseDestPath, fileName + "_" + str(tileSize) + "_" + str(zoom))
        return os.path.exists(destPath)
                
class VTTiler(object):
    
    def __init__(self, extent, tileSize, zoom, dem=None, ortho=None):
        self.extent = extent
        self.tileSize = tileSize
        self.zoom = zoom
        self.dem = dem
        self.ortho = ortho
        
    def create (self, baseDestPath):
        if hasattr(self, "ortho") and hasattr(self, "dem"):
            ortho = Raster(self.ortho, self.tileSize)
            dem = Raster(self.dem, self.tileSize)

            sizes = ortho.sizes(self.extent, self.zoom)
            if dem.pixelSizeX() < ortho.pixelSizeX():
                sizes = dem.sizes(self.extent, self.zoom)
            if not dem.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                dem.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)
            if not ortho.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                ortho.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)
            return

        if hasattr(self, DEM):
            dem = Raster(self.dem, self.tileSize)
            sizes = dem.sizes(self.extent, self.zoom)
            if not dem.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                dem.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)
            return

        if hasattr(self, ORTHO):
            ortho = Raster(self.ortho, self.tileSize)
            sizes = self.ortho.sizes(self.extent, self.zoom)
            if not ortho.alreadyCreated(baseDestPath, self.tileSize, self.zoom):
                ortho.createForSizes(self.extent, sizes, baseDestPath, self.tileSize, self.zoom)
            return


if __name__ == "__main__":
    originExtent = Extent(828719, 6493848, 845000, 6520000)
    tiler = VTTiler(originExtent, 1024, 2, '/home/ctjhoa/.qgis2/python/plugins/pluginappserver/rasters/test/Mnt_L93.tiff', '/home/ctjhoa/.qgis2/python/plugins/pluginappserver/rasters/test/GrandLyon2m_L93_RGB.tif')
    tiler.create('/home/ctjhoa/.qgis2/python/plugins/pluginappserver/rasters')
