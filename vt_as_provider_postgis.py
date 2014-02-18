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
    #  @param column of the resource
    #  @param column2 representing a height of column or another geometry (TinZ)
    def __init__(self, host, dbname, port, user, password, srid, table, column, color, column2=None, column2Type=None):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(host)
        self.db.setDatabaseName(dbname)
        self.db.setPort(port)
        self.db.setUserName(user)
        self.db.setPassword(password)
        self.table = table
        self.column = column
        self.column2 = column2
        self.column2Type = column2Type
        self.srid = srid
        self.geometry1 = None
        self.geometry2 = None
        self.retGeometry = None
        self.hasH = False
        self.color = color

        if not self.db.open():
            raise Exception('Connection to database cannot be established')

        print "Connection established to database %s -> %s" % (host, dbname)

        query = QSqlQuery(self.db)

        if self.column2Type == 'geometry':
            getGeometry = """SELECT GeometryType({column_}), GeometryType({column2_}) FROM {table_} LIMIT 1
            """.format(column_=column,
                       column2_=column2,
                       table_=table)
            if query.exec_(getGeometry):
                query.next()
                self.geometry1 = query.value(0)
                self.geometry2 = query.value(1)
            else:
                print query.lastQuery()
                print query.lastError().text()
                raise Exception('DB request failed')

        else:
            getGeometry = """SELECT GeometryType({column_}) FROM {table_} LIMIT 1
            """.format(column_=column,
                       table_=table)
            if query.exec_(getGeometry):
                query.next()
                self.geometry1 = query.value(0)
            else:
                print query.lastQuery()
                print query.lastError().text()
                raise Exception('DB request failed')

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
        """.format(column_=self.column,
                   extent_=extent,
                   srid_=self.srid)

        request = self._get_request()
        request += intersect

        if not query.exec_(request):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')

        return {'it': query, 'geom': self.retGeometry, 'hasH': self.hasH, 'color': self.color}

    ## _get_request send a request to catch the type of the data
    #  @return the request
    def _get_request(self):
        if (self.geometry1 == 'TIN' or
                self.geometry2 == 'TIN'):
            self.retGeometry = 'TIN'
            request = self._request_tin()

        elif (self.geometry1 == 'POLYHEDRALSURFACE' or
                self.geometry2 == 'POLYHEDRALSURFACE'):
            self.retGeometry = 'POLYHEDRALSURFACE'
            request = self._request_polyh()

        elif (self.geometry1 == 'POINT' or
                self.geometry1 == 'LINESTRING' or
                self.geometry1 == 'MULTILINESTRING'):
            self.retGeometry = self.geometry1
            request = self._request_point_line()

        elif (self.geometry1 == 'POLYGON' or
                self.geometry1 == 'MULTIPOLYGON'):
            self.retGeometry = self.geometry1
            request = self._request_polygon()

        else:
            pass
            #Multipoint, others...
            #print self.geometry1
            #raise Exception('Can\'t request this kind of geometry')

        return request

    ## _request_point_line to request point or line data
    #  @return the request for data point or line
    def _request_point_line(self):
        if self.column2 is None or self.column2Type == 'geometry':
            return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self.column,
                       table_=self.table)

        else:
            self.hasH = True
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self.column,
                       hcolumn_=self.column2,
                       table_=self.table)

    ## _request_polygon to request polygon data
    #  @return the request for data polygon
    def _request_polygon(self):
        if self.column2 is None or self.column2Type == 'geometry':
            return """SELECT ST_AsGeoJSON(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self.column,
                       table_=self.table)

        else:
            self.hasH = True
            return """SELECT ST_AsGeoJSON(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self.column,
                       hcolumn_=self.column2,
                       table_=self.table)

    ## _request_point_line to request polyhedral data
    #  @return the request for data polyhedral
    def _request_polyh(self):
        # SHOULD BE PATIENT
        if self.geometry1 == 'POLYHEDRALSURFACE':
            col = self.column
        else:
            col = self.column2
        return """SELECT ST_AsX3D(ST_Tesselate({column_})) FROM {table_}
        """.format(column_=col,
                   table_=self.table)

    ## _request_point_line to request tin data
    #  @return the request for data tin
    def _request_tin(self):
        if self.geometry1 == 'TIN':
            col = self.column
        else:
            col = self.column2
        return """SELECT ST_AsX3D({column_}) FROM {table_}
        """.format(column_=col,
                   table_=self.table)

    ## Return columns and types of a specific table
    #  @param host to define the host of the database
    #  @param dbname to define the database
    #  @param user to define the user of the database
    #  @param password to define the password of the user
    #  @param table to define the table in the database
    #  @return the result of the request
    @staticmethod
    def get_columns_info_table(host, dbname, user, password, table):
        db = QSqlDatabase.addDatabase("QPSQL")
        db.setHostName(host)
        db.setDatabaseName(dbname)
        db.setUserName(user)
        db.setPassword(password)
        if db.open():
            query = QSqlQuery(db)
            st = table.split('.')
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
