

class Layer:


    def __init__(self, host, dbname, port, user, password, srid, table, colorType, column, column2=None, typeColumn2=None):
        self._host = host
        self._dbname = dbname
        self._port = port
        self._user = user
        self._password = password
        self._table = table
        self._column = column

        self._srid = srid
        self._column2 = None
        self._typeColumn2 = None

        self._colorType = colorType
        self._columnColor = None
        self._color = []

    #
    # columnColor is None if the layer has a plain color so color is an array with only one color in.
    # else columnColor is the field in db to color geometries with right color and color is an array with dict in
    # dict in array looks like that:
    # {
    # 	"min" 	: value,
    #	"max" 	: value,
    #	"color"	: value
    # }
    def add_color(self, columnColor, color):
        if colorColumn is not None:
            self._columnColor = columnColor
        self._color = color
