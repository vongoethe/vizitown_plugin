import os
import math
import tempfile
import shutil

from osgeo import gdal
import gdal_retile
import gdal_merge
from PyQt4.QtCore import *


## TileGenerator
#  Manage Image and MNT to tile and dimension this.
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
        self.processChoice = self._check_data(dataSrcImg, dataSrcMnt)

    ##  Getter of the data destination directory
    def _get_data_dst(self):
        return self.dataDst

    ## Setter of the data destination directory Image
    #  @param data the new image source
    def _set_data_src_img(self, data):
        self.dataSrcImg = data

    ## Setter of the data destination directory Mnt
    #  @param data the new mnt source
    def _set_data_src_mnt(self, data):
        self.dataSrcMnt = data

    ## Setter of the extent
    #  @param extent the new extent
    def _set_extent(self, extent):
        self.extent = extent

    ## _create_repositories method to create the several repositories
    def _create_repositories(self):
        if os.path.exists(self.tmpRepo):
            shutil.rmtree(self.tmpRepo)
        os.mkdir(self.tmpRepo)
        if hasattr(self, 'dataSrcImg'):
            os.mkdir(self.dataDstImg)
        if hasattr(self, 'dataSrcMnt'):
            os.mkdir(self.dataDstMnt)

    ## _check_data define the process to apply in function of the data instanciate
    #  @param dataSrcImg the path of the image source
    #  @param dataSrcMnt the path of the mnt source
    def _check_data(self, dataSrcImg, dataSrcMnt):
        if dataSrcImg is not None:
            if dataSrcMnt is not None:
                return 0
            else:
                return 1
        else:
            if dataSrcMnt is not None:
                return 2

    ## _calculate_extent calculate the extent and set it
    def _calculate_extent(self):
        xMin = float(self.extent[0])
        xMax = float(self.extent[1])
        yMin = float(self.extent[2])
        yMax = float(self.extent[3])

        distX = xMax - xMin
        distY = yMax - yMin

        factorX = math.ceil((xMax - xMin) / self.tileSize) * self.tileSize
        factorY = math.ceil((yMax - yMin) / self.tileSize) * self.tileSize

        self._set_extent([xMin, xMin + factorX, yMax - factorY, yMax])

    ## _process_merge merge the image and mnt data with the new extent
    def _process_merge(self):
        uLX = str(self.extent[0])
        uLY = str(self.extent[3])
        lRX = str(self.extent[1])
        lRY = str(self.extent[2])

        if hasattr(self, 'dataSrcImg'):
            gdal_merge.main(["-init", "0", "-ul_lr", uLX, uLY, lRX, lRY, "-o", self.dataMergeImg, self.dataSrcImg])
            self._set_data_src_img(self.dataMergeImg)

        if hasattr(self, 'dataSrcMnt'):
            gdal_merge.main(["-init", "0", "-separate", "-ul_lr", uLX, uLY, lRX, lRY, "-o", self.dataMergeMnt, self.dataSrcMnt])
            self._set_data_src_mnt(self.dataMergeMnt)

    ##_process_tile_img create tiles and pyramid of this Image
    def _process_tile_img(self):
        reload(gdal_retile)
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", self.dataDstImg, self.dataSrcImg])

    ##_process_tile_mnt create tiles and pyramid of this Mnt
    def _process_tile_mnt(self):
        reload(gdal_retile)
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", self.dataDstMnt, self.dataSrcMnt])

    ##_process_pyramid_mnt create pyramid of this Mnt
    def _process_pyramid_mnt(self):
        reload(gdal_retile)
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-pyramidOnly",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", self.dataDstMnt, self.dataSrcMnt])

    ## _process_clip_mnt clip the mnt data with the image tile size
    #  and lauch the pyramid process
    #  @param dataImg the repository to stock the tile image source
    #  @param dataDirMnt the repository to stock the mnt data
    def _process_clip_mnt(self, dataImg, dataDirMnt):
        dataSourceListRepo = os.listdir(dataImg)
        for dataRepo in dataSourceListRepo:
            if (os.path.isdir(os.path.join(dataImg, dataRepo))):
                if not os.path.exists(os.path.join(dataDirMnt, dataRepo)):
                    os.mkdir(os.path.join(dataDirMnt, dataRepo))
                self._process_clip_mnt(os.path.join(dataImg, dataRepo), os.path.join(dataDirMnt, dataRepo))

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

    ## _process_to_dim_tile manage mnt and image tiles to fix this dimension
    #  @param dataTile the repository to find the data source
    #  @param dataDstDir the repository to stock the final data
    def _process_to_dim_tile(self, dataTile, dataDstDir):
        dataSourceListRepo = os.listdir(dataTile)

        for dataRepo in dataSourceListRepo:
            if (os.path.isdir(os.path.join(dataTile, dataRepo))):
                if not os.path.exists(os.path.join(dataDstDir, dataRepo)):
                    os.mkdir(os.path.join(dataDstDir, dataRepo))
                self._process_to_dim_tile(os.path.join(dataTile, dataRepo), os.path.join(dataDstDir, dataRepo))

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

    ## _clean_up clean the temp repository
    def _clean_up(self):
        if hasattr(self, 'dataSrcImg'):
            imgDirName = os.path.basename(os.path.normpath(self.dataDstImg))
            self._copytree(os.path.join(self.tmpRepo, imgDirName), os.path.join(self.dataDst, imgDirName))
        if hasattr(self, 'dataSrcMnt'):
            mntDirName = os.path.basename(os.path.normpath(self.dataDstMnt))
            self._copytree(os.path.join(self.tmpRepo, mntDirName), os.path.join(self.dataDst, mntDirName))

    ## _copytree method copy data with specifics actions
    #  Our implementation of copytree because standard cannot copy in an existing repository
    #  @param src source repository
    #  @param dst destination repository
    #  @param symlinks to symbolic file
    #  @param ignore to ignore data file
    def _copytree(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                self._copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    ## launch_process manage the several process to generate data tiles
    def launch_process(self):
        self._create_repositories()
        self._calculate_extent()
        self._process_merge()
        if (self.processChoice == 0):
            self._process_tile_img()
            self._process_clip_mnt(self.dataDstImg, self.dataDstMnt)
            self._process_to_dim_tile(self.dataDst, self.tmpRepo)
            self._process_pyramid_mnt()
        elif (self.processChoice == 1):
            self._process_tile_img()
            self._process_to_dim_tile(self.dataDst, self.tmpRepo)
        elif (self.processChoice == 2):
            self._process_tile_mnt()
            self._process_to_dim_tile(self.dataDst, self.tmpRepo)
        self._clean_up()
