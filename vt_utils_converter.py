import re
from xml.dom import minidom
import json


## X3DTranslateToThreeJs class to converts an X3D formats in a json
class X3DTranslateToThreeJs:

    ## The Constructor
    def __init__(self):
        self.nbPointVertice = 3

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
    "type"          : {TYPE},
    "geometries"    : [{JSON_GEOM}]
}"""

        self._jsonGeom = """{
    "height"        : {HEIGHT},
    "coordinates"   : [{COORDINATES}]
}"""

    ## parse method to manage the process in the class and
    #  use the appropriate process in function of the data
    #  @param message to stock the data
    #  @param geometry to check the type of geometry
    def parse(self, array, geometry, hasH):

        exchange = self._jsonExchange
        # geometry in 3 dimensions
        if (geometry == 'POLYHEDRALSURFACE' or
                geometry == 'TIN'):
            exchange = re.sub('{TYPE}', "3", exchange)
        else:
            # geometry in 2.5 dimensions (geometry with height)
            if hasH:
                exchange = re.sub('{TYPE}', "2.5", exchange)
            # geometry in 2 dimensions
            else:
                exchange = re.sub('{TYPE}', "2", exchange)

        noHeight = "0"
        geometries = ""
        for g in array:
            # geometry has height
            if hasH:
                if geometry == 'POINT':
                    geometries += self._parse_point(str(g[0]), str(g[1])) + ','

                elif (geometry == 'LINESTRING' or
                        geometry == 'MULTILINESTRING'):
                    geometries += self._parse_line(str(g[0]), str(g[1])) + ','

                elif (geometry == 'POLYGON' or
                        geometry == 'MULTIPOLYGON'):
                    geometries += self._parse_polygon(str(g[0]), str(g[1])) + ','

            else:
                if geometry == 'POINT':
                    geometries += self._parse_point(str(g), noHeight) + ','

                elif (geometry == 'LINESTRING' or
                        geometry == 'MULTILINESTRING'):
                    geometries += self._parse_line(str(g), noHeight) + ','

                elif (geometry == 'POLYGON' or
                        geometry == 'MULTIPOLYGON'):
                    geometries += self._parse_polygon(str(g), noHeight) + ','

        geometries = remove_comma(geometries)
        exchange = re.sub('{JSON_GEOM}', geometries, exchange)
        return exchange

    ## _parse_point method to parse a point data
    #  @param message to stock the data
    #  @return a json file
    def _parse_point(self, message, height):
        vertice = message.split(' ')
        vertice.pop()
        return self._get_json_geom(vertice, height)

    ## _parse_line method to parse a line data
    #  @param xmldoc to stock the data
    #  @return a json file
    def _parse_line(self, message, height):
        xmldoc = minidom.parseString(message)
        vertices = self._get_vertices(xmldoc)
        vertices = vertices.split(',')
        for i in range(len(vertices) - 1, 0, -self.nbPointVertice):
            vertices.pop(i)
        return self._get_json_geom(vertices, height)

    def _parse_polygon(self, message, height):
        js = json.loads(message)
        print js['type']
        if js['type'] == 'Polygon':
            return self._get_json_geom(self._get_polygon_point(js['coordinates'][0]), height)

        elif js['type'] == 'MultiPolygon':
            geometries = ""
            for i in range(len(js['coordinates'][0])):
                geometries += self._get_json_geom(self._get_polygon_point(js['coordinates'][0][i]), height) + ','
            return geometries
        else:
            return ""

    def _get_polygon_point(self, polygon):
        X = 0
        Y = 1
        array = []
        print polygon
        for i in range(len(polygon)):
            array.append(polygon[i][X])
            array.append(polygon[i][Y])
        return array

    ## _parse_triangle method to parse a triangle data
    #  @param xmldoc to stock the data
    #  @return a json file
    def _parse_triangle(self, xmldoc):
        nbIndexFace = 3
        bitMask = 0

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
        return self._get_json(nbFace, nbVertice, faces, vertices)

    ## _get_vertices Getter of vertex data
    #  @param xmldoc to stock the data
    #  @return a specific vertex
    def _get_vertices(sef, xmldoc):
        nodeVertice = xmldoc.getElementsByTagName('Coordinate')
        vertices = nodeVertice[0].getAttribute('point')
        vertices = re.sub(' ', ',', vertices)
        return remove_comma(vertices)

    ## _count_vertice method to count the number of vertex
    #  @param vertices stock a vertex number
    #  @return a number of vertex
    def _count_vertice(self, vertices):
        verticesTab = vertices.split(',')
        return len(verticesTab) / self.nbPointVertice

    def _get_json_geom(self, pointArray, height):
        gjson = self._jsonGeom
        coord = ''
        for i in range(len(pointArray) - 1):
            coord += str(pointArray[i]) + ',' + str(pointArray[i + 1]) + ','
            i += 1
        coord = remove_comma(coord)

        gjson = re.sub('{COORDINATES}', coord, gjson)
        gjson = re.sub('{HEIGHT}', height, gjson)
        return gjson

    ## _get_json Getter of json data
    #  @param nbFaces to define the number of faces
    #  @param nbVertices to define the number of vertex
    #  @param faces stock a faces values
    #  @param vertices stock a vertex values
    #  @return a json file
    def _get_json_threejs(self, nbFaces, nbVertices, faces, vertices):
        json = self._json

        json = re.sub("{VERTICES}", str(nbVertices), json)
        json = re.sub("{FACES}", str(nbFaces), json)

        json = re.sub("{TAB_VERTICES}", str(vertices), json)
        if faces is not None:
            json = re.sub("{TAB_FACES}", str(faces), json)
        else:
            json = re.sub("{TAB_FACES}", "", json)

        return json

    @staticmethod
    def remove_comma(string):
        if string[-1:] == ',':
            string = string[:-1]
        return string