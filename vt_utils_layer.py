import re
from vt_utils


class Layer:

    def __init__(self, QgsMapLayer, column2=None, typeColumn2=None):
        self.qgisLayer = QgsMapLayer
        source = self.parse_vector(QgsMapLayer.source())

        self._host = source['host']
        self._dbname = source['dbname']
        self._port = source['port']
        self._user = source['user']
        self._password = source['password']
        self._table = source['table']
        self._column = source['column']

        self._srid = QgsMapLayer.crs().postgisSrid()
        self._column2 = column2
        self._typeColumn2 = typeColumn2

        self._displayName = QgsMapLayer.name() + ' ' + self._column

        # single id for a layer
        self._uuid = re.sub("\"", "", str(dbname + table + column))

        # singleSymbol
        # graduatedSymbol
        # categorizedSymbol
        self._colorType = QgsMapLayer.rendererV2().type()

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

    ## parseVector to recuperate vector information in QGIS
    #  This function give the query to ask the database and
    #  return vectors informations into QGIS
    #  @param source String information to query the database
    #  @param srid of the vector layer
    #  @param color of the vector layer
    #  @return String with vectors informations
    def parse_vector(self, source):
        m = re.match(r"""
        \s*dbname='(?P<dbname>.*?)'\s*host=(?P<host>\d+.\d+.\d+.\d+)\s*port=(?P<port>\d+)
        \s*user='(?P<user>.*?)'\s*password='(?P<password>.*?)'\s*.*
        \s*.*\s*table=(?P<table>\S+)\s*\((?P<column>.*?)\)""", source, re.X)
        return {
            'dbname': m.group('dbname'),
            'host': m.group('host'),
            'port': int(m.group('port')),
            'user': m.group('user'),
            'password': m.group('password'),
            'table': m.group('table'),
            'column': m.group('column'),
        }