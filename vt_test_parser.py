import unittest
import vt_utils_parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.source = """
        dbname='data' host=12.12.12.12 port=5432 user='lecture' password='pass' key='gid' srid=2154 type=MULTIPOLYGON table=\"public\".\"mnt_tin\" (geom) sql=
        """

    def test_parse_vector(self):
        result = vt_utils_parser.parse_vector(self.source, "2154")
        self.assertEqual(result['dbname'], 'data', 'Parsing dbname fail')
        self.assertEqual(result['host'], '12.12.12.12', 'Parsing host fail')
        self.assertEqual(result['port'], 5432, 'Parsing port fail')
        self.assertEqual(result['user'], 'lecture', 'Parsing user fail')
        self.assertEqual(result['password'], 'pass', 'Parsing password fail')
        self.assertEqual(result['srid'], '2154', 'Parsing srid fail')
        self.assertEqual(result['table'], '\"public\".\"mnt_tin\"', 'Parsing table fail')
        self.assertEqual(result['column'], 'geom', 'Parsing column fail')

if __name__ == "__main__":
    unittest.main()