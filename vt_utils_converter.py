import re


def translateX3DToThreeJs(message):

    deb = "<IndexedFaceSet  coordIndex='"
    mid = "'><Coordinate point='"

    tmp = re.sub("<IndexedFaceSet  coordIndex='", "", message)
    index = re.match("(.*)\'>(.*)", tmp).group(1)

    tmp = re.sub(index + mid, "", tmp)
    vertices = re.match("(.*)\' />(.*)", tmp).group(1)
    vertices = re.sub(" ", ",", vertices)
    verticesT = vertices.split(',')

    indexT = index.split(' ')
    indexT.insert(0, "-1")
    for i in range(len(indexT)):
        if(i % 5 == 0):
            indexT[i] = -1

    faces = ','.join(str(e) for e in indexT)

    json = """
    {
        "metadata" :
        {
            "formatVersion" : 3.1,
            "generatedBy"   : "Vizitown Creation",
            "vertices"      : {VERTICES},
            "faces"         : {FACES},
            "normals"       : 0,
            "colors"        : 0,
            "uvs"           : [],
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
    }
    """

    json = re.sub("{VERTICES}", str(len(verticesT) / 3), json)
    json = re.sub("{FACES}", str(len(indexT) / 5), json)
    json = re.sub("{TAB_VERTICES}", vertices, json)
    json = re.sub("{TAB_FACES}", faces, json)

    return json