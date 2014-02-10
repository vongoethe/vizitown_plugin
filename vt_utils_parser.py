import re
import vt_as_providers


def vectorToPostgisProvider(source):
    print source
    m = re.match(r"dbname='(?P<dbname>.*?)' host=(?P<host>\d+.\d+.\d+.\d+) port=(?P<port>\d+) user='(?P<user>.*?)' password='(?P<password>.*?)' .* srid=(?P<srid>\d+) .* table=(?P<table>\S+) \((?P<column>.*?)\)", source)
    return vt_as_providers.PostgisProvider(m.group('host'), 
                                           m.group('dbname'),
                                           m.group('user'),
                                           m.group('password'),
                                           m.group('srid'),
                                           m.group('table'),
                                           m.group('column'))
