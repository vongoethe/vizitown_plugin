import json
from vt_utils_singleton import Singleton


## SyncManager
#  A singleton to store websockets who
#  want to be registered as listener of QGIS extent changes
@Singleton
class SyncManager:
    def __init__(self):
        self.websockets = []

    ## add_listener method
    #  Record a websocket as listener for sync
    #  @param ws Web socket where the listener listen
    def add_listener(self, ws):
        self.websockets.append(ws)

    ## remove_all_listener mathod
    #  Delete a listener for sync
    def remove_all_listener(self):
        self.websockets = []

    ## notify_extent_change mathod
    #  Send new extent with all websockets stored
    #  @param extent the new extent to synchronized the view
    def notify_extent_change(self, extent):
        for ws in self.websockets:
            ws.sendMessage(json.dumps(extent, separators=(',', ':')))
