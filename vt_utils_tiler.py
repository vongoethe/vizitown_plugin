import os
import math
import tempfile
import shutil
import re
import subprocess
from osgeo import gdal
import gdal_retile
import gdal_merge


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
            self.dataDstImg = os.path.join(self.dataDst, "img_%s_%d_%d" % (os.path.splitext(os.path.basename(dataSrcImg))[0], tileSize, levels))
            self.dataMergeImg = os.path.join(path, "img_%s_%d_%d_merge.tif" % (os.path.splitext(os.path.basename(dataSrcImg))[0], tileSize, levels))

        if dataSrcMnt is not None:
            self.dataSrcMnt = dataSrcMnt
            self.dataDstMnt = os.path.join(self.dataDst, "dem_%s_%d_%d" % (os.path.splitext(os.path.basename(dataSrcMnt))[0], tileSize, levels))
            self.dataMergeMnt = os.path.join(path, "dem_%s_%d_%d_merge.tif" % (os.path.splitext(os.path.basename(dataSrcMnt))[0], tileSize, levels))

        self.gdalTranslate = 'gdal_translate'
        self.tileSize = tileSize
        self.levels = levels
        self.extent = extent
        self.processChoice = self._check_data(dataSrcImg, dataSrcMnt)
        print self.gdalTranslate

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
        yMin = float(self.extent[1])
        xMax = float(self.extent[2])
        yMax = float(self.extent[3])

        distX = xMax - xMin
        distY = yMax - yMin

        factorX = math.ceil((xMax - xMin) / self.tileSize) * self.tileSize
        factorY = math.ceil((yMax - yMin) / self.tileSize) * self.tileSize

        self.extent = [xMin, xMin + factorX, yMax - factorY, yMax]

    ## _process_merge merge the image and mnt data with the new extent
    def _process_merge(self):
        uLX = str(self.extent[0])
        lRX = str(self.extent[1])
        lRY = str(self.extent[2])
        uLY = str(self.extent[3])

        if hasattr(self, 'dataSrcImg'):
            gdal_merge.main(["-init", "0", "-ul_lr", uLX, uLY, lRX, lRY, "-o", self.dataMergeImg, self.dataSrcImg])
            self.dataSrcImg = self.dataMergeImg

        if hasattr(self, 'dataSrcMnt'):
            gdal_merge.main(["-init", "0", "-separate", "-ul_lr", uLX, uLY, lRX, lRY, "-o", self.dataMergeMnt, self.dataSrcMnt])
            self.dataSrcMnt = self.dataMergeMnt

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
    def _process_pyramid_mnt(self, pyramidDstDir):
        reload(gdal_retile)
        mntDirName = os.path.basename(os.path.normpath(self.dataDstMnt))
        gdal_retile.main(["-v",
                          "-of", "Png",
                          "-pyramidOnly",
                          "-levels", str(self.levels),
                          "-ps", str(self.tileSize), str(self.tileSize),
                          "-targetDir", os.path.join(self.tmpRepo, mntDirName), pyramidDstDir])

    ## _process_clip_mnt clip the mnt data with the image tile size
    #  @param dataImg the repository to stock the tile image source
    #  @param dirMnt the repository to stock the mnt data
    def _process_clip_mnt(self, dataImg, dirMnt):
        dataSourceListRepo = os.listdir(dataImg)
        for dataRepo in dataSourceListRepo:
            if (os.path.isdir(os.path.join(dataImg, dataRepo))):
                if not os.path.exists(os.path.join(dirMnt, dataRepo)):
                    os.mkdir(os.path.join(dirMnt, dataRepo))
                self._process_clip_mnt(os.path.join(dataImg, dataRepo), os.path.join(dirMnt, dataRepo))

        for currentFile in dataSourceListRepo:
            if re.search("png", currentFile) is not None:
                if re.search("png.", currentFile) is None:
                    ds = gdal.Open(os.path.join(dataImg, currentFile), gdal.GA_ReadOnly)
                    geoInfo = ds.GetGeoTransform()

                    index = len(os.path.basename(self.dataDstImg))
                    mntName = (os.path.basename(self.dataDstMnt)) + currentFile[index:]
                    mntDst = os.path.join(dirMnt, mntName)

                    optionsMnt = []
                    optionsMnt.append(self.gdalTranslate)
                    optionsMnt.append('-of')
                    optionsMnt.append('Png')
                    optionsMnt.append('-projwin')
                    optionsMnt.append(str(float(geoInfo[0])))
                    optionsMnt.append(str(float(geoInfo[3])))
                    optionsMnt.append(str(((float(geoInfo[1]) * float(self.tileSize)) + float(geoInfo[0]))))
                    optionsMnt.append(str(((float(geoInfo[5]) * int(self.tileSize)) + float(geoInfo[3]))))
                    optionsMnt.append(self.dataSrcMnt)
                    optionsMnt.append(mntDst)

                    print optionsMnt

                    if subprocess.mswindows:
                        info = subprocess.STARTUPINFO()
                        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        info.wShowWindow = subprocess.SW_HIDE
                        proc = subprocess.Popen(optionsMnt, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    else:
                        proc = subprocess.Popen(optionsMnt, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                    proc.wait()

    ## _process_to_dim_tile manage mnt and image tiles to fix this dimension
    #  @param dataTile the repository to find the data source
    #  @param dstDir the repository to stock the final data
    def _process_to_dim_tile(self, dataTile, dstDir):
        dataSourceListRepo = os.listdir(dataTile)
        for dataRepo in dataSourceListRepo:
            if (os.path.isdir(os.path.join(dataTile, dataRepo))):
                if not os.path.exists(os.path.join(dstDir, dataRepo)):
                    os.mkdir(os.path.join(dstDir, dataRepo))
                self._process_to_dim_tile(os.path.join(dataTile, dataRepo), os.path.join(dstDir, dataRepo))

        for currentFile in dataSourceListRepo:
            if re.search("png", currentFile) is not None:
                if re.search("png.", currentFile) is None:
                    if (self.processChoice == 1):
                        if re.search("dem_", currentFile) is not None:
                            self._process_pyramid_mnt(os.path.join(dstDir, currentFile))

                    ds = gdal.Open(os.path.join(dataTile, currentFile), gdal.GA_ReadOnly)

                    if(ds.RasterXSize != int(self.tileSize) or ds.RasterYSize != int(self.tileSize)):
                        options = []
                        options.append(self.gdalTranslate)
                        options.append('-of')
                        options.append("Png")
                        options.append('-outsize')
                        options.append(str(int(self.tileSize)))
                        options.append(str(int(self.tileSize)))
                        options.append(os.path.join(dataTile, currentFile))
                        options.append(os.path.join(dstDir, currentFile))

                        if subprocess.mswindows:
                            info = subprocess.STARTUPINFO()
                            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            info.wShowWindow = subprocess.SW_HIDE
                            proc = subprocess.Popen(options, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        else:
                            proc = subprocess.Popen(options, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                        proc.wait()
                    else:
                        shutil.copy(os.path.join(dataTile, currentFile), os.path.join(dstDir, currentFile))
                        shutil.copy(os.path.join(dataTile, currentFile) + ".aux.xml", os.path.join(dstDir, currentFile) + ".aux.xml")

    ## _clean_up clean the temp repository
    def _clean_up(self):
        if hasattr(self, 'dataSrcImg'):
            imgDirName = os.path.basename(os.path.normpath(self.dataDstImg))
            self._copytree(os.path.join(self.tmpRepo, imgDirName), os.path.join(self.dataDst, imgDirName))
            os.remove(self.dataSrcImg)
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

    ## _check_existing_dir verify if the tile generation is already make
    #  for this data, tile size and levels
    @staticmethod
    def _check_existing_dir(dataSrcImg, dataSrcMnt, path, tileSize, levels):
        if dataSrcImg is not None:
            dirImg = os.path.join(path, "img_%s_%d_%d" % (os.path.splitext(os.path.basename(dataSrcImg))[0], tileSize, levels))
            if dataSrcMnt is not None:
                dirMnt = os.path.join(path, "dem_%s_%d_%d" % (os.path.splitext(os.path.basename(dataSrcMnt))[0], tileSize, levels))
                if os.path.exists(dirImg) and os.path.exists(dirMnt):
                    return 0
            else:
                if os.path.exists(dirImg):
                    return 0
        else:
            if dataSrcMnt is not None:
                dirMnt = os.path.join(path, "dem_%s_%d_%d" % (os.path.splitext(os.path.basename(dataSrcMnt))[0], tileSize, levels))
                if os.path.exists(dirMnt):
                    return 0

    ## launch_process manage the several process to generate data tiles
    @staticmethod
    def launch_process(gdalPath, dataSrcImg, dataSrcMnt, path, extent, tileSize=512, levels=2):
        cwd = os.getcwd()
        if gdalPath != None:
            envval = unicode(os.getenv("PATH"))
            if not gdalPath.lower() in envval.lower().split(os.pathsep):
                envval += "%s%s" % (os.pathsep, gdalPath)
                os.putenv("PATH", envval)
                os.chdir(gdalPath)
        generator = TileGenerator(dataSrcImg, dataSrcMnt, path, extent, tileSize, levels)
        generator._create_repositories()
        generator._calculate_extent()
        generator._process_merge()
        if (generator.processChoice == 0):
            generator._process_tile_img()
            generator._process_clip_mnt(generator.dataDstImg, generator.dataDstMnt)
            generator._process_to_dim_tile(generator.dataDst, generator.tmpRepo)
        elif (generator.processChoice == 1):
            generator._process_tile_img()
            generator._process_to_dim_tile(generator.dataDst, generator.tmpRepo)
        elif (generator.processChoice == 2):
            generator._process_tile_mnt()
            generator._process_to_dim_tile(generator.dataDst, generator.tmpRepo)
        os.chdir(cwd)
        generator._clean_up()
