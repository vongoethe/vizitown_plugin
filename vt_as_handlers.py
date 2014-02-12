from vt_utils_converter import X3DTranslateToThreeJs
import cyclone.websocket
import vt_as_providers


## Data Handler
#  Use to handle the transmission of the data
#  retreived from postgis to the web browser
class DataHandler(cyclone.websocket.WebSocketHandler):
    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket opened"

    ## Method call when a message is received
    #  Request all content in the extent specified in the message
    #  @param message in JSON format like:
    #  '{"Xmin": 0, "Ymin": 0, "Xmax": 50, "Ymax": 50}'
    def messageReceived(self, message):
        vectors = providers.ProviderManager.Instance().requestTile(*json.loads(message))
        translator = X3DTranslateToThreeJs()
        for v in vectors:
            ## TODO: Maybe make a buffer
            while v['it'].next():
                result = str(v['it'].value(0).toString())
                json_ = X3DTranslateToThreeJs().parse(result, v['geom'])
                self.sendMessage(json_)

    ## Method call when the websocket is closed
    def connectionLost(self):
        print "WebSocket closed"


## Synchronisation Handler
#  Use to handle the synchronisation of the view
#  from QGIS to the web browser
class SyncHandler(cyclone.websocket.WebSocketHandler):
    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket opened"

    ## Method call when a message is received
    def messageReceived(self, message):
        pass  # TODO

    ## Method call when the websocket is closed
    def connectionLost(self):
        print "WebSocket closed"
