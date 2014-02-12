from vt_utils_singleton import Singleton
from PyQt4.QtCore import *
from PyQt4.QtSql import *


## Provider manager
#  Singleton which contains several provider
@Singleton
class ProviderManager:
    def __init__(self):
        self.vectors = []
        self.dem = None
        self.raster = None

    ## Add a provider to the manager
    #  @param p the provider to add
    def addVectorProvider(self, p):
        self.vectors.append(p)

    ## Request a tile for all his providers
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        result = []
        for p in self.vectors:
            result.append(p.requestTile(Xmin, Ymin, Xmax, Ymax))
        return result


## Raster provider
#  Stock the attribute to use a raster resource
class PostgisProvider:
    ## Constructor
    #  @param host database host
    #  @param dbname database name
    #  @param user database user
    #  @param password database user password
    #  @param srid of the resource
    #  @param table of the resource
    #  @param column of the resource
    def __init__(self, host, dbname, user, password, srid, table, column):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(host)
        self.db.setDatabaseName(dbname)
        self.db.setUserName(user)
        self.db.setPassword(password)
        self.table = table
        self.column = column
        self.srid = srid
        self.geometry = ""

        if self.db.open():
            print "Connection established to database %s -> %s" % (host, dbname)

            query = QSqlQuery(self.db)
            getGeometry = "SELECT GeometryType({column_}) FROM {table_} LIMIT 1".format(column_=column, table_=table)
            query.exec_(getGeometry)
            query.next()
            self.geometry = query.value(0)
        else:
            raise Exception('Connection to database cannot be established')

    ## Return all the result contains in the extent in param
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db)
        request = ""

        extent = """POLYGON(({Xmin_} {Ymin_}, {Xmax_} {Ymin_}, {Xmax_} {Ymax_}, {Xmin_} {Ymax_}, {Xmin_} {Ymin_}))
        """.format(Xmin_=Xmin,
                   Xmax_=Xmax,
                   Ymin_=Ymin,
                   Ymax_=Ymax)

        intersect = " WHERE ST_Intersects({column_}, ST_GeomFromText('{extent_}', {srid_}))".format(extent_=extent, srid_=self.srid, column_=self.column)

        if (self.geometry == 'POINT' or
                self.geometry == 'LINESTRING' or
                self.geometry == 'MULTILINESTRING'):
            request = self._request_point_line()

        elif (self.geometry == 'POLYGONE' or
                self.geometry == 'POLYHEDRALSURFACE'):
            request = self._request_triangulate()

        else:
            # Multipoint, multipolygon, others...
            raise Exception('Can\'t request this kind of geometry')

        request += intersect
        print request
        if not query.exec_(request):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')

        return {'it': query, 'geom': self.geometry}

    def _request_point_line(self):
        return "SELECT ST_AsX3D(ST_Force3D({column_})) FROM {table_}".format(column_=self.column, table_=self.table)

    def _request_triangulate(self):
        return "SELECT ST_AsX3D(ST_Tesselate(ST_Force3D({column_}))) FROM {table_}".format(column_=self.column, table_=self.table)


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

    ## Undefined for raster
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        pass
