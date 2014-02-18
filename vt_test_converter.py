import unittest
import json
from vt_utils_converter import PostgisToJSON


class translateJSON(unittest.TestCase):

    def setUp(self):
        
        #self.point = "844134.284462888841517 6516568.605687109753489 0"
        #self.line = "<IndexedLineSet  coordIndex='0 1 2 3 4 5 6 7 8'><Coordinate point='844187.943697994574904 6518232.016619521193206 0 844201.841662708669901 6518224.785503129474819 0 844278.95548352599144 6518186.30289267282933 0 844300.016633692430332 6518175.119627367705107 0 844311.424576590536162 6518169.747550436295569 0 844410.036452979431488 6518129.295050370506942 0 844448.537077572080307 6518116.9088667454198 0 844508.316286795539781 6518103.210729259997606 0 844559.869014470255934 6518091.156238601543009 0 ' /></IndexedLineSet> "
        #self.lod1 = "<IndexedTriangleSet  index='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35'><Coordinate point='-149992.141194042400457 7859668.6658656578511 0 -149981.131755757261999 7859668.649239290505648 0 -149981.131755757261999 7859668.649239290505648 8 -149992.141194042400457 7859668.6658656578511 8 -149992.141194042400457 7859668.6658656578511 0 -149981.131755757261999 7859668.649239290505648 8 -149992.125124575686641 7859679.306463955901563 8 -149981.131755757261999 7859668.649239290505648 8 -149981.115686494740658 7859679.289837553165853 8 -149992.125124575686641 7859679.306463955901563 8 -149992.141194042400457 7859668.6658656578511 8 -149981.131755757261999 7859668.649239290505648 8 -149981.115686494740658 7859679.289837553165853 8 -149981.131755757261999 7859668.649239290505648 0 -149981.115686494740658 7859679.289837553165853 0 -149981.115686494740658 7859679.289837553165853 8 -149981.131755757261999 7859668.649239290505648 8 -149981.131755757261999 7859668.649239290505648 0 -149992.125124575686641 7859679.306463955901563 0 -149992.141194042400457 7859668.6658656578511 8 -149992.125124575686641 7859679.306463955901563 8 -149992.125124575686641 7859679.306463955901563 0 -149992.141194042400457 7859668.6658656578511 0 -149992.141194042400457 7859668.6658656578511 8 -149981.115686494740658 7859679.289837553165853 0 -149992.125124575686641 7859679.306463955901563 8 -149981.115686494740658 7859679.289837553165853 8 -149981.115686494740658 7859679.289837553165853 0 -149992.125124575686641 7859679.306463955901563 0 -149992.125124575686641 7859679.306463955901563 8 -149981.131755757261999 7859668.649239290505648 0 -149992.125124575686641 7859679.306463955901563 0 -149981.115686494740658 7859679.289837553165853 0 -149981.131755757261999 7859668.649239290505648 0 -149992.141194042400457 7859668.6658656578511 0 -149992.125124575686641 7859679.306463955901563 0'/></IndexedTriangleSet>"
        self.oneSimplePoint = ["844134.284462888841517 6516568.605687109753489 0"]
        self.twoPointsHeight = [["844134.284462888841517 6516568.605687109753489 0", "10"], ["144134.284462888841517 6516568.605687109753489 0", "25"]]

        self.lineSimple = ["<IndexedLineSet  coordIndex='0 1 2 3 4'><Coordinate point='847423.133840369875543 6519126.773986855521798 0 847427.16084886121098 6519029.311356557533145 0 847431.001942750066519 6518961.135681151412427 0 847435.155744896968827 6518878.69126517791301 0 847435.500586390029639 6518853.990726242773235 0 ' /></IndexedLineSet>"]
        self.lineWithHeight = [["<IndexedLineSet  coordIndex='0 1 2 3 4'><Coordinate point='847423.133840369875543 6519126.773986855521798 0 847427.16084886121098 6519029.311356557533145 0 847431.001942750066519 6518961.135681151412427 0 847435.155744896968827 6518878.69126517791301 0 847435.500586390029639 6518853.990726242773235 0 ' /></IndexedLineSet>", "10"]]

        self.polygon = ['{"type":"Polygon","coordinates":[[[852321.383846897,6509501.96687314,0],[852320.082282889,6509513.99731137,0],[852322.110674802,6509514.19758986,0],[852322.79144221,6509508.14240802,0],[852323.452207997,6509502.16716017,0],[852321.383846897,6509501.96687314,0]]]}']
        self.multipolygon = ['{"type":"MultiPolygon", "coordinates": [[[[30, 20, 0], [45, 40, 0], [10, 40, 0], [30, 20, 0]]], [[[15, 5, 0], [40, 10, 0], [10, 20, 0], [5, 10, 0], [15, 5, 0]]]]}']

        self.tin = ["<IndexedTriangleSet  index='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35'><Coordinate point='852320.082282889052294 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 0 852323.452207996975631 6509501.966873140074313 11 852320.082282889052294 6509501.966873140074313 11 852320.082282889052294 6509501.966873140074313 0 852323.452207996975631 6509501.966873140074313 0 852320.082282889052294 6509514.19758986029774 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509514.19758986029774 11 852320.082282889052294 6509514.19758986029774 11 852320.082282889052294 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 0 852323.452207996975631 6509514.19758986029774 0 852323.452207996975631 6509514.19758986029774 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509514.19758986029774 0 852320.082282889052294 6509501.966873140074313 0 852320.082282889052294 6509501.966873140074313 11 852320.082282889052294 6509514.19758986029774 11 852320.082282889052294 6509514.19758986029774 0 852320.082282889052294 6509501.966873140074313 0 852320.082282889052294 6509514.19758986029774 11 852320.082282889052294 6509514.19758986029774 0 852320.082282889052294 6509514.19758986029774 11 852323.452207996975631 6509514.19758986029774 11 852323.452207996975631 6509514.19758986029774 0 852320.082282889052294 6509514.19758986029774 0 852323.452207996975631 6509514.19758986029774 11 852320.082282889052294 6509501.966873140074313 0 852320.082282889052294 6509514.19758986029774 0 852323.452207996975631 6509514.19758986029774 0 852323.452207996975631 6509501.966873140074313 0 852320.082282889052294 6509501.966873140074313 0 852323.452207996975631 6509514.19758986029774 0'/></IndexedTriangleSet>"]

        self.hasHeight = True
        self.noHeight = False

        self.geomPoint = 'POINT'
        self.geomLine = 'LINESTRING'
        self.geomPolyg = 'POLYGON'
        self.geomMPolyg = 'MULTIPOLYGON'
        self.geomPolyh = 'POLYHEDRALSURFACE'

        self.translator = PostgisToJSON()

    # ONE POINT NO HEIGHT
    def test_json_one_point_check_type(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight)
        jsonOnePoint = json.loads(ret)
        self.assertEqual(jsonOnePoint['type'], "2")

    def test_json_one_pont_check_nb_geometry(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight)
        jsonOnePoint = json.loads(ret)
        geometries = jsonOnePoint['geometries']
        self.assertEqual(len(geometries), 1)

    def test_json_one_point_check_coordinates(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight)
        jsonOnePoint = json.loads(ret)
        geometries = jsonOnePoint['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [844134.284462888841517, 6516568.605687109753489])

    def test_json_one_point_check_height(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight)
        jsonOnePoint = json.loads(ret)
        geometries = jsonOnePoint['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # TWO POINTS WITH HEIGHT
    def test_json_two_points_check_type(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight)
        jsonTwoPoints = json.loads(ret)
        self.assertEqual(jsonTwoPoints['type'], "2.5")

    def test_json_two_points_check_nb_geometry(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight)
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries']
        self.assertEqual(len(geometries), 2)

    def test_json_two_points_check_coordinates_point1(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight)
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [844134.284462888841517, 6516568.605687109753489])

    def test_json_two_points_check_coordinates_point2(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight)
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][1]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [144134.284462888841517, 6516568.605687109753489])

    def test_json_two_points_check_height_point1(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight)
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 10)

    def test_json_two_points_check_height_point2(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight)
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][1]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 25)

    # LINE
    def test_json_line_check_type(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight)
        jsonLine = json.loads(ret)
        self.assertEqual(jsonLine['type'], "2")

    def test_json_line_check_nb_geometry(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight)
        jsonLine = json.loads(ret)
        self.assertEqual(len(jsonLine['geometries']), 1)

    def test_json_line_check_coordinates(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight)
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [847423.133840369875543,6519126.773986855521798,847427.16084886121098,6519029.311356557533145,847431.001942750066519,6518961.135681151412427,847435.155744896968827,6518878.69126517791301,847435.500586390029639,6518853.990726242773235])

    def test_json_line_check_height(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight)
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # LINE WITH HEIGHT
    def test_json_lineH_check_type(self):
        ret = self.translator.parse(self.lineWithHeight, self.geomLine, self.hasHeight)
        jsonLine = json.loads(ret)
        self.assertEqual(jsonLine['type'], "2.5")

    def test_json_lineH_check_coordinates(self):
        ret = self.translator.parse(self.lineWithHeight, self.geomLine, self.hasHeight)
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [847423.133840369875543,6519126.773986855521798,847427.16084886121098,6519029.311356557533145,847431.001942750066519,6518961.135681151412427,847435.155744896968827,6518878.69126517791301,847435.500586390029639,6518853.990726242773235])


    def test_json_lineH_check_height(self):
        ret = self.translator.parse(self.lineWithHeight, self.geomLine, self.hasHeight)
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 10)

    # POLYGONE
    def test_json_polygon_check_type(self):
        ret = self.translator.parse(self.polygon, self.geomPolyg, self.noHeight)
        jsonPoly = json.loads(ret)
        self.assertEqual(jsonPoly['type'], "2")

    def test_json_polygon_check_coordinates(self):
        ret = self.translator.parse(self.polygon, self.geomPolyg, self.noHeight)
        jsonPoly = json.loads(ret)
        geometries = jsonPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [852321.383847,6509501.96687,852320.082283,6509513.99731,852322.110675,6509514.19759,852322.791442,6509508.14241,852323.452208,6509502.16716,852321.383847,6509501.96687])

    def test_json_polygon_check_height(self):
        ret = self.translator.parse(self.polygon, self.geomPolyg, self.noHeight)
        jsonPoly = json.loads(ret)
        geometries = jsonPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # MULTIPOLYGON
    def test_json_multipolygon_check_type(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight)
        jsonMPoly = json.loads(ret)
        self.assertEqual(jsonMPoly['type'], "2")

    def test_json_two_points_check_nb_geometry(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight)
        jsonMPoly = json.loads(ret)
        geometries = jsonMPoly['geometries']
        self.assertEqual(len(geometries), 2)

    def test_json_multipolygon_check_coordinates_poly1(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight)
        jsonMPoly = json.loads(ret)
        geometries = jsonMPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [30, 20, 45, 40, 10, 40, 30, 20])

    def test_json_multipolygon_check_coordinates_poly2(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight)
        jsonMPoly = json.loads(ret)
        geometries = jsonMPoly['geometries'][1]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [15, 5, 40, 10, 10, 20, 5, 10, 15, 5])

    def test_json_multipolygon_check_height(self):
        ret = self.translator.parse(self.polygon, self.geomMPolyg, self.noHeight)
        jsonPoly = json.loads(ret)
        geometries = jsonPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # TIN
    def test_json_tin_check_type(self):
        ret = self.translator.parse(self.tin, self.geomPolyh, self.noHeight)
        jsonPolyh = json.loads(ret)
        self.assertEqual(jsonPolyh['type'], "3")

    def test_json_tin_check_nb_faces(self):
        ret = self.translator.parse(self.tin, self.geomPolyh, self.noHeight)
        jsonPolyh = json.loads(ret)
        geometries = jsonPolyh['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        metadata = json.loads(json.dumps(geometry['metadata']))    
        self.assertEqual(metadata['faces'], 12)
 
    def test_json_tin_check_nb_vertices(self):
        ret = self.translator.parse(self.tin, self.geomPolyh, self.noHeight)
        jsonPolyh = json.loads(ret)
        geometries = jsonPolyh['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        metadata = json.loads(json.dumps(geometry['metadata']))    
        self.assertEqual(metadata['vertices'], 36)

if __name__ == '__main__':
    unittest.main()