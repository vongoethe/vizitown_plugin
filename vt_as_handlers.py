import json
import os
import gdal
import cyclone.websocket
from vt_utils_converter import PostgisToJSON
from vt_as_provider_manager import ProviderManager
from vt_as_sync import SyncManager


## A handler give initial parameters to the browser
class InitHandler(cyclone.web.RequestHandler):
    ## Method to initialize the handler
    def initialize(self, initParam):
        self.initParam = initParam

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    ## Handle GET HTTP
    def get(self):
        self.write(json.dumps(self.initParam, separators=(',', ':')))


## Data Handler
#  Use to handle the transmission of the data
#  retreived from postgis to the web browser
class DataHandler(cyclone.websocket.WebSocketHandler):
    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket data opened"

    ## Method call when a message is received
    #  Request all content in the extent specified in the message
    #  @param message in JSON format like:
    #  '{"Xmin": 0, "Ymin": 0, "Xmax": 50, "Ymax": 50}'
    def messageReceived(self, message):
        d = json.loads(message)
        vectors = ProviderManager.instance().request_tile(**d)
        if not vectors:
            self.sendMessage("{}")
            return
        translator = PostgisToJSON()
        for v in vectors:
            array = []
            while v['it'].next():
                if v['hasH']:
                    array.append([v['it'].value(0), v['it'].value(1)])
                else:
                    array.append(v['it'].value(0))

                if not v['it'].next():
                    break

            json_ = translator.parse(array, v['geom'], v['hasH'])
            array = []
            self.sendMessage(json_)

    ## Method call when the websocket is closed
    #  @param reason to indicate the reason of the closed instance
    def connectionLost(self, reason):
        print "WebSocket data closed"


## Synchronisation Handler
#  Use to handle the synchronisation of the view
#  from QGIS to the web browser
class SyncHandler(cyclone.websocket.WebSocketHandler):
    ## Method to initialize the handler
    def initialize(self):
        SyncManager.instance().add_listener(self)

    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket sync opened"

    ## Method call when a message is received
    #  @param message received
    def messageReceived(self, message):
        pass  # Do nothing, simplex communication

    ## Method call when the websocket is closed
    #  @param reason to indicate the reason of the closed instance
    def connectionLost(self, reason):
        print "WebSocket sync closed"

    def on_finish(self):
        print "WebSocket finished"
        SyncManager.instance().remove_listener(self)


## Tiles information handler
#  Use to give the information related to the tiles generated
#  when the GDAL tiling is finished
class TilesInfoHandler(cyclone.websocket.WebSocketHandler):

    ## Method to initialize the handler
    #  @param GDALprocess the process gdal 
    #  @param tilesInfo the dictionnary with the information about the data
    def initialize(self, GDALprocess, tilesInfo):
        self.GDALprocess = GDALprocess
        self.tilesInfo = tilesInfo

    ## Method call when the websocket is opened
    def connectionMade(self):
        print "Wait GDAL tiling ..."
        self.GDALprocess.join()
        print "Send tiles info ..."

        demPixelSize = {}
        demLocation = os.path.join(os.path.dirname(__file__), 'rasters', os.path.basename(ProviderManager.instance().dem.httpResource))
        demPixelSize = self._list_pixel_size(0, demPixelSize, demLocation)
        self.tilesInfo['demPixelSize'] = demPixelSize

        texturePixelSize = {}
        textureLocation = os.path.join(os.path.dirname(__file__), 'rasters', os.path.basename(ProviderManager.instance().texture.httpResource))
        texturePixelSize = self._list_pixel_size(0, texturePixelSize, textureLocation)
        self.tilesInfo['texturePixelSize'] = texturePixelSize

        self.sendMessage(json.dumps(self.tilesInfo, separators=(',', ':')))

    ## Method to add the level and the pixel size of image in function of the zoom levels
    #  @param index to indicate the zoom levels
    #  @param pixelSize the dictionnary initial
    #  @param path to indicate the data location
    #  @result the dictionnary with the several zoom levels and the pixel size
    def _list_pixel_size(self, index, pixelSize, path):
        listDir = os.listdir(path)

        for currentElem in listDir:
            if os.path.isdir(os.path.join(path, currentElem)):
                self._list_pixel_size(currentElem, pixelSize, os.path.join(path, currentElem))
            else:
                pixelSize[index] = self._get_pixel_size(os.path.join(path, currentElem))
                return pixelSize

    ## Method to get the pixel size in the image
    #  @param img to get the information
    #  @return the pixel size
    def _get_pixel_size(self, img):
        ds = gdal.Open(img, gdal.GA_ReadOnly)
        return ds.GetGeoTransform()[1]
