

class ProviderFactory():

    ## Create all providers with the selected layers in the GUI
    def create_vector_providers(self, arrayLayer):
        for row_index in range(self.tw_layers.rowCount()):
            # if the layer is checked
            if self.tw_layers.item(row_index, 0).checkState() == QtCore.Qt.Checked:
                vectorLayer = self.tw_layers.item(row_index, 1).data(QtCore.Qt.UserRole)

                colorType = vectorLayer.rendererV2().type()
                columnColor = get_column_color(vectorLayer)
                layerColor = get_color(vectorLayer)
                srid = vectorLayer.crs().postgisSrid()
                info = vt_utils_parser.parse_vector(vectorLayer.source(), srid, colorType)
                column2 = self.tw_layers.cellWidget(row_index, 2).currentText()

                if column2 == "None":
                    vLayer = Layer(**info)
                    vLayer.add_color(columnColor, layerColor)
                    provider = PostgisProvider(vLayer)
                else:
                    info['column2'] = column2.split(" - ")[0]
                    info['typeColumn2'] = column2.split(" - ")[1]
                    vLayer = Layer(**info)
                    vLayer.add_color(columnColor, layerColor)
                    provider = PostgisProvider(vLayer)
                self.providerManager.add_vector_provider(provider)

    ## Create all providers for DEM and raster
    def create_raster_providers(self):
        dataSrcImg = None
        dataSrcMnt = None
        path = os.path.join(os.path.dirname(__file__), "rasters")
        extent = self.get_gui_extent()
        tileSize = self.get_size_tile()
        if self.has_dem():
            dem = self.cb_dem.itemData(self.cb_dem.currentIndex())
            demProvider = self.providerManager.create_raster_provider(dem, str(self.sb_port.value()), str(tileSize), self.zoomLevel)
            self.providerManager.dem = demProvider
            dataSrcMnt = demProvider.source
        if self.has_texture():
            texture = self.cb_texture.itemData(self.cb_texture.currentIndex())
            textureProvider = self.providerManager.create_raster_provider(texture, str(self.sb_port.value()), str(tileSize), self.zoomLevel)
            self.providerManager.texture = textureProvider
            dataSrcImg = textureProvider.source
        if self.has_raster():
            if os.name is 'nt':
                pythonPath = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
                mp.set_executable(pythonPath)
                sys.argv = [None]
            originExtent = Extent(extent[0], extent[1], extent[2], extent[3])
            self.queue = Queue()
            self.clear_rasters_directory(path)
            tiler = VTTiler(originExtent, tileSize, self.zoomLevel, dataSrcMnt, dataSrcImg)
            self.GDALprocess = mp.Process(target=tiler.create, args=(path, self.queue))
            self.GDALprocess.start()