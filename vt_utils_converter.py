import re
from xml.dom import minidom


class X3DTranslateToThreeJs:

    def __init__(self):
        self.nbFaces = 0
        self.nbVertices = 0

        self.nbPointVertice = 3

        self.__json = """{
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

    def parse(self, message, geometry):

        if geometry == 'POINT':
            return self.__parse_point(message)
        else:
            xmldoc = minidom.parseString(message)
            if geometry == 'LINESTRING' or geometry == 'MULTILINESTRING':
                return self.__parse_line(xmldoc)

    def __parse_point(self, message):
        nbFace = "0"
        nbPoint = "1"

        vertice = re.sub(' ', ',', message)
        return self.__get_json(nbFace, nbPoint, None, vertice)

    def __parse_line(self, xmldoc):
        nbFace = "0"

        nodeVertice = xmldoc.getElementsByTagName('Coordinate')
        vertices = nodeVertice[0].getAttribute('point')
        vertices = re.sub(' ', ',', vertices)
        vertices = vertices[:-1]

        verticesTab = vertices.split(',')
        nbVertice = len(verticesTab) / self.nbPointVertice
        return self.__get_json(nbFace, str(nbVertice), None, vertices)

    def __get_json(self, nbFaces, nbVertices, faces, vertices):
        self.__define_field(nbFaces, nbVertices)

        json = self.__json

        json = re.sub("{VERTICES}", nbVertices, json)
        json = re.sub("{FACES}", nbFaces, json)

        json = re.sub("{TAB_VERTICES}", vertices, json)
        if faces is not None:
            json = re.sub("{TAB_FACES}", faces, json)
        else:
            json = re.sub("{TAB_FACES}", "", json)

        return json

    def __define_field(self, nbFaces, nbVertices):
        self.nbFaces = nbFaces
        self.nbVertices = nbVertices