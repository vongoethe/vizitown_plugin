from vt_utils_singleton import Singleton
from PyQt4.QtCore import *
from PyQt4.QtSql import *


## Provider manager
#  Singleton which contains several provider
@Singleton
class ProviderManager:
    def __init__(self):
        self.providers = []

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
            getGeometry = "SELECT GeometryType({column_} FROM {table_} LIMIT 1"
            query.exec_(getGeometry)
            query.next()
            print query.value(0)
        else:
            raise Exception('Connection to database cannot be established')

    ## Return all the result contains in the extent in param
    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db)
        polygon = """POLYGON(({Xmin_} {Ymin_}, {Xmax_} {Ymin_}, {Xmax_} {Ymax_}, {Xmin_} {Ymax_}, {Xmin_} {Ymin_}))
        """.format(Xmin_=Xmin,
                   Xmax_=Xmax,
                   Ymin_=Ymin,
                   Ymax_=Ymax)
        q = """SELECT ST_AsGeoJSON({column_}) FROM {table_} WHERE ST_Intersects(geom, ST_GeomFromText('{polygon_}', {srid_}))
        """.format(column_=self.column,
                   table_=self.table,
                   polygon_=polygon,
                   srid_=self.srid)

        if not query.exec_(q):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')
        result = []
        while query.next():
            result.append(query.value(0))
        return result


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
