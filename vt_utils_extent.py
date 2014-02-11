from qgis.gui import *


class extent(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def canvasPressEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        #Get the click
        xMin = self.canvas.extent().xMinimum()
        yMin = self.canvas.extent().yMinimum()
        xMax = self.canvas.extent().xMaximum()
        yMax = self.canvas.extent().yMaximum()
        print xMin
        print yMin
        print xMax
        print yMax

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
