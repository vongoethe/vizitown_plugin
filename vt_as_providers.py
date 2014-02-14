from vt_utils_singleton import Singleton
from vt_utils_converter import X3DTranslateToThreeJs
from PyQt4.QtCore import *
from PyQt4.QtSql import *


## Provider manager
#  Singleton which contains several provider
@Singleton
class ProviderManager:
    def __init__(self):
<<<<<<< HEAD
        self.providers = []
=======
        self.vectors = []
        self.dem = None
        self.texture = None
>>>>>>> camille/new_ui

    ## Add a provider to the manager
    #  @param p the provider to add
    def addProvider(self, p):
        self.providers.append(p)

    ## Request a tile for all his providers
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        result = []
        for p in self.providers:
            result.append(p.requestTile(Xmin, Ymin, Xmax, Ymax))
        return result


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
    def __init__(self, host, dbname, user, password, srid, table, column, column2, column2Type):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(host)
        self.db.setDatabaseName(dbname)
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
        self.translator = X3DTranslateToThreeJs()
        print "Instantiate PostgisProvider"

        if self.db.open():
            print "Connection established to database %s -> %s" % (host, dbname)

            query = QSqlQuery(self.db)

            if self.column2Type == 'geometry':
                getGeometry = """SELECT GeometryType({column_}), GeometryType({column2_}) FROM {table_} LIMIT 1
<<<<<<< HEAD
                """.format(column_=column,
=======
                """.format(column_=column, 
>>>>>>> camille/new_ui
                           column2_=column2,
                           table_=table)
                if query.exec_(getGeometry):
                    query.next()
                    self.geometry1 = query.value(0).toString()
                    self.geometry2 = query.value(1).toString()
                else:
                    print query.lastQuery()
                    print query.lastError().text()
                    raise Exception('DB request failed')

            else:
                getGeometry = """SELECT GeometryType({column_}) FROM {table_} LIMIT 1
<<<<<<< HEAD
                """.format(column_=column,
=======
                """.format(column_=column, 
>>>>>>> camille/new_ui
                           table_=table)
                if query.exec_(getGeometry):
                    query.next()
                    self.geometry1 = query.value(0).toString()
                else:
                    print query.lastQuery()
                    print query.lastError().text()
                    raise Exception('DB request failed')

        else:
            raise Exception('Connection to database cannot be established')

    ## Return all the result contains in the extent in param
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db)
        request = ""

<<<<<<< HEAD
        extent = """POLYGON(({Xmin_} {Ymin_},
                             {Xmax_} {Ymin_},
                             {Xmax_} {Ymax_},
                             {Xmin_} {Ymax_},
                             {Xmin_} {Ymin_}))
=======
        extent = """POLYGON(({Xmin_} {Ymin_}, 
                             {Xmax_} {Ymin_}, 
                             {Xmax_} {Ymax_}, 
                             {Xmin_} {Ymax_}, 
                             {Xmin_} {Ymin_}))  
>>>>>>> camille/new_ui
        """.format(Xmin_=Xmin,
                   Xmax_=Xmax,
                   Ymin_=Ymin,
                   Ymax_=Ymax)

        intersect = """ WHERE {column_} && ST_GeomFromText('{extent_}', {srid_})
        """.format(column_=column,
                   extent_=extent,
                   srid_=self.srid)

        request = self._get_request()
        request += intersect
<<<<<<< HEAD

=======
        
>>>>>>> camille/new_ui
        ## LOG DEBUG
        print request

        if not query.exec_(request):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')

        return {'it': query, 'geom': self.retGeometry, 'hasH': self.hasH}

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
            #Multipoint, others...
            raise Exception('Can\'t request this kind of geometry')

        return request

    def _request_point_line(self):
        if self.column2 is None or self.column2Type == 'geometry':
            return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self.column,
                       table_=self.table)
<<<<<<< HEAD

        else:
            self.hasH = True
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self.column,
                       hcolumn_=column2,
                       table_=self.table)

    def _request_polygon(self):
        if self.column2 is None or self.column2Type == 'geometry':
            return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self.column,
                       table_=self.table)

        else:
            self.hasH = True
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self.column,
                       hcolumn_=column2,
                       table_=self.table)

    def _request_polyh(self):
        # SHOULD BE PATIENT
        if self.geometry1 == 'POLYHEDRALSURFACE':
            col = self.column
        else:
            col = self.column2
        return """SELECT ST_AsX3D(ST_Tesselate(ST_Force3D({column_}))) FROM {table_}
        """.format(column_=col,
                   table_=self.table)

    def _request_tin(self):
        if self.geometry1 == 'TIN':
            col = self.column
        else:
            col = self.column2
        return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
        """.format(column_=col,
                   table_=self.table)
=======

        else:
            self.hasH = True
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self.column,
                       hcolumn_=column2,
                       table_=self.table)

    def _request_polygon(self):
        if self.column2 is None or self.column2Type == 'geometry':
            return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
            """.format(column_=self.column,
                       table_=self.table)

        else:
            self.hasH = True
            return """SELECT ST_AsX3D(ST_Force3D({column_})), {hcolumn_} FROM {table_}
            """.format(column_=self.column,
                       hcolumn_=column2,
                       table_=self.table)     

    def _request_polyh(self):
        # SHOULD BE PATIENT
        if self.geometry1 == 'POLYHEDRALSURFACE':
            col = self.column
        else:
            col = self.column2
        return """SELECT ST_AsX3D(ST_Tesselate(ST_Force3D({column_}))) FROM {table_}
        """.format(column_=col, 
                   table_=self.table)

    def _request_tin(self):
        if self.geometry1 == 'TIN':
            col = self.column
        else:
            col = self.column2
        return """SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}
        """.format(column_=col,
                   table_=self.table)

>>>>>>> camille/new_ui


## Raster provider
#  Stock the attribute to use a raster resource
class RasterProvider:
    ## Constructor
    #  @param name of the raster
    #  @param extent of the raster
    #  @param srid of the raster
    #  @param source local path of the raster
    #  @param httpRessource URL location
    def __init__(self, name, extent, srid, source, httpRessource):
        self.name = name
        self.extent = extent
        self.srid = srid
        self.source = source
        self.httpRessource = httpRessource
<<<<<<< HEAD

    ## Undefined for raster
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        pass
=======
>>>>>>> camille/new_ui
