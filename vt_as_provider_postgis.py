import re

from PyQt4.QtCore import *
from PyQt4.QtSql import *


## Postgis provider
#  Stock the attribute to use a postgis resource
class PostgisProvider:

    ## Constructor
    #  @param _layer
    def __init__(self, layer):
        self.db = QSqlDatabase.addDatabase("QPSQL", layer._uuid)
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
        else:
            self.hasH = False

        if self._layer._typeColumn2 == 'geometry':
            getGeometry = """SELECT GeometryType({column_}), GeometryType({column2_}) FROM {table_} LIMIT 1
            """.format(column_=self._layer._column,
                       column2_=self._layer._column2,
                       table_=self._layer._table)
            if not query.exec_(getGeometry):
                print query.lastQuery()
                print query.lastError().text()
                raise Exception('DB request failed')

            while query.next():
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

            while query.next():
                self.geometry1 = query.value(0)

    ## request_tile method
    #  Return all the result contains in the extent in param
    #  @param Xmin
    #  @param Ymin
    #  @param Xmax
    #  @param Ymax
    #  @return the tile
    def request_tile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db.database(self._layer._uuid))
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

        pExtent = """ST_GeomFromText('{extent_}', {srid_})
        """.format(extent_=extent,
                   srid_=self._layer._srid)

        request = self._get_request(pExtent)

        if not query.exec_(request):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')

        results = self._sort_result(query)
        colors = self._color_array()
        return {'results': results, 'geom': self.retGeometry, 'hasH': self.hasH, 'color': colors, 'uuid': self._layer._uuid}

    ## sort_result method
    #  Sort the request result in function of the type of symbology apply on the data
    #  @param iterator
    #  @return the table with the data and associated symbol
    def _sort_result(self, iterator):
        colorType = self._layer.get_color_type()
        if (colorType == "singleSymbol"):
            return self._get_result_single_symbol(iterator)

        elif (colorType == "graduatedSymbol"):
            return self._get_result_graduated_symbol(iterator)

        elif (colorType == "categorizedSymbol"):
            return self._get_result_categorized_symbol(iterator)

    ## _get_result_single_symbol method
    #  Run through the iterator to check the associated symbol
    #  @param iterator
    #  @return the table with the data and associated symbol
    def _get_result_single_symbol(self, iterator):
        array = [[]]
        while iterator.next():
            if self.hasH:
                array[0].append([iterator.value(0), iterator.value(1)])
            else:
                array[0].append(iterator.value(0))
        return array

    ## _get_result_graduated_symbol method
    #  Run through the iterator to check the associated symbol and sorted it
    #  @param iterator
    #  @return the table with the data and associated symbol
    def _get_result_graduated_symbol(self, iterator):
        nbColor = len(self._layer._color)
        array = [[] for i in range(nbColor)]

        while iterator.next():
            for i in range(nbColor):
                if self.hasH:
                    if (iterator.value(2) > self._layer._color[i]['min'] and
                            iterator.value(2) <= self._layer._color[i]['max']):
                        array[i].append([iterator.value(0), iterator.value(1)])
                else:
                    if (iterator.value(1) > self._layer._color[i]['min'] and
                            iterator.value(1) <= self._layer._color[i]['max']):
                        array[i].append(iterator.value(0))
        return array

    ## _get_result_categorized_symbol method
    #  Run through the iterator to check the associated symbol and sorted it
    #  @param iterator
    #  @return the table with the data and associated symbol
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

    ## _get_request method
    #  Send a request to catch the type of the data
    #  @return the request
    def _get_request(self, pExtent):
        # Request TIN geometry
        if (self.geometry1 == 'TIN' or
                self.geometry2 == 'TIN'):
            self.retGeometry = 'TIN'
            request = self._request_tin(pExtent)

        # Request polyhedralsurface geometry
        # Very long request because geometries need to be tesselated
        elif (self.geometry1 == 'POLYHEDRALSURFACE' or
                self.geometry2 == 'POLYHEDRALSURFACE'):
            self.retGeometry = 'POLYHEDRALSURFACE'
            request = self._request_polyh(pExtent)

        # Request point, line or multiline geometry
        elif (self.geometry1 == 'POINT' or
                self.geometry1 == 'LINESTRING' or
                self.geometry1 == 'MULTILINESTRING'):
            self.retGeometry = self.geometry1
            request = self._request_point_line(pExtent)

        # Request polygon or multipolygon geometry
        elif (self.geometry1 == 'POLYGON' or
                self.geometry1 == 'MULTIPOLYGON'):
            self.retGeometry = self.geometry1
            request = self._request_polygon(pExtent)

        # Can't request this kink of geometry
        else:
            pass
            #Multipoint, others...

        if self._layer._columnColor is not None:
            request = re.sub("FROM", ", " + self._layer._columnColor + " FROM", request)

        return request

    ## _request_point_line method
    #  Request point or line data
    #  @return the request for data point or line
    def _request_point_line(self, pExtent):
        if self._layer._column2 is None or self._layer._typeColumn2 == 'geometry':
            return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
            WHERE ST_Intersects(ST_Centroid({column_}), {pExtent_})
            """.format(column_=self._layer._column,
                       table_=self._layer._table,
                       pExtent_=pExtent)

        else:
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            WHERE ST_Intersects(ST_Centroid({column_}), {pExtent_})
            """.format(column_=self._layer._column,
                       hcolumn_=self._layer._column2,
                       table_=self._layer._table,
                       pExtent_=pExtent)

    ## _request_polygon method
    #  Request polygon data
    #  @return the request for data polygon
    def _request_polygon(self, pExtent):
        if self._layer._column2 is None or self._layer._typeColumn2 == 'geometry':
            return """SELECT ST_AsGeoJSON(ST_Force3D({column_})) FROM {table_}
            WHERE ST_Intersects(ST_Centroid({column_}), {pExtent_})
            """.format(column_=self._layer._column,
                       table_=self._layer._table,
                       pExtent_=pExtent)

        else:
            return """SELECT ST_AsGeoJSON(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            WHERE ST_Intersects(ST_Centroid({column_}), {pExtent_})
            """.format(column_=self._layer._column,
                       hcolumn_=self._layer._column2,
                       table_=self._layer._table,
                       pExtent_=pExtent)

    ## _request_polyh method
    #  Request polyhedral data
    #  @return the request for data polyhedral
    def _request_polyh(self, pExtent):
        # SHOULD BE PATIENT
        if self.geometry1 == 'POLYHEDRALSURFACE':
            col = self._layer._column
        else:
            col = self._layer._column2
        return """SELECT ST_AsX3D(ST_Tesselate({column_})) FROM {table_}
        WHERE {column_} && {pExtent_}
        """.format(column_=col,
                   table_=self._layer._table,
                   pExtent_=pExtent)

    ## _request_tin
    #  Request tin data
    #  @return the request for data tin
    def _request_tin(self, pExtent):
        if self.geometry1 == 'TIN':
            col = self._layer._column
        else:
            col = self._layer._column2
        return """SELECT ST_AsX3D({column_}) FROM {table_}
        WHERE {column_} && {pExtent_}
        """.format(column_=col,
                   table_=self._layer._table,
                   pExtent_=pExtent)

    ## _color_array method
    #  Create an arry with all color of the layer
    #  @return the array
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

    ## get_columns_info_table static method
    #  Return columns and types of a specific table
    #  @param layer to access at the table
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