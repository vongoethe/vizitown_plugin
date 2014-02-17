import json
from vt_utils_singleton import Singleton


## SyncManager
#  A singleton to store websockets who
#  want to be registered as listener of QGIS extent changes
@Singleton
class SyncManager:
    def __init__(self):
        self.websockets = []

    ## Record a websocket as listener for sync
    def add_listener(self, ws):
        self.websockets.append(ws)

    ## Delete a listener for sync
    def remove_all_listener(self):
        self.websockets = []

    ## Send new extent with all websockets stored
    def notify_extent_change(self, extent):
        for ws in self.websockets:
            ws.sendMessage(json.dumps(extent, separators=(',', ':')))
