import re
from xml.dom import minidom


class X3DTranslateToThreeJs:

    def __init__(self):
        self.nbFaces = 0
        self.nbVertices = 0

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

    def __parse_point(self, message):

        vertice = re.sub(' ', ',', message)
        return self.__get_json("0", "1", None, vertice)

    def __get_json(self, nbFaces, nbVertices, faces, vertices):
        self.__define_field(nbFaces, nbVertices)

        json = self.__json

        json = re.sub("{VERTICES}", nbVertices, json)
        json = re.sub("{FACES}", nbFaces, json)

        json = re.sub("{TAB_VERTICES}", vertices, json)
        if faces is not None:
            json = re.sub("{TAB_FACES}", faces, json)

        return json

    def __define_field(self, nbFaces, nbVertices):
        self.nbFaces = nbFaces
        self.nbVertices = nbVertices