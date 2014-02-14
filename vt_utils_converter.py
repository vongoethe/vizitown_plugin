import re
from xml.dom import minidom


## X3DTranslateToThreeJs class to converts an X3D formats in a json
class X3DTranslateToThreeJs:

    ## The Constructor
    def __init__(self):
        self.nbFaces = 0
        self.nbVertices = 0

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
                    geometries += self._parse_point(str(g[0]), g[1]) + ','
            else:
                if geometry == 'POINT':
                    geometries += self._parse_point(str(g), noHeight) + ','

        if geometries[-1:] == ',':
            geometries = geometries[:-1]
        exchange = re.sub('{JSON_GEOM}', geometries, exchange)
        return exchange
        #        else:
        #            xmldoc = minidom.parseString(g[0])
        #            if (geometry == 'LINESTRING' or
        #                    geometry == 'MULTILINESTRING'):
        #                geometries += self._parse_line(xmldoc, g[1]) + ','

        #    else:
        #        if geometry == 'POINT':
        #            geometries += self._parse_point(g, noHeight)
        #        else:
        #            xmldoc = minidom.parseString(g)
        #            if (geometry == 'TIN' or
        #                    geometry == 'POLYHEDRALSURFACE'):
        #                geometries += self._parse_triangle(xmldoc) + ','

        #if geometry == 'POINT':
        #    return self._parse_point(message)
        #else:
        #    xmldoc = minidom.parseString(message)
        #    if geometry == 'LINESTRING' or geometry == 'MULTILINESTRING':
        #        return self._parse_line(xmldoc)
        #    elif geometry == 'POLYGON' or geometry == 'POLYHEDRALSURFACE':
        #        return self._parse_triangle(xmldoc)
        #    else:
        #        return None

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
    def _parse_line(self, xmldoc):
        nbFace = 0

        vertices = self._get_vertices(xmldoc)
        nbVertice = self._count_vertice(vertices)

        return self._get_json(nbFace, nbVertice, None, vertices)

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
        if vertices[-1:] == ',':
            vertices = vertices[:-1]
        return vertices

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
            coord += pointArray[i] + ',' + pointArray[i + 1] + ','
            i += 1
        if coord[-1:] == ',':
            coord = coord[:-1]

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
        self._define_field(nbFaces, nbVertices)

        json = self._json

        json = re.sub("{VERTICES}", str(nbVertices), json)
        json = re.sub("{FACES}", str(nbFaces), json)

        json = re.sub("{TAB_VERTICES}", str(vertices), json)
        if faces is not None:
            json = re.sub("{TAB_FACES}", str(faces), json)
        else:
            json = re.sub("{TAB_FACES}", "", json)

        return json

    ## _define_field method define information about data
    #  @param nbFaces to define the number of faces
    #  @param nbVertices to define the number of vertex
    def _define_field(self, nbFaces, nbVertices):
        self.nbFaces = nbFaces
        self.nbVertices = nbVertices
