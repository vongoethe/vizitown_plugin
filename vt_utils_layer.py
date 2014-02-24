import re

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

        # single id for a layer
        self._uuid = re.sub("\"", "", str(dbname + table + column))

        # singleSymbol
        # graduatedSymbol
        # categorizedSymbol
        self._colorType = colorType

        # if self._colorType is singleSymbol equal None
        # else is field in database to sort data
        self._columnColor = None

        # if self_colorType is singleSymbol is an array of one with one color in index 0
        # elif self.colorType is graduatedSymbol is an array of dict like that {"min":  value, "max": value, "color": color}
        # elif self.colorType is categorizedSymbol is an array of dict like that {"value": value, "color": color}
        self._color = []

    # columnColor is None if the layer has a plain color so color is an array with only one color in.
    # else columnColor is the field in db to color geometries with right color and color is an array with dict in
    # dict in array looks like that:
    # {
    # 	"min" 	: value,
    #	"max" 	: value,
    #	"color"	: value
    # }
    def add_color(self, columnColor, color):
        if columnColor is not None:
            self._columnColor = columnColor
        self._color = color