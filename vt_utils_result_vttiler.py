from vt_utils_singleton import Singleton


@Singleton
class ResultVTTiler:

    def __init__(self):
        self.pixelSize = None
        self.minHeight = None
        self.maxHeight = None

    def set_result(self, arrayR):
        if self.is_define():
            return
        else:
            self.pixelSize = arrayR[0]
            if len(arrayR) > 1:
                self.minHeight = arrayR[1]
                self.maxHeight = arrayR[2]

    def is_define(self):
        if self.pixelSize is not None:
            return True
        else:
            return False

    def is_dem(self):
        if self.is_define():
            if(self.minHeight is not None and
                    self.maxHeight is not None):
                return True
        return False
