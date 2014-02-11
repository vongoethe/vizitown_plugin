import json
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
        result = providers.ProviderManager.Instance().requestTile(*json.loads(message))
        self.sendMessage(json.dumps(result, separators=(',', ':')))

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
