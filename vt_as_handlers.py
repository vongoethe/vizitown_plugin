import os
import json
import os
import cyclone.websocket
from multiprocessing import Queue
from vt_utils_converter import PostgisToJSON
from vt_as_provider_manager import ProviderManager
from vt_as_sync import SyncManager
from osgeo import gdal


## A static file handler which authorize cross origin
class CorsStaticFileHandler(cyclone.web.StaticFileHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')


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
    #  '{"Xmin": 0, "Ymin": 0, "Xmax": 50, "Ymax": 50}' for request all vectors
    #  '{"Xmin": 0, "Ymin": 0, "Xmax": 50, "Ymax": 50, uuid: "my_uuid"}' for a request only a specific vector
    def messageReceived(self, message):
        if message == "{}":
            return
        d = json.loads(message)
        vectors = ProviderManager.instance().request_tile(**d)
        if not vectors:
            self.sendMessage("{}")
            return
        translator = PostgisToJSON()
        for v in vectors:
            for i in range(len(v['results'])):
                if v['results'][i]:
                    json_ = translator.parse(v['results'][i], v['geom'], v['hasH'], v['color'][i], v['uuid'])
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
    def initialize(self, GDALprocess, tilesInfo, queue):
        self.GDALprocess = GDALprocess
        self.tilesInfo = tilesInfo
        self.queue = queue

    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket tiles_info opened"
        result = self.queue.get()
        if self.GDALprocess and self.GDALprocess.is_alive():
            print "Wait GDAL tiling ..."
            self.GDALprocess.join()
            print "Send tiles info ..."

        # Add pixel Size in JSON and Min/Max height if have dem
        if result:
            self.tilesInfo['pixelSize'] = result[0]
            if len(result) > 1:
                self.tilesInfo['minHeight'] = result[1]
                self.tilesInfo['maxHeight'] = result[2]

        js = json.dumps(self.tilesInfo, separators=(',', ':'))
        self.sendMessage(js)

    ## Method call when the websocket is closed
    #  @param reason to indicate the reason of the closed instance
    def connectionLost(self, reason):
        print "WebSocket tiles_info closed"

    ## Method to get the pixel size in the image
    #  @param img to get the information
    #  @return the pixel size
    def _get_pixel_size(self, img):
        ds = gdal.Open(img, gdal.GA_ReadOnly)
        return ds.GetGeoTransform()[1]
