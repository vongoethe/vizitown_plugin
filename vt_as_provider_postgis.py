import re

from PyQt4.QtCore import *
from PyQt4.QtSql import *


## Postgis provider
#  Stock the attribute to use a postgis resource
class PostgisProvider:

    ## Constructor
    #  @param host database host
    #  @param dbname database name
    #  @param user database user
    #  @param password database user password
    #  @param srid of the resource
    #  @param table of the resource
    #  @param color of the resource
    #  @param column of the resource
    #  @param column2 representing a height of column or another geometry (TinZ)
    def __init__(self, layer):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(layer._host)
        self.db.setDatabaseName(layer._dbname)
        self.db.setPort(layer._port)
        self.db.setUserName(layer._user)
        self.db.setPassword(layer._password)
        self._layer = layer
        self.geometry1 = None
        self.geometry2 = None
        self.retGeometry = None
        self.hasH = False

        if not self.db.open():
            raise Exception('Connection to database cannot be established')

        print "Connection established to database %s -> %s" % (self._layer._host, self._layer._dbname)

        query = QSqlQuery(self.db)

        if self._layer._column2 is not None and self._layer._typeColumn2 != 'geometry':
            self.hasH = True

        if self._layer._typeColumn2 == 'geometry':
            getGeometry = """SELECT GeometryType({column_}), GeometryType({column2_}) FROM {table_} LIMIT 1
            """.format(column_=self._layer._column,
                       column2_=self._layer._column2,
                       table_=self._layer._table)

            if not query.exec_(getGeometry):
                print query.lastQuery()
                print query.lastError().text()
                raise Exception('DB request failed')

            query.next()
            self.geometry1 = query.value(0)
            self.geometry2 = query.value(1)

        else:
            getGeometry = """SELECT GeometryType({column_}) FROM {table_} LIMIT 1
            """.format(column_=self._layer._column,
                       table_=self._layer._table)
            if not query.exec_(getGeometry):
                print query.lastQuery()
                print query.lastError().text()
                raise Exception('DB request failed')

            query.next()
            self.geometry1 = query.value(0)

    ## Return all the result contains in the extent in param
    #  @param Xmin
    #  @param Ymin
    #  @param Xmax
    #  @param Ymax
    #  @return the tile
    def request_tile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db)
        request = ""

        extent = """POLYGON(({Xmin_} {Ymin_},
                             {Xmax_} {Ymin_},
                             {Xmax_} {Ymax_},
                             {Xmin_} {Ymax_},
                             {Xmin_} {Ymin_}))
        """.format(Xmin_=Xmin,
                   Xmax_=Xmax,
                   Ymin_=Ymin,
                   Ymax_=Ymax)

        intersect = """ WHERE {column_} && ST_GeomFromText('{extent_}', {srid_})
        """.format(column_=self._layer._column,
                   extent_=extent,
                   srid_=self._layer._srid)

        request = self._get_request()
        request += intersect

        if not query.exec_(request):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')

        results = self._sort_result(query)
        colors = self._color_array()
        return {'results': results, 'geom': self.retGeometry, 'hasH': self.hasH, 'color': colors, 'uuid': self._layer._uuid}

    def _sort_result(self, iterator):
        if (self._layer._colorType == "singleSymbol"):
            return self._get_result_single_symbol(iterator)

        elif (self._layer._colorType == "graduatedSymbol"):
            return self._get_result_graduated_symbol(iterator)

        elif (self._layer._colorType == "categorizedSymbol"):
            return self._get_result_categorized_symbol(iterator)

    def _get_result_single_symbol(self, iterator):
        array = [[]]
        while iterator.next():
            if self.hasH:
                array[0].append([iterator.value(0), iterator.value(1)])
            else:
                array[0].append(iterator.value(0))
        return array

    def _get_result_graduated_symbol(self, iterator):
        nbColor = len(self._layer._color)
        array = [[] for i in range(nbColor)]

        while iterator.next():
            for i in range(nbColor):
                if self.hasH:
                    if (iterator.value(2) >= self._layer._color[i]['min'] and
                            iterator.value(2) <= self._layer._color[i]['max']):
                        array[i].append([iterator.value(0), iterator.value(1)])
                else:
                    if (iterator.value(1) >= self._layer._color[i]['min'] and
                            iterator.value(1) <= self._layer._color[i]['max']):
                        array[i].append(iterator.value(0))
        return array

    def _get_result_categorized_symbol(self, iterator):
        nbColor = len(self._layer._color)
        array = [[] for i in range(nbColor)]

        while iterator.next():
            for i in range(nbColor):
                if self.hasH:
                    if iterator.value(2) == self._layer._color[i]['value']:
                        array[i].append([iterator.value(0), iterator.value(1)])
                else:
                    if iterator.value(1) == self._layer._color[i]['value']:
                        array[i].append(iterator.value(0))
        return array

    ## _get_request send a request to catch the type of the data
    #  @return the request
    def _get_request(self):
        # Request TIN geometry
        if (self.geometry1 == 'TIN' or
                self.geometry2 == 'TIN'):
            self.retGeometry = 'TIN'
            request = self._request_tin()

        # Request polyhedralsurface geometry
        # Very long request because geometries need to be tesselated
        elif (self.geometry1 == 'POLYHEDRALSURFACE' or
                self.geometry2 == 'POLYHEDRALSURFACE'):
            self.retGeometry = 'POLYHEDRALSURFACE'
            request = self._request_polyh()

        # Request point, line or multiline geometry
        elif (self.geometry1 == 'POINT' or
                self.geometry1 == 'LINESTRING' or
                self.geometry1 == 'MULTILINESTRING'):
            self.retGeometry = self.geometry1
            request = self._request_point_line()

        # Request polygon or multipolygon geometry
        elif (self.geometry1 == 'POLYGON' or
                self.geometry1 == 'MULTIPOLYGON'):
            self.retGeometry = self.geometry1
            request = self._request_polygon()

        # Can't request this kink of geometry
        else:
            pass
            #Multipoint, others...

        if self._layer._columnColor is not None:
            request = re.sub("FROM", ", " + self._layer._columnColor + " FROM", request)

        return request

    ## _request_point_line to request point or line data
    #  @return the request for data point or line
    def _request_point_line(self):
        if self._layer._column2 is None or self._layer._typeColumn2 == 'geometry':
            return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self._layer._column,
                       table_=self._layer._table)

        else:
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self._layer._column,
                       hcolumn_=self._layer._column2,
                       table_=self._layer._table)

    ## _request_polygon to request polygon data
    #  @return the request for data polygon
    def _request_polygon(self):
        if self._layer._column2 is None or self._layer._typeColumn2 == 'geometry':
            return """SELECT ST_AsGeoJSON(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self._layer._column,
                       table_=self._layer._table)

        else:
            return """SELECT ST_AsGeoJSON(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self._layer._column,
                       hcolumn_=self._layer._column2,
                       table_=self._layer._table)

    ## _request_polyh to request polyhedral data
    #  @return the request for data polyhedral
    def _request_polyh(self):
        # SHOULD BE PATIENT
        if self.geometry1 == 'POLYHEDRALSURFACE':
            col = self._layer._column
        else:
            col = self._layer._column2
        return """SELECT ST_AsX3D(ST_Tesselate({column_})) FROM {table_}
        """.format(column_=col,
                   table_=self._layer._table)

    ## _request_tin to request tin data
    #  @return the request for data tin
    def _request_tin(self):
        if self.geometry1 == 'TIN':
            col = self._layer._column
        else:
            col = self._layer._column2
        return """SELECT ST_AsX3D({column_}) FROM {table_}
        """.format(column_=col,
                   table_=self._layer._table)

    def _color_array(self):
        array = []
        nbColor = len(self._layer._color)
        if nbColor == 1:
            array.append(self._layer._color[0]['color'])
            return array
        else:
            for i in range(nbColor):
                array.append(self._layer._color[i]['color'])
            return array

    ## Return columns and types of a specific table
    #  @param host to define the host of the database
    #  @param dbname to define the database
    #  @param user to define the user of the database
    #  @param password to define the password of the user
    #  @param table to define the table in the database
    #  @return the result of the request
    @staticmethod
    def get_columns_info_table(layer):
        db = QSqlDatabase.addDatabase("QPSQL")
        db.setHostName(layer._host)
        db.setDatabaseName(layer._dbname)
        db.setUserName(layer._user)
        db.setPassword(layer._password)
        if db.open():
            query = QSqlQuery(db)
            st = layer._table.split('.')
            st[0] = re.sub('"', '\'', st[0])
            st[1] = re.sub('"', '\'', st[1])
            getInfo = """
                SELECT column_name, udt_name
                FROM information_schema.columns
                WHERE table_name = {table_} AND table_schema = {schema_}
                ORDER BY column_name;
            """.format(table_=st[1], schema_=st[0])
            query.exec_(getInfo)
            result = {}
            while query.next():
                result[query.value(0)] = query.value(1)
            return result
        else:
            raise Exception('Connection to database cannot be established')