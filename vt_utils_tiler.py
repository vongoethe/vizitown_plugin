import os
import math
import tempfile
import shutil
from osgeo import gdal
import gdal_retile
import gdal_merge
from PyQt4.QtCore import *

## TileGenerator Class manage Image and MNT to tile and dimension this.
class TileGenerator:

    ## The Constuctor with several parameter
    #  This constructor check the presence of the data and initialize the fields
    #  @param dataSrcImg the path of the image source
    #  @param dataSrcMnt the path of the mnt source
    #  @param path the path of the data destination
    #  @param extent the extent of the view
    #  @param tileSize to dimension and tile the data
    #  @param levels to define the several levels of zoom
    def __init__(self, dataSrcImg, dataSrcMnt, path, extent, tileSize=2048, levels=2):
        if path is None:
            raise Exception("Invalid path")
        self.dataDst = path
        self.tmpRepo = os.path.join(tempfile.gettempdir(), "vizitown")

        if dataSrcImg is not None:
            self.dataSrcImg = dataSrcImg
            self.dataDstImg = os.path.join(self.dataDst, "img_%s" % os.path.splitext(os.path.basename(dataSrcImg))[0])
            self.dataMergeImg = os.path.join(path, "img_%s_merge.tif" % os.path.splitext(os.path.basename(dataSrcImg))[0])

        if dataSrcMnt is not None:
            self.dataSrcMnt = dataSrcMnt
            self.dataDstMnt = os.path.join(self.dataDst, "mnt_%s" % os.path.splitext(os.path.basename(dataSrcMnt))[0])
            self.dataMergeMnt = os.path.join(path, "mnt_%s_merge.tif" % os.path.splitext(os.path.basename(dataSrcMnt))[0])

        self.tileSize = tileSize
        self.levels = levels
        self.extent = extent
        self.processChoice = self.__check_data(dataSrcImg, dataSrcMnt)

    ##  Getter of the data destination directory
    def __get_data_dst(self):
        return self.dataDst

    ## Setter of the data destination directory Image
    #  @param data the new image source
    def __set_data_src_img(self, data):
        self.dataSrcImg = data

    ## Setter of the data destination directory Mnt
    #  @param data the new mnt source
    def __set_data_src_mnt(self, data):
        self.dataSrcMnt = data

    ## Setter of the extent
    #  @param extent the new extent
    def __set_extent(self, extent):
        self.extent = extent

    ## __create_repositories method to create the several repositories
    def __create_repositories(self):
        if os.path.exists(self.tmpRepo):
            shutil.rmtree(self.tmpRepo)
        os.mkdir(self.tmpRepo)
        if hasattr(self, 'dataSrcImg'):
            os.mkdir(self.dataDstImg)
        if hasattr(self, 'dataSrcMnt'):
            os.mkdir(self.dataDstMnt)

    ## __check_data define the process to apply in function of the data instanciate
    #  @param dataSrcImg the path of the image source
    #  @param dataSrcMnt the path of the mnt source
    def __check_data(self, dataSrcImg, dataSrcMnt):
        if dataSrcImg is not None:
            if dataSrcMnt is not None:
                return 0
            else:
                return 1
        else:
            if dataSrcMnt is not None:
                return 2

    ## __calculate_extent calculate the extent and set it
    def __calculate_extent(self):
        xMin = float(self.extent[0])
        xMax = float(self.extent[1])
        yMin = float(self.extent[2])
        yMax = float(self.extent[3])

        distX = xMax - xMin
        distY = yMax - yMin

        factorX = math.ceil((xMax - xMin) / self.tileSize) * self.tileSize
        factorY = math.ceil((yMax - yMin) / self.tileSize) * self.tileSize

        self.__set_extent([xMin, xMin + factorX, yMax - factorY, yMax])

    ## __process_merge merge the image and mnt data with the new extent
    def __process_merge(self):
        uLX = str(self.extent[0])
        uLY = str(self.extent[3])
        lRX = str(self.extent[1])
        lRY = str(self.extent[2])

        if hasattr(self, 'dataSrcImg'):
            gdal_merge.main(["-init", "0", "-ul_lr", uLX, uLY, lRX, lRY, "-o", self.dataMergeImg, self.dataSrcImg])
            self.__set_data_src_img(self.dataMergeImg)

        if hasattr(self, 'dataSrcMnt'):
            gdal_merge.main(["-init", "0", "-separate", "-ul_lr", uLX, uLY, lRX, lRY, "-o", self.dataMergeMnt, self.dataSrcMnt])
            self.__set_data_src_mnt(self.dataMergeMnt)

    ##__process_tile_img create tiles and pyramid of this Image
    def __process_tile_img(self):
        reload(gdal_retile)
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", self.dataDstImg, self.dataSrcImg])

    ##__process_tile_mnt create tiles and pyramid of this Mnt
    def __process_tile_mnt(self):
        reload(gdal_retile)
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", self.dataDstMnt, self.dataSrcMnt])

    ##__process_pyramid_mnt create pyramid of this Mnt
    def __process_pyramid_mnt(self):
        reload(gdal_retile)
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-pyramidOnly",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", self.dataDstMnt, self.dataSrcMnt])

    ## __process_clip_mnt clip the mnt data with the image tile size
    #  and lauch the pyramid process
    #  @param dataImg the repository to stock the tile image source
    #  @param dataDirMnt the repository to stock the mnt data
    def __process_clip_mnt(self, dataImg, dataDirMnt):
        dataSourceListRepo = os.listdir(dataImg)
        for dataRepo in dataSourceListRepo:
            if (os.path.isdir(os.path.join(dataImg, dataRepo))):
                if not os.path.exists(os.path.join(dataDirMnt, dataRepo)):
                    os.mkdir(os.path.join(dataDirMnt, dataRepo))
                self.__process_clip_mnt(os.path.join(dataImg, dataRepo), os.path.join(dataDirMnt, dataRepo))

        for dataFile in dataSourceListRepo:
            if os.path.splitext(dataFile)[1] is "png":
                if not len(os.path.splitext(dataFile)) > 2:
                    ds = gdal.Open(os.path.join(dataImg, dataFile), gdal.GA_ReadOnly)
                    geoInfo = ds.GetGeoTransform()

                    optionsMnt = []
                    optionsMnt.append("-of Png -projwin %f %f %f %f" % (float(geoInfo[0]), float(geoInfo[3]),
                                      ((float(geoInfo[1]) * float(self.tileSize)) + float(geoInfo[0])),
                                      ((float(geoInfo[5]) * int(self.tileSize)) + float(geoInfo[3]))))
                    optionsMnt.append("%s %s" % (self.dataSrcMnt, os.path.join(dataDirMnt, "mnt%s" % dataFile[3:])))
                    cmdMnt = "gdal_translate " + " ".join(optionsMnt)
                    processMnt = QProcess()
                    processMnt.start(cmdMnt)
                    processMnt.waitForFinished()

    ## __process_to_dim_tile manage mnt and image tiles to fix this dimension
    #  @param dataTile the repository to find the data source
    #  @param dataDstDir the repository to stock the final data
    def __process_to_dim_tile(self, dataTile, dataDstDir):
        dataSourceListRepo = os.listdir(dataTile)

        for dataRepo in dataSourceListRepo:
            if (os.path.isdir(os.path.join(dataTile, dataRepo))):
                if not os.path.exists(os.path.join(dataDstDir, dataRepo)):
                    os.mkdir(os.path.join(dataDstDir, dataRepo))
                self.__process_to_dim_tile(os.path.join(dataTile, dataRepo), os.path.join(dataDstDir, dataRepo))

        for dataFile in dataSourceListRepo:
            if os.path.splitext(dataFile)[1] is "png":
                if not len(os.path.splitext(dataFile)) > 2:
                    ds = gdal.Open(os.path.join(dataTile, dataFile), gdal.GA_ReadOnly)
                    geoInfo = ds.GetGeoTransform()

                    if(ds.RasterXSize != int(self.tileSize) & ds.RasterYSize != int(self.tileSize)):
                        options = []
                        options.append("-of png -outsize %d %d" % (int(self.tileSize), int(self.tileSize)))
                        options.append("%s %s " % (os.path.join(dataTile, dataFile), os.path.join(dataDstDir, dataFile)))

                        cmd = "gdal_translate " + " ".join(options)
                        process = QProcess()
                        process.start(cmd)
                        process.waitForFinished()
                    else:
                        shutil.copy(os.path.join(dataTile, dataFile), os.path.join(dataDstDir, dataFile))
                        shutil.copy(os.path.join(dataTile, dataFile) + ".aux.xml", os.path.join(dataDstDir, dataFile) + ".aux.xml")

    ## __clean_up clean the temp repository
    def __clean_up(self):
        if hasattr(self, 'dataSrcImg'):
            shutil.copytree(os.path.join(self.tmpRepo, os.path.basename(self.dataDstImg)), self.dataDst)
        if hasattr(self, 'dataSrcMnt'):
            shutil.copytree(os.path.join(self.tmpRepo, os.path.basename(self.dataDstMnt)), self.dataDst)

    ## launch_process manage the several process to generate data tiles
    def launch_process(self):
        self.__create_repositories()
        self.__calculate_extent()
        self.__process_merge()
        if (self.processChoice == 0):
            self.__process_tile_img()
            self.__process_clip_mnt(self.dataDstImg, self.dataDstMnt)
            self.__process_to_dim_tile(self.dataDst, self.tmpRepo)
            self.__process_pyramid_mnt()
        elif (self.processChoice == 1):
            self.__process_tile_img()
            self.__process_to_dim_tile(self.dataDst, self.tmpRepo)
        elif (self.processChoice == 2):
            self.__process_tile_mnt()
            self.__process_to_dim_tile(self.dataDst, self.tmpRepo)
        self.__clean_up()
