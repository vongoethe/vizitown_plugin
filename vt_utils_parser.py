import re
import vt_as_providers


def vectorToPostgisProvider(source):
    m = re.match(r"dbname='(?P<dbname>.*?)' host=(?P<host>\w+) port=(?P<port>\d+) user='(?P<user>.*?)' password='(?P<password>.*?)' .* srid=(?P<srid>\d+) .* table=(?P<table>\S+)'", source)
    return vt_as_providers.PostgisProvider(m.group('host'), 
                                           m.group('dbname'),
                                           m.group('user'),
                                           m.group('password'),
                                           m.group('srid'),
                                           m.group('table'))
