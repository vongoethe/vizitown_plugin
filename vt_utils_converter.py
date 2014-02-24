import re
from xml.dom import minidom
import json


## PostgisToJSON class to converts an X3D formats in a json
class PostgisToJSON:

    ## The Constructor
    def __init__(self):
        self.nbPointVertice = 3
        self.noHeight = 0

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

    ## parse method to manage the process in the class and
    #  use the appropriate process in function of the data
    #  @param resultArray to stock the data
    #  @param geometry to check the type of geometry
    #  @param hasH to define the representation of data
    #  @param color to define the color of data
    #  @return a json
    def parse(self, resultArray, geometry, hasH, color, uuid):

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

        exchange = re.sub('{COLOR}', color[0], exchange)
        exchange = re.sub('{GEOMETRY}', geometry, exchange)
        exchange = re.sub('{UUID}', uuid, exchange)
        print exchange

        noHeight = "0"
        geometries = ""
        for g in resultArray:
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

                elif (geometry == 'POLYHEDRALSURFACE' or
                        geometry == 'TIN'):
                    geometries += self._parse_triangle(str(g[0])) + ','

            else:
                if geometry == 'POINT':
                    geometries += self._parse_point(str(g), noHeight) + ','

                elif (geometry == 'LINESTRING' or
                        geometry == 'MULTILINESTRING'):
                    geometries += self._parse_line(str(g), noHeight) + ','

                elif (geometry == 'POLYGON' or
                        geometry == 'MULTIPOLYGON'):
                    geometries += self._parse_polygon(str(g), noHeight) + ','

                elif (geometry == 'POLYHEDRALSURFACE' or
                        geometry == 'TIN'):
                    geometries += self._parse_triangle(str(g)) + ','

        geometries = PostgisToJSON.remove_comma(geometries)
        exchange = re.sub('{JSON_GEOM}', geometries, exchange)
        return exchange

    ## _parse_point method to parse a point data
    #  @param message to stock the data
    #  @param height to add an information of elevation
    #  @return a json file
    def _parse_point(self, message, height):
        vertice = message.split(' ')
        vertice.pop()
        return self._get_json_geom(vertice, height)

    #def _parse_point(self, result, hasH):
    #    if hasH:
    #        vertice = str(result[0])
    #        height = str(result[1])
    #    else:
    #        vertice = str(result)
    #        height = self.noHeight
    #    vertice.pop()
    #    return self._get_json_geom(vertice, height)

    ## _parse_line method to parse a line data
    #  @param message to stock the data
    #  @param height to add an information of elevation
    #  @return a json file
    def _parse_line(self, message, height):
        xmldoc = minidom.parseString(message)
        vertices = self._get_vertices(xmldoc)
        vertices = vertices.split(',')
        for i in range(len(vertices) - 1, 0, -self.nbPointVertice):
            vertices.pop(i)
        return self._get_json_geom(vertices, height)

    ## _parse_polygon method to parse a polygon or multipolygon data
    #  @param message to stock the data
    #  @param height to add an information of elevation
    #  @return a json file
    def _parse_polygon(self, message, height):
        js = json.loads(message)
        if js['type'] == 'Polygon':
            return self._get_json_geom(self._get_polygon_point(js['coordinates'][0]), height)

        elif js['type'] == 'MultiPolygon':
            geometries = ""
            for i in range(len(js['coordinates'])):
                geometries += self._get_json_geom(self._get_polygon_point(js['coordinates'][i][0]), height) + ','
            return PostgisToJSON.remove_comma(geometries)
        else:
            return ""

    ## _get_polygon_point method to select a points with a polygon
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

    ## _parse_triangle method to parse a triangle data
    #  @param string to stock the data
    #  @return a json file
    def _parse_triangle(self, string):
        nbIndexFace = 3
        bitMask = 0
        xmldoc = minidom.parseString(string)
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

    ## _get_vertices Getter of vertex data
    #  @param xmldoc to stock the data
    #  @return a specific vertex
    def _get_vertices(sef, xmldoc):
        nodeVertice = xmldoc.getElementsByTagName('Coordinate')
        vertices = nodeVertice[0].getAttribute('point')
        vertices = re.sub(' ', ',', vertices)
        return PostgisToJSON.remove_comma(vertices)

    ## _count_vertice method to count the number of vertex
    #  @param vertices stock a vertex number
    #  @return a number of vertex
    def _count_vertice(self, vertices):
        verticesTab = vertices.split(',')
        return len(verticesTab) / self.nbPointVertice

    ## _get_json_geom Getter of a geo json data
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

    ## _get_json_threejs Getter a threejs json data
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

    ## remove_comma to delete the comma in a string
    #  @string the string to transform
    #  @return the string after the process
    @staticmethod
    def remove_comma(string):
        if string[-1:] == ',':
            string = string[:-1]
        return string