import re
from xml.dom import minidom


## X3DTranslateToThreeJs class to converts an X3D formats in a json
class X3DTranslateToThreeJs:

    ## The Constructor
    def __init__(self):
        self.nbFaces = 0
        self.nbVertices = 0

        self.nbPointVertice = 3

        self.__jsonThreejs = """{
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

        self.__jsonExchange = """{
    "type"          : {TYPE},
    "geometries"    : [{JSON_GEOM}]
}"""

        self.__jsonGeom = """{
    "height"        : {HEIGHT},
    "coordinates"   : [{COORDINATES}]
}"""

    ## parse method to manage the process in the class and
    #  use the appropriate process in function of the data
    #  @param message to stock the data
    #  @param geometry to check the type of geometry
    def parse(self, array, geometry, hasH):

        exchange = self.jsonExchange
        # geometry in 3 dimensions
        if (geometry == 'POLYHEDRALSURFACE' or
                geometry == 'TIN'):
            exchange = re.sub('{TYPE}', 3, exchange)
        else:
            # geometry in 2.5 dimensions (geometry with height)
            if hasH:
                exchange = re.sub('{TYPE}', 2.5, exchange)
            # geometry in 2 dimensions 
            else:
                exchange = re.sub('{TYPE}', 2, exchange)

        noHeight = 0
        geometries = ""
        for geometry in array:
            # geometry has height
            if hasH:
                if geometry == 'POINT':
                    geometries += self.__parse_point(geometry[0], geometry[1])
                else:
                    xmldoc = minidom.parseString(geometry[0])
                elif (geometry == 'LINESTRING' or
                        geometry == 'MULTILINESTRING'):
                    geometries += self.__parse_line(xmldoc, geometry[1]) + ','


            else:
                if geometry == 'POINT':
                    geometries += self.__parse_point(geometry, noHeight)
                else:
                    xmldoc = minidom.parseString(geometry)
                    if (geometry == 'TIN' or
                            geometry == 'POLYHEDRALSURFACE'):
                        geometries += self.__parse_triangle(xmldoc) + ','



        if geometry == 'POINT':
            return self.__parse_point(message)
        else:
            xmldoc = minidom.parseString(message)
            if geometry == 'LINESTRING' or geometry == 'MULTILINESTRING':
                return self.__parse_line(xmldoc)
            elif geometry == 'POLYGON' or geometry == 'POLYHEDRALSURFACE':
                return self.__parse_triangle(xmldoc)
            else:
                return None

    ## __parse_point method to parse a point data
    #  @param message to stock the data
    #  @return a json file
    def __parse_point(self, message, height):

        vertice = re.sub(' ', ',', message)
        vertice.pop()
        return self.__get_json_geom(vertice, height)

    ## __parse_line method to parse a line data
    #  @param xmldoc to stock the data
    #  @return a json file
    def __parse_line(self, xmldoc):
        nbFace = 0

        vertices = self.__get_vertices(xmldoc)
        nbVertice = self.__count_vertice(vertices)

        return self.__get_json(nbFace, nbVertice, None, vertices)

    ## __parse_triangle method to parse a triangle data
    #  @param xmldoc to stock the data
    #  @return a json file
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
        return self.__get_json(nbFace, nbVertice, faces, vertices)

    ## __get_vertices Getter of vertex data
    #  @param xmldoc to stock the data
    #  @return a specific vertex
    def __get_vertices(sef, xmldoc):
        nodeVertice = xmldoc.getElementsByTagName('Coordinate')
        vertices = nodeVertice[0].getAttribute('point')
        vertices = re.sub(' ', ',', vertices)
        if vertices[-1:] == ',':
            vertices = vertices[:-1]
        return vertices

    ## __count_vertice method to count the number of vertex
    #  @param vertices stock a vertex number
    #  @return a number of vertex
    def __count_vertice(self, vertices):
        verticesTab = vertices.split(',')
        return len(verticesTab) / self.nbPointVertice

    def __get_json_geom(self, pointArray, height):
        gjson = self.__jsonGeom
        coord = ''
        for i in range(len(x)):
            coord += X[i] + ',' + Y[i] + ','
        if coord[-1:] == ',':
            coord == coord[:-1]
        
        gjson = re.sub('{COORDINATES}', coord, gjson)
        gjson = re.sub('{HEIGHT}', height, gjson)
        return gjson

    ## __get_json Getter of json data
    #  @param nbFaces to define the number of faces
    #  @param nbVertices to define the number of vertex
    #  @param faces stock a faces values
    #  @param vertices stock a vertex values
    #  @return a json file
    def __get_json_threejs(self, nbFaces, nbVertices, faces, vertices):
        self.__define_field(nbFaces, nbVertices)

        json = self.__json

        json = re.sub("{VERTICES}", str(nbVertices), json)
        json = re.sub("{FACES}", str(nbFaces), json)

        json = re.sub("{TAB_VERTICES}", str(vertices), json)
        if faces is not None:
            json = re.sub("{TAB_FACES}", str(faces), json)
        else:
            json = re.sub("{TAB_FACES}", "", json)

        return json

    ## __define_field method define information about data
    #  @param nbFaces to define the number of faces
    #  @param nbVertices to define the number of vertex
    def __define_field(self, nbFaces, nbVertices):
        self.nbFaces = nbFaces
        self.nbVertices = nbVertices
