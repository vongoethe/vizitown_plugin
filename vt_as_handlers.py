import json
import cyclone.websocket
from vt_utils_converter import X3DTranslateToThreeJs
from vt_as_providers import ProviderManager


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
        print message
        d = json.loads(message)
        vectors = ProviderManager.instance().requestTile(d['Xmin'], d['Ymin'], d['Xmax'], d['Ymax'])
        translator = X3DTranslateToThreeJs()
        for v in vectors:
            ## TODO: Maybe make a buffer
            while v['it'].next():
                print "sendmessage"
                result = str(v['it'].value(0).toString())
                json_ = translator.parse(result, v['geom'])
                self.sendMessage(json_)

    ## Method call when the websocket is closed
    def connectionLost(self, reason):
        print "WebSocket data closed"


## Synchronisation Handler
#  Use to handle the synchronisation of the view
#  from QGIS to the web browser
class SyncHandler(cyclone.websocket.WebSocketHandler):
    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket sync opened"

    ## Method call when a message is received
    def messageReceived(self, message):
        pass  # TODO

    ## Method call when the websocket is closed
    def connectionLost(self, reason):
        print "WebSocket sync closed"
