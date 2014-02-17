import cyclone.escape
import cyclone.web
import cyclone.websocket


## Ping handler
#  Basic HTTP request handler which return "pong"
#  to a GET HTTP
class PingHandler(cyclone.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    ## Handle GET HTTP
    def get(self):
        self.write("Hello, world")


## Echo handler
#  Basic HTTP request handler which return "pong"
#  to a GET HTTP
class EchoHandler(cyclone.websocket.WebSocketHandler):
    ## Method call when the websocket is opened
    def connectionMade(self):
        print "WebSocket opened"

    ## Method call when a message is received
    #  Return the message content to the sender
    def messageReceived(self, message):
        self.sendMessage(message)

    ## Method call when the websocket is closed
    def connectionLost(self, reason):
        print "WebSocket closed"
