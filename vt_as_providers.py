from vt_utils_singleton import Singleton
from PyQt4.QtCore import *
from PyQt4.QtSql import *


@Singleton
class ProviderManager:
    def __init__(self):
        self.providers = []

    def addProvider(self, p):
        self.providers.append(p)

    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        result = []
        for p in self.providers:
            result.append(p.requestTile(Xmin, Ymin, Xmax, Ymax))
        return result


class PostgisProvider:
    def __init__(self, host, dbname, user, password, srid, table, column):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(host)
        self.db.setDatabaseName(dbname)
        self.db.setUserName(user)
        self.db.setPassword(password)
        self.table = table
        self.column = column
        self.srid = srid

        if self.db.open():
            print "Connection established to database %s -> %s" % (host, dbname)
        else:
            raise Exception('Connection to database cannot be established')

    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db)

        polygon = "POLYGON(({Xmin_} {Ymin_}, {Xmax_} {Ymin_}, {Xmax_} {Ymax_}, {Xmin_} {Ymax_}, {Xmin_} {Ymin_}))".format(Xmin_=Xmin,
                                                                                                                          Xmax_=Xmax,
                                                                                                                          Ymin_=Ymin,
                                                                                                                          Ymax_=Ymax)
        q = "SELECT ST_AsGeoJSON({column_}) FROM {table_} WHERE ST_Intersects(geom, ST_GeomFromText('{polygon_}', {srid_}))".format(column_=self.column,
                                                                                                                                    table_=self.table,
                                                                                                                                    polygon_=polygon,
                                                                                                                                    srid_=self.srid)

        if not query.exec_(q):
            print query.lastQuery()
            print query.lastError().text()
            raise Exception('DB request failed')
        result = []
        while query.next():
            print query
            result.append(query.value(0))
        return result


class RasterProvider:
    def __init__(self, name, extent, srid, source, httpRessource):
        self.name = name
        self.extent = extent
        self.srid = srid
        self.source = source
        self.httpRessource = httpRessource

    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        pass
