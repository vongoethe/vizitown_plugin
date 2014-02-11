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
            elif geometry == 'POLYGON' or geometry == 'MULTIPOLYGON' or geometry == 'POLYHEDRALSURFACE':
                return self.__parse_triangle(xmldoc)
            else:
                return None

    def __parse_point(self, message):
        nbFace = "0"
        nbPoint = "1"

        vertice = re.sub(' ', ',', message)
        return self.__get_json(nbFace, nbPoint, None, vertice)

    def __parse_line(self, xmldoc):
        nbFace = "0"

        vertices = self.__get_vertices(xmldoc)
        nbVertice = self.__count_vertice(vertices)

        return self.__get_json(nbFace, str(nbVertice), None, vertices)

    def __parse_triangle(self, xmldoc):
        nbIndexFace = 3
        bitMask = 0

        vertices = self.__get_vertices(xmldoc)
        nbVertice = self.__count_vertice(vertices)

        facesTab = []
        for i in range(0, nbVertice, nbIndexFace):
            facesTab.append(0)
            facesTab.append(i)
            facesTab.append(i + 1)
            facesTab.append(i + 2)

        faces = ','.join(str(f) for f in facesTab)
        nbFace = nbVertice / nbIndexFace
        return self.__get_json(str(nbFace), str(nbVertice), faces, vertices)

    def __get_vertices(sef, xmldoc):
        nodeVertice = xmldoc.getElementsByTagName('Coordinate')
        vertices = nodeVertice[0].getAttribute('point')
        vertices = re.sub(' ', ',', vertices)
        if vertices[-1:] == ',':
            vertices = vertices[:-1]
        return vertices

    def __count_vertice(self, vertices):
        verticesTab = vertices.split(',')
        return len(verticesTab) / self.nbPointVertice

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