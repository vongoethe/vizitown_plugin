from vt_utils_singleton import Singleton


## Class ResultVTTiler
#  Singleton which contains one result of a tile generation
@Singleton
class ResultVTTiler:

    ## Constructor
    def __init__(self):
        self.pixelSize = None
        self.minHeight = None
        self.maxHeight = None

    ## set_result method
    #  Indicate the pixel size and if is a dem the min and max height value
    #  @param arrayR contains the several images
    def set_result(self, arrayR):
        if self.is_define():
            return
        else:
            self.pixelSize = arrayR[0]
            if len(arrayR) > 1:
                self.minHeight = arrayR[1]
                self.maxHeight = arrayR[2]

    ## is_define method
    #  Check if the pixel size is already define
    def is_define(self):
        if self.pixelSize is not None:
            return True
        else:
            return False

    ## is_dem method
    #  Check if the data is a data elevation model
    def is_dem(self):
        if self.is_define():
            if(self.minHeight is not None and
                    self.maxHeight is not None):
                return True
        return False
