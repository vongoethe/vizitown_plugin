# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 QGIS Plugin for viewing data in 3D
                              -------------------
        begin                : 2014-02-03
        copyright            : (C) 2014 by Cubee(ESIPE)
        email                : lp_vizitown@googlegroups.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import json
from multiprocessing import Queue

import cyclone.websocket

from vt_utils_converter import PostgisToJSON
from vt_as_provider_manager import ProviderManager
from vt_as_sync import SyncManager
from vt_utils_result_vttiler import ResultVTTiler
from vt_utils_parameters import Parameters


## Class CorsStaticFileHandler
#  A static file handler which authorize cross origin
#  Unherited cyclone.web.StaticFileHandler
class CorsStaticFileHandler(cyclone.web.StaticFileHandler):

    ## set_default_headers method
    #  Define the headers for the default handler
    #  @override cyclone.web.StaticFileHandler
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')


## Class InitHandler
#  A handler give initial parameters to the browser
#  Unherited cyclone.web.RequestHandler
class InitHandler(cyclone.web.RequestHandler):

    ## initialize method
    #  Initialize the handler for the init parameter
    #  @override cyclone.web.RequestHandler
    def initialize(self):
        self.parameters = Parameters.instance()

    ## set_default_headers method
    #  Define the headers for the default handler
    #  @override cyclone.web.RequestHandler
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    ## get method
    #  Handle GET HTTP
    #  @override cyclone.web.RequestHandler
    def get(self):
        self.write(json.dumps(self.parameters.get_viewer_param(), separators=(',', ':')))


## Class Data Handler
#  Use to handle the transmission of the data
#  retreived from postgis to the web browser
#  Unherited cyclone.websocket.WebSocketHandler
class DataHandler(cyclone.websocket.WebSocketHandler):

    ## connectionMade method
    #  Method call when the websocket is opened
    #  @override cyclone.websocket.WebSocketHandler
    def connectionMade(self):
        print "WebSocket data opened"

    ## messageReceived method
    #  Method call when a message is received
    #  Request all content in the extent specified in the message
    #  @param message in JSON format like:
    #   '{"Xmin": 0, "Ymin": 0, "Xmax": 50, "Ymax": 50}' for request all vectors
    #   '{"Xmin": 0, "Ymin": 0, "Xmax": 50, "Ymax": 50, uuid: "my_uuid"}' for a request only a specific vector
    #  @override cyclone.websocket.WebSocketHandler
    def messageReceived(self, message):
        # Keep alive connection
        if message == "ping":
            self.sendMessage("pong")
            return
        d = json.loads(message)
        vectors = ProviderManager.instance().request_tile(**d)
        if not vectors:
            self.sendMessage("{}")
            return
        translator = PostgisToJSON()
        for v in vectors:
            for i in range(len(v['results'])):
                if v['results'][i]:
                    json_ = translator.parse(v['results'][i], v['geom'], v['hasH'], v['color'][i], v['uuid'])
                    self.sendMessage(json_)

    ## connectionLost method
    #  Method call when the websocket is closed
    #  @param reason to indicate the reason of the closed instance
    #  @override cyclone.websocket.WebSocketHandler
    def connectionLost(self, reason):
        print "WebSocket data closed"


## Synchronisation Handler
#  Use to handle the synchronisation of the view
#  from QGIS to the web browser
#  Unherited cyclone.websocket.WebSocketHandler
class SyncHandler(cyclone.websocket.WebSocketHandler):

    ## initialize method
    #  Method to initialize the handler
    #  @override cyclone.websocket.WebSocketHandler
    def initialize(self):
        SyncManager.instance().add_listener(self)

    ## connectionMade method
    #  Method call when the websocket is opened
    #  @override cyclone.websocket.WebSocketHandler
    def connectionMade(self):
        print "WebSocket sync opened"

    ## meassageReceived method
    #  Method call when a message is received
    #  @param message received
    #  @override cyclone.websocket.WebSocketHandler
    def messageReceived(self, message):
        # Keep alive connection
        if message == "ping":
            self.sendMessage("pong")
            return
        pass  # Do nothing, simplex communication

    ## connectionLost method
    #  Method call when the websocket is closed
    #  @param reason to indicate the reason of the closed instance
    #  @override cyclone.websocket.WebSocketHandler
    def connectionLost(self, reason):
        print "WebSocket sync closed"

    ## on_finish method
    #  Method remove the listener
    #  @override cyclone.websocket.WebSocketHandler
    def on_finish(self):
        print "WebSocket finished"
        SyncManager.instance().remove_listener(self)


## Tiles information handler
#  Use to give the information related to the tiles generated
#  when the GDAL tiling is finished
#  Unherited cyclone.websocket.WebSocketHandler
class TilesInfoHandler(cyclone.websocket.WebSocketHandler):

    ## initialize method
    #  Method to initialize the handler
    #  @override cyclone.websocket.WebSocketHandler
    def initialize(self):
        self.parameters = Parameters.instance()
        self.result = ResultVTTiler.instance()

    ## connectionMade method
    #  Method call when the websocket is opened
    #  @override cyclone.websocket.WebSocketHandler
    def connectionMade(self):
        print "WebSocket tiles_info opened"

        if not self.result.is_define():
            self.result.set_result(self.parameters.GDALqueue.get())
            self.parameters.GDALqueue.close()

        if self.parameters.GDALprocess and self.parameters.GDALprocess.is_alive():
            print "Wait GDAL tiling ..."
            self.parameters.GDALprocess.join()
            print "Send tiles info ..."

        tilesInfo = self.parameters.get_tiling_param()
        # Add pixel Size in JSON and Min/Max height if have dem
        if self.result.is_define():
            tilesInfo['pixelSize'] = self.result.pixelSize
            if self.result.is_dem():
                tilesInfo['minHeight'] = self.result.minHeight
                tilesInfo['maxHeight'] = self.result.maxHeight

        js = json.dumps(tilesInfo, separators=(',', ':'))
        self.sendMessage(js)

    ## connectionLost method
    #  Method call when the websocket is closed
    #  @param reason to indicate the reason of the closed instance
    #  @override cyclone.websocket.WebSocketHandler
    def connectionLost(self, reason):
        print "WebSocket tiles_info closed"
