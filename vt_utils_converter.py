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
import re
from xml.dom import minidom
import json


## Class PostgisToJSON
#  Converts an X3D formats in a json
class PostgisToJSON:

    ## Constructor
    def __init__(self):
        self.nbPointVertice = 3
        self.noHeight = "0"

        self._jsonThreejs = """{
        "metadata" :
        {
            "formatVersion" : 3.1,
            "generatedBy"   : "Vizitown Creation",
            "vertices"      : {VERTICES},
            "faces"         : {FACES},
            "normals"       : 0,
            "colors"        : 0,
            "uvs"           : 0,
            "materials"     : 0,
            "morphTargets"  : 0,
            "bones"         : 0
        },

        "vertices" : [{TAB_VERTICES}],

        "morphTargets" : [],

        "normals" : [],

        "colors" : [],

        "uvs" : [],

        "faces" : [{TAB_FACES}],

        "bones" : [],

        "skinIndices" : [],

        "skinWeights" : [],

        "animations" : []

    }"""

        self._jsonExchange = """{
    "dim"          : "{TYPE}",
    "color"        : "{COLOR}",
    "type"         : "{GEOMETRY}",
    "uuid"         : "{UUID}",
    "geometries"   : [{JSON_GEOM}]
}"""

        self._jsonGeom = """{
        "height"        : {HEIGHT},
        "coordinates"   : [{COORDINATES}]
    }"""

    ## parse method
    #  Manage the process in the class and use the appropriate process in function of the data
    #  @param resultArray to stock the data
    #  @param geometry to check the type of geometry
    #  @param hasH to define the representation of data
    #  @param color to define the color of data
    #  @param uuid to define the identifiant of data
    #  @return a json
    def parse(self, resultArray, geometry, hasH, color, uuid):
        self.geometry = geometry
        self.hasH = hasH
        self.color = color
        self.uuid = uuid
        exchange = self._jsonExchange

        geometries = ""
        for r in resultArray:
            # geometry has height
            data = self._get_data(r, hasH)
            if geometry == 'POINT':
                geometries += self._parse_point(data) + ','

            elif (geometry == 'LINESTRING' or
                    geometry == 'MULTILINESTRING'):
                geometries += self._parse_line(data) + ','

            elif (geometry == 'POLYGON' or
                    geometry == 'MULTIPOLYGON'):
                geometries += self._parse_polygon(data) + ','

            elif (geometry == 'POLYHEDRALSURFACE' or
                    geometry == 'TIN'):
                geometries += self._parse_triangle(data) + ','

        geometries = PostgisToJSON.remove_comma(geometries)
        exchange = self._replace_metadata(exchange)
        exchange = re.sub('{JSON_GEOM}', geometries, exchange)
        return exchange

    ## _replace_metadata method
    #  Change the metadata by another information
    #  @param exchange the new information
    #  @return the new metadata
    def _replace_metadata(self, exchange):
        exchange = re.sub('{COLOR}', self.color, exchange)
        exchange = re.sub('{UUID}', self.uuid, exchange)
        # geometry in 3 dimensions
        if (self.geometry == 'POLYHEDRALSURFACE' or
                self.geometry == 'TIN'):
            exchange = re.sub('{TYPE}', "3", exchange)
        else:
            # geometry in 2.5 dimensions (geometry with height)
            if self.hasH:
                exchange = re.sub('{TYPE}', "2.5", exchange)
            # geometry in 2 dimensions
            else:
                exchange = re.sub('{TYPE}', "2", exchange)

        geom = ''
        if self.geometry == 'POINT':
            geom = 'point'
        elif (self.geometry == 'LINESTRING' or
                self.geometry == 'MULTILINESTRING'):
            geom = 'line'
        elif (self.geometry == 'POLYGON' or
                self.geometry == 'MULTIPOLYGON' or
                self.geometry == 'POLYHEDRALSURFACE' or
                self.geometry == 'TIN'):
            geom = 'polygon'
        else:
            geom = 'undefined'
        return re.sub('{GEOMETRY}', geom, exchange)

    ## _get_data method
    #  Getter to access to the data and associated information
    #  @param result
    #  @param hasH
    #  @return the data
    def _get_data(self, result, hasH):
        data = []
        if hasH:
            data.append(str(result[0]))
            data.append(str(result[1]))
        else:
            data.append(result)
            data.append(self.noHeight)
        return data

    ## _parse_point method
    #  Parse a point data
    #  @param dataArray to stock the data
    #  @return a json file
    def _parse_point(self, dataArray):
        vertice = dataArray[0].split(' ')
        vertice.pop()
        try:
            # dataArray[1] is a number and its a normal point
            float(dataArray[1])
            return self._get_json_geom(vertice, dataArray[1])
        except:
            # dataArray[1] NaN probably a json
            self.geometry = 'TIN'
            X = float(vertice[0])
            Y = float(vertice[1])
            js = json.loads(dataArray[1])
            verticesArray = js['vertices']
            for i in range(0, len(verticesArray), 3):
                verticesArray[i] += X
                verticesArray[i + 1] += Y
            js['vertices'] = verticesArray
            return json.dumps(js)

    ## _parse_line method
    #  Parse a line data
    #  @param dataArray to stock the data
    #  @return a json file
    def _parse_line(self, dataArray):
        xmldoc = minidom.parseString(dataArray[0])
        vertices = self._get_vertices(xmldoc)
        vertices = vertices.split(',')
        for i in range(len(vertices) - 1, 0, -self.nbPointVertice):
            vertices.pop(i)
        return self._get_json_geom(vertices, dataArray[1])

    ## _parse_polygon method
    #  Parse a polygon or multipolygon data
    #  @param dataArray to stock the data
    #  @return a json file
    def _parse_polygon(self, dataArray):
        js = json.loads(dataArray[0])
        if js['type'] == 'Polygon':
            return self._get_json_geom(self._get_polygon_point(js['coordinates'][0]), dataArray[1])

        elif js['type'] == 'MultiPolygon':
            geometries = ""
            for i in range(len(js['coordinates'])):
                geometries += self._get_json_geom(self._get_polygon_point(js['coordinates'][i][0]), dataArray[1]) + ','
            return PostgisToJSON.remove_comma(geometries)
        else:
            return ""

    ## _get_polygon_point method
    #  Select a points with a polygon
    #  @polygon to define a polygon
    #  @return an array with the vertices of the polygon
    def _get_polygon_point(self, polygon):
        X = 0
        Y = 1
        array = []
        for i in range(len(polygon)):
            array.append(polygon[i][X])
            array.append(polygon[i][Y])
        return array

    ## _parse_triangle method
    #  Parse a triangle data
    #  @param string to stock the data
    #  @return a json file
    def _parse_triangle(self, dataArray):
        nbIndexFace = 3
        bitMask = 0
        xmldoc = minidom.parseString(dataArray[0])
        vertices = self._get_vertices(xmldoc)
        nbVertice = self._count_vertice(vertices)

        facesTab = []
        for i in range(0, nbVertice, nbIndexFace):
            facesTab.append(0)
            facesTab.append(i)
            facesTab.append(i + 1)
            facesTab.append(i + 2)

        faces = ','.join(str(f) for f in facesTab)
        nbFace = nbVertice / nbIndexFace
        return self._get_json_threejs(nbFace, nbVertice, faces, vertices)

    ## _get_vertices method
    #  Getter of vertex data
    #  @param xmldoc to stock the data
    #  @return a specific vertex
    def _get_vertices(self, xmldoc):
        nodeVertice = xmldoc.getElementsByTagName('Coordinate')
        vertices = nodeVertice[0].getAttribute('point')
        vertices = re.sub(' ', ',', vertices)
        return PostgisToJSON.remove_comma(vertices)

    ## _count_vertice method
    #  Count the number of vertex
    #  @param vertices stock a vertex number
    #  @return a number of vertex
    def _count_vertice(self, vertices):
        verticesTab = vertices.split(',')
        return len(verticesTab) / self.nbPointVertice

    ## _get_json_geom method
    #  Getter of a geo json data
    #  @param pointArray with the several point with coordinates
    #  @param height to add an information of elevation
    #  @return a geojson file
    def _get_json_geom(self, pointArray, height):
        gjson = self._jsonGeom
        coord = ''
        for i in range(0, len(pointArray) - 1, 2):
            coord += str(pointArray[i]) + ',' + str(pointArray[i + 1]) + ','
        coord = PostgisToJSON.remove_comma(coord)

        gjson = re.sub('{COORDINATES}', coord, gjson)
        gjson = re.sub('{HEIGHT}', height, gjson)
        return gjson

    ## _get_json_threejs method
    #  Getter a threejs json data
    #  @param nbFaces to define the number of faces
    #  @param nbVertices to define the number of vertex
    #  @param faces stock a faces values
    #  @param vertices stock a vertex values
    #  @return a threejs json file
    def _get_json_threejs(self, nbFaces, nbVertices, faces, vertices):
        js = self._jsonThreejs

        js = re.sub("{VERTICES}", str(nbVertices), js)
        js = re.sub("{FACES}", str(nbFaces), js)

        js = re.sub("{TAB_VERTICES}", str(vertices), js)
        if faces is not None:
            js = re.sub("{TAB_FACES}", str(faces), js)
        else:
            json = re.sub("{TAB_FACES}", "", js)

        return js

    ## remove_comma static method
    #  Delete the comma in a string
    #  @string the string to transform
    #  @return the string after the process
    @staticmethod
    def remove_comma(string):
        if string[-1:] == ',':
            string = string[:-1]
        return string