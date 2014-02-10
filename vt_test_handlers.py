import cyclone.escape
import cyclone.web
import cyclone.websocket


class PingHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class EchoHandler(cyclone.websocket.WebSocketHandler):
    def connectionMade(self):
        print "WebSocket opened"

    def messageReceived(self, message):
        self.sendMessage(message)

    def connectionLost(self, reason):
        print "WebSocket closed"
