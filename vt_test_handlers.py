import cyclone.escape
import cyclone.web
import cyclone.websocket


## Ping handler
#  Basic HTTP request handler which return "pong"
#  to a GET HTTP
class PingHandler(cyclone.web.RequestHandler):
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
