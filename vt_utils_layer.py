import re
from vt_utils


class Layer:

    def __init__(self, QgsMapLayer):
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
        self._column2 = None
        self._typeColumn2 = None

        self._displayName = QgsMapLayer.name() + ' ' + self._column

        # single id for a layer
        self._uuid = re.sub("\"", "", str(dbname + table + column))


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

    def update_color(self)
        self._columnColor = self.get_column_color()
        self._color = self.get_color()

    ## Get the color of the vector layer. If is categorized symbol or graduate symbol, the color is white
    def get_color(self):
        renderer = self.qgisLayer.rendererV2()
        if self.get_color_type() == "singleSymbol":
            tabColor = []
            tabColor.append({'color': str(renderer.symbol().color().name())})
            return tabColor
        if self.get_color_type() == "graduatedSymbol":
            tabColor = []
            color = []
            lowerValue = []
            upperValue = []
            size = 0
            for i in renderer.symbols():
                color.append(str(i.color().name()))
                size = size + 1
            for j in renderer.ranges():
                lowerValue.append(j.lowerValue())
                upperValue.append(j.upperValue())
            for nb in xrange(size):
                tabColor.append({'min': lowerValue[nb], 'max': upperValue[nb], 'color': color[nb]})
            return tabColor
        if self.get_color_type() == "categorizedSymbol":
            tabColor = []
            color = []
            value = []
            size = 0
            for i in renderer.symbols():
                color.append(str(i.color().name()))
                size = size + 1
            for cat in renderer.categories():
                value.append(cat.value())
            for nb in xrange(size):
                tabColor.append({'value': value[nb], 'color': color[nb]})
            return tabColor

    # singleSymbol
    # graduatedSymbol
    # categorizedSymbol
    def get_color_type(self):
        return self.qgisLayer.rendererV2().type()

    ## Get the name of the column where the analysis was perform. If there isn't analysis, the name is none
    def get_column_color(self):
        if self.get_color_type() == "singleSymbol":
            return None
        if self.get_color_type() == "graduatedSymbol" or self.get_color_type() == "categorizedSymbol":
            return renderer.classAttribute()
