import json
import cyclone.websocket
import vt_as_providers


class DataHandler(cyclone.websocket.WebSocketHandler):
    def connectionMade(self):
        print "WebSocket opened"

    def messageReceived(self, message):
        result = providers.ProviderManager.Instance().requestTile(*json.loads(message))
        self.sendMessage(json.dumps(result, separators=(',', ':')))

    def connectionLost(self):
        print "WebSocket closed"


class SyncHandler(cyclone.websocket.WebSocketHandler):
    def connectionMade(self):
        print "WebSocket opened"

    def messageReceived(self, message):
        pass  # TODO

    def connectionLost(self):
        print "WebSocket closed"
