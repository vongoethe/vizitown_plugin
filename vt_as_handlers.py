import json
import cyclone.websocket
from vt_utils_converter import PostgisToJSON
from vt_as_provider_manager import ProviderManager
from vt_as_sync import SyncManager


## A handler give initial parameters to the browser
class InitHandler(cyclone.web.RequestHandler):
    def initialize(self, initParam):
        self.initParam = initParam

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
        bufferSize = 100
        d = json.loads(message)
        vectors = ProviderManager.instance().request_tile(d['Xmin'], d['Ymin'], d['Xmax'], d['Ymax'])
        if not vectors:
            self.sendMessage("{}")
            return
        translator = PostgisToJSON()
        for v in vectors:
            ## TODO: Maybe make a buffer
            array = []
            while v['it'].next():
                # seconde boucle
                for i in range(bufferSize):
                    if v['hasH']:
                        array.append([v['it'].value(0), v['it'].value(1)])
                    else:
                        array.append(v['it'].value(0))

                    if not v['it'].next():
                        break

                json_ = translator.parse(array, v['geom'], v['hasH'])
                print "Send message"
                array = []
                self.sendMessage(json_)

    ## Method call when the websocket is closed
    def connectionLost(self, reason):
        print "WebSocket data closed"


## Synchronisation Handler
#  Use to handle the synchronisation of the view
#  from QGIS to the web browser
class SyncHandler(cyclone.websocket.WebSocketHandler):
    def initialize(self):
        SyncManager.instance().add_listener(self)

    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket sync opened"
        SyncManager.instance().isSocketOpen = True

    ## Method call when a message is received
    def messageReceived(self, message):
        pass  # Do nothing, simplex communication

    ## Method call when the websocket is closed
    def connectionLost(self, reason):
        print "WebSocket sync closed"
        SyncManager.instance().isSocketOpen = False


## Tiles information handler
#  Use to give the information related to the tiles generated
#  when the GDAL tiling is finished
class TilesInfoHandler(cyclone.websocket.WebSocketHandler):
    def initialize(self, GDALprocess, tilesInfo):
        self.GDALprocess = GDALprocess
        self.tilesInfo = tilesInfo

    ## Method call when the websocket is opened
    def connectionMade(self):
        print "Wait GDAL tiling ..."
        self.GDALprocess.join()
        print "Send tiles info ..."
        self.sendMessage(json.dumps(self.tilesInfo, separators=(',', ':')))
