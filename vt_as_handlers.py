import json
import cyclone.websocket
import vt_as_providers
        
class BaseHandler(cyclone.websocket.WebSocketHandler):
    @property
    def db(self):
        return self.application.db


class DataHandler(BaseHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        result = providers.ProviderManager.Instance().requestTile(*json.loads(message))
        self.write_message(json.dumps(result, separators=(',', ':')))

    def on_close(self):
        print "WebSocket closed"


class SyncHandler(BaseHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        pass  # TODO

    def on_close(self):
        print "WebSocket closed"
