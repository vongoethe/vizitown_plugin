from vt_utils_singleton import Singleton
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
    def __init__(self, host, dbname, user, password, srid, table):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(host)
        self.db.setDatabaseName(dbname)
        self.db.setUserName(user)
        self.db.setPassword(password)
        self.table = table
        self.column = None
        self.srid = srid

        if self.db.open():
            print "Connection established to database %s -> %s" % (host, dbname)
        else:
            raise Exception('Connection to database cannot be established')

    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        query = QSqlQuery(self.db)
        query.prepare("""
            SELECT ST_AsGeoJSON(:column)
            FROM :table
            WHERE ST_Intersects(geom, ST_GeomFromText(
                'POLYGON((
                    :Xmin :Ymin,
                    :Xmax :Ymin,
                    :Xmax :Ymax,
                    :Xmin :Ymax,
                    :Xmin :Ymin))',
                :srid)
            );
        """)
        query.bindValue(":column", self.column)
        query.bindValue(":table", self.table)
        query.bindValue(":Xmin", Xmin)
        query.bindValue(":Ymin", Ymin)
        query.bindValue(":Xmax", Xmax)
        query.bindValue(":Ymax", Ymax)
        query.bindValue(":srid", self.srid)
        query.exec_()
        result = []
        while query.next():
            result.append(query.value(0))
        return result


class RasterProvider:
    def __init__(self, name, exent, srid, source, httpRessource):
        self.name = name
        self.extent = extent
        self.srid = srid
        self.source = source
        self.httpRessource = httpRessource

    def requestTile(self, Xmin, Ymin, Xmax, Ymax):
        pass
