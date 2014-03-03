# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Vizitown
                                 A QGIS plugin
 QGIS Plugin for viewing data in 3D
                              -------------------
        begin                : 2014-02-03
        copyright            : (C) 2014 by Cubee(ESIPE)
        email                : lp_vizitown@googlegroups.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import unittest
import json
from vt_utils_converter import PostgisToJSON

## Test postgisToJSON class if the conversion of an X3D formats into a json operates
class translateJSON(unittest.TestCase):

    def setUp(self):
        self.oneSimplePoint = ["844134.284462888841517 6516568.605687109753489 0"]
        self.twoPointsHeight = [["844134.284462888841517 6516568.605687109753489 0", "10"], ["144134.284462888841517 6516568.605687109753489 0", "25"]]

        self.lineSimple = ["<IndexedLineSet  coordIndex='0 1 2 3 4'><Coordinate point='847423.133840369875543 6519126.773986855521798 0 847427.16084886121098 6519029.311356557533145 0 847431.001942750066519 6518961.135681151412427 0 847435.155744896968827 6518878.69126517791301 0 847435.500586390029639 6518853.990726242773235 0 ' /></IndexedLineSet>"]
        self.lineWithHeight = [["<IndexedLineSet  coordIndex='0 1 2 3 4'><Coordinate point='847423.133840369875543 6519126.773986855521798 0 847427.16084886121098 6519029.311356557533145 0 847431.001942750066519 6518961.135681151412427 0 847435.155744896968827 6518878.69126517791301 0 847435.500586390029639 6518853.990726242773235 0 ' /></IndexedLineSet>", "10"]]

        self.polygon = ['{"type":"Polygon","coordinates":[[[852321.383846897,6509501.96687314,0],[852320.082282889,6509513.99731137,0],[852322.110674802,6509514.19758986,0],[852322.79144221,6509508.14240802,0],[852323.452207997,6509502.16716017,0],[852321.383846897,6509501.96687314,0]]]}']
        self.multipolygon = ['{"type":"MultiPolygon", "coordinates": [[[[30, 20, 0], [45, 40, 0], [10, 40, 0], [30, 20, 0]]], [[[15, 5, 0], [40, 10, 0], [10, 20, 0], [5, 10, 0], [15, 5, 0]]]]}']

        self.tin = ["<IndexedTriangleSet  index='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35'><Coordinate point='852320.082282889052294 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 0 852323.452207996975631 6509501.966873140074313 11 852320.082282889052294 6509501.966873140074313 11 852320.082282889052294 6509501.966873140074313 0 852323.452207996975631 6509501.966873140074313 0 852320.082282889052294 6509514.19758986029774 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509514.19758986029774 11 852320.082282889052294 6509514.19758986029774 11 852320.082282889052294 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509501.966873140074313 0 852323.452207996975631 6509514.19758986029774 0 852323.452207996975631 6509514.19758986029774 11 852323.452207996975631 6509501.966873140074313 11 852323.452207996975631 6509514.19758986029774 0 852320.082282889052294 6509501.966873140074313 0 852320.082282889052294 6509501.966873140074313 11 852320.082282889052294 6509514.19758986029774 11 852320.082282889052294 6509514.19758986029774 0 852320.082282889052294 6509501.966873140074313 0 852320.082282889052294 6509514.19758986029774 11 852320.082282889052294 6509514.19758986029774 0 852320.082282889052294 6509514.19758986029774 11 852323.452207996975631 6509514.19758986029774 11 852323.452207996975631 6509514.19758986029774 0 852320.082282889052294 6509514.19758986029774 0 852323.452207996975631 6509514.19758986029774 11 852320.082282889052294 6509501.966873140074313 0 852320.082282889052294 6509514.19758986029774 0 852323.452207996975631 6509514.19758986029774 0 852323.452207996975631 6509501.966873140074313 0 852320.082282889052294 6509501.966873140074313 0 852323.452207996975631 6509514.19758986029774 0'/></IndexedTriangleSet>"]

        self.hasHeight = True
        self.noHeight = False

        self.colors = "#000000"

        self.geomPoint = 'POINT'
        self.geomLine = 'LINESTRING'
        self.geomPolyg = 'POLYGON'
        self.geomMPolyg = 'MULTIPOLYGON'
        self.geomPolyh = 'POLYHEDRALSURFACE'

        self.translator = PostgisToJSON()

    # ONE POINT NO HEIGHT
    def test_json_one_point_check_type(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight, self.colors, "demo")
        jsonOnePoint = json.loads(ret)
        self.assertEqual(jsonOnePoint['dim'], "2")

    def test_json_one_pont_check_nb_geometry(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight, self.colors, "demo")
        jsonOnePoint = json.loads(ret)
        geometries = jsonOnePoint['geometries']
        self.assertEqual(len(geometries), 1)

    def test_json_one_point_check_coordinates(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight, self.colors, "demo")
        jsonOnePoint = json.loads(ret)
        geometries = jsonOnePoint['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [844134.284462888841517, 6516568.605687109753489])

    def test_json_one_point_check_height(self):
        ret = self.translator.parse(self.oneSimplePoint, self.geomPoint, self.noHeight, self.colors, "demo")
        jsonOnePoint = json.loads(ret)
        geometries = jsonOnePoint['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # TWO POINTS WITH HEIGHT
    def test_json_two_points_check_type(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight, self.colors, "demo")
        jsonTwoPoints = json.loads(ret)
        self.assertEqual(jsonTwoPoints['dim'], "2.5")

    def test_json_two_points_check_nb_geometry(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight, self.colors, "demo")
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries']
        self.assertEqual(len(geometries), 2)

    def test_json_two_points_check_coordinates_point1(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight, self.colors, "demo")
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [844134.284462888841517, 6516568.605687109753489])

    def test_json_two_points_check_coordinates_point2(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight, self.colors, "demo")
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][1]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [144134.284462888841517, 6516568.605687109753489])

    def test_json_two_points_check_height_point1(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight, self.colors, "demo")
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 10)

    def test_json_two_points_check_height_point2(self):
        ret = self.translator.parse(self.twoPointsHeight, self.geomPoint, self.hasHeight, self.colors, "demo")
        jsonTwoPoints = json.loads(ret)
        geometries = jsonTwoPoints['geometries'][1]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 25)

    # LINE
    def test_json_line_check_type(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        self.assertEqual(jsonLine['dim'], "2")

    def test_json_line_check_nb_geometry(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        self.assertEqual(len(jsonLine['geometries']), 1)

    def test_json_line_check_coordinates(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [847423.133840369875543,6519126.773986855521798,847427.16084886121098,6519029.311356557533145,847431.001942750066519,6518961.135681151412427,847435.155744896968827,6518878.69126517791301,847435.500586390029639,6518853.990726242773235])

    def test_json_line_check_height(self):
        ret = self.translator.parse(self.lineSimple, self.geomLine, self.noHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # LINE WITH HEIGHT
    def test_json_lineH_check_type(self):
        ret = self.translator.parse(self.lineWithHeight, self.geomLine, self.hasHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        self.assertEqual(jsonLine['dim'], "2.5")

    def test_json_lineH_check_coordinates(self):
        ret = self.translator.parse(self.lineWithHeight, self.geomLine, self.hasHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [847423.133840369875543,6519126.773986855521798,847427.16084886121098,6519029.311356557533145,847431.001942750066519,6518961.135681151412427,847435.155744896968827,6518878.69126517791301,847435.500586390029639,6518853.990726242773235])


    def test_json_lineH_check_height(self):
        ret = self.translator.parse(self.lineWithHeight, self.geomLine, self.hasHeight, self.colors, "demo")
        jsonLine = json.loads(ret)
        geometries = jsonLine['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 10)

    # POLYGONE
    def test_json_polygon_check_type(self):
        ret = self.translator.parse(self.polygon, self.geomPolyg, self.noHeight, self.colors, "demo")
        jsonPoly = json.loads(ret)
        self.assertEqual(jsonPoly['dim'], "2")

    def test_json_polygon_check_coordinates(self):
        ret = self.translator.parse(self.polygon, self.geomPolyg, self.noHeight, self.colors, "demo")
        jsonPoly = json.loads(ret)
        geometries = jsonPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [852321.383847,6509501.96687,852320.082283,6509513.99731,852322.110675,6509514.19759,852322.791442,6509508.14241,852323.452208,6509502.16716,852321.383847,6509501.96687])

    def test_json_polygon_check_height(self):
        ret = self.translator.parse(self.polygon, self.geomPolyg, self.noHeight, self.colors, "demo")
        jsonPoly = json.loads(ret)
        geometries = jsonPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # MULTIPOLYGON
    def test_json_multipolygon_check_type(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight, self.colors, "demo")
        jsonMPoly = json.loads(ret)
        self.assertEqual(jsonMPoly['dim'], "2")

    def test_json_two_points_check_nb_geometry(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight, self.colors, "demo")
        jsonMPoly = json.loads(ret)
        geometries = jsonMPoly['geometries']
        self.assertEqual(len(geometries), 2)

    def test_json_multipolygon_check_coordinates_poly1(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight, self.colors, "demo")
        jsonMPoly = json.loads(ret)
        geometries = jsonMPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [30, 20, 45, 40, 10, 40, 30, 20])

    def test_json_multipolygon_check_coordinates_poly2(self):
        ret = self.translator.parse(self.multipolygon, self.geomMPolyg, self.noHeight, self.colors, "demo")
        jsonMPoly = json.loads(ret)
        geometries = jsonMPoly['geometries'][1]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['coordinates'], [15, 5, 40, 10, 10, 20, 5, 10, 15, 5])

    def test_json_multipolygon_check_height(self):
        ret = self.translator.parse(self.polygon, self.geomMPolyg, self.noHeight, self.colors, "demo")
        jsonPoly = json.loads(ret)
        geometries = jsonPoly['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        self.assertEqual(geometry['height'], 0)

    # TIN
    def test_json_tin_check_type(self):
        ret = self.translator.parse(self.tin, self.geomPolyh, self.noHeight, self.colors, "demo")
        jsonPolyh = json.loads(ret)
        self.assertEqual(jsonPolyh['dim'], "3")

    def test_json_tin_check_nb_faces(self):
        ret = self.translator.parse(self.tin, self.geomPolyh, self.noHeight, self.colors, "demo")
        jsonPolyh = json.loads(ret)
        geometries = jsonPolyh['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        metadata = json.loads(json.dumps(geometry['metadata']))    
        self.assertEqual(metadata['faces'], 12)
 
    def test_json_tin_check_nb_vertices(self):
        ret = self.translator.parse(self.tin, self.geomPolyh, self.noHeight, self.colors, "demo")
        jsonPolyh = json.loads(ret)
        geometries = jsonPolyh['geometries'][0]
        js = json.dumps(geometries)
        geometry = json.loads(js)
        metadata = json.loads(json.dumps(geometry['metadata']))    
        self.assertEqual(metadata['vertices'], 36)

if __name__ == '__main__':
    unittest.main()