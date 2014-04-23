ViziTown
========

This QGIS plugin allows interactive 3D visualization on GIS datasets in a web browser.


Installation
============

Requirements:

- QGIS >= 2.0
- python-gdal
- a default web browser with webGL capability ([test here](http://get.webgl.org)

Download `vizitown.zip` and unzip it in your `.qgis2/python/plugins` directory.

Launch QGIS and, in the Plugin Manager, check that the plugin is loaded.


Architecture
============

ViziTown is a web server running within QGIS.

QGIS and the ViziTown window are used to configure and launch the server (based on [cyclone](http://cyclone.io/)).

A web client (your defaut web browser) is used to visualize and travel trough the 3D scene.


Restrictions
============

- All data must share the same coordinate system
- Raster data must be local
- DEM must have only one band, otherwise they won't be recognized as DEM
- Vector layers must come from a PostGIS database
- MULTIPOINT data are not supported
- Empty dataset are not supported

POLYHEDRALSURFACE need to be tessellated and this could be quite long. Preprocessing the data by adding a tessellated geometry field is advised. POLYHEDRALSURFACE can only be handled if PostGIS is compiled with SFCGAL support.


Tutorial
========

By default the current QGIS extend is used to generate the 3D scene. This extend can be changed in the `Extend` tab of the ViziTown window.

Adding a DEM and/or texture
---------------------------

Add your DEM/texture as a raster layer in QGIS. Open ViziTown and, in the `Layers` tab select the layer in the `DEM`/`texture` combo-box. Click on `Generate`. Your default web browser should open. 
You can explore the scene by using the mouse to change the camera orientation (click + move toward) and keyboard arrows to move around. 

Adding vector layers
--------------------

Create a connection to a PostGIS database, and add the vector layers in QGIS. Open ViziTown and, in the `Layers` tab, select the layers you want to display in 3D with hte check-boxes on the left.

To display 2D features, you can leave the `Field` column. If a DEM is present, 2D geometries will be draped on the relief.

2D polygons can be extruded by selecting the field from which the extrusion height must be read from in the column `Field`.

For 2D points and lines, and 3D features, the specified altitude is used to translate the features in the z direction.

Adding complex geometries
-------------------------

It is often useful to represent some features in great details. Those features can be stored in the form of a json text field of a POINT layer in the PostGIS database. 

Add the POINT layer in QGIS and select the json text field in ViziTown column `Field`.


Reporting bugs
==============

In case a problem occurs, please use github issue reporting facility and add the contend of the file `.qgis2/python/plugins/vizitown/GDAL_Process.err` to your bug report.


Credits
=======


License
=======








