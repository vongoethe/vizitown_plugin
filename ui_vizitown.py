# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_vizitown.ui'
#
# Created: Mon Feb 10 16:56:28 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Vizitown(object):
    def setupUi(self, Vizitown):
        Vizitown.setObjectName(_fromUtf8("Vizitown"))
        Vizitown.setEnabled(True)
        Vizitown.resize(477, 579)
        Vizitown.setMinimumSize(QtCore.QSize(477, 579))
        Vizitown.setMaximumSize(QtCore.QSize(477, 579))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("vt.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Vizitown.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(Vizitown)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(Vizitown)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.Layers = QtGui.QWidget()
        self.Layers.setObjectName(_fromUtf8("Layers"))
        self.gridLayout_2 = QtGui.QGridLayout(self.Layers)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.Layers)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cb_MNT = QtGui.QComboBox(self.groupBox)
        self.cb_MNT.setObjectName(_fromUtf8("cb_MNT"))
        self.horizontalLayout.addWidget(self.cb_MNT)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.Layers)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.listWidget_Left = QtGui.QListWidget(self.groupBox_3)
        self.listWidget_Left.setObjectName(_fromUtf8("listWidget_Left"))
        self.gridLayout_3.addWidget(self.listWidget_Left, 0, 0, 1, 1)
        self.listWidget_Right = QtGui.QListWidget(self.groupBox_3)
        self.listWidget_Right.setObjectName(_fromUtf8("listWidget_Right"))
        self.gridLayout_3.addWidget(self.listWidget_Right, 0, 5, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.but_Add = QtGui.QPushButton(self.groupBox_3)
        self.but_Add.setObjectName(_fromUtf8("but_Add"))
        self.verticalLayout.addWidget(self.but_Add)
        self.but_Supp = QtGui.QPushButton(self.groupBox_3)
        self.but_Supp.setObjectName(_fromUtf8("but_Supp"))
        self.verticalLayout.addWidget(self.but_Supp)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 3, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.Layers)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.cb_Raster = QtGui.QComboBox(self.groupBox_2)
        self.cb_Raster.setObjectName(_fromUtf8("cb_Raster"))
        self.horizontalLayout_2.addWidget(self.cb_Raster)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.tabWidget.addTab(self.Layers, _fromUtf8(""))
        self.Opt = QtGui.QWidget()
        self.Opt.setObjectName(_fromUtf8("Opt"))
        self.gridLayout_4 = QtGui.QGridLayout(self.Opt)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem, 3, 0, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(self.Opt)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_7 = QtGui.QLabel(self.groupBox_4)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_3.addWidget(self.label_7)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.Numero_Port = QtGui.QLineEdit(self.groupBox_4)
        self.Numero_Port.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Numero_Port.setObjectName(_fromUtf8("Numero_Port"))
        self.horizontalLayout_3.addWidget(self.Numero_Port)
        self.gridLayout_4.addWidget(self.groupBox_4, 0, 0, 1, 1)
        self.groupBox_5 = QtGui.QGroupBox(self.Opt)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_8 = QtGui.QLabel(self.groupBox_5)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_4.addWidget(self.label_8)
        self.cb_tuile = QtGui.QComboBox(self.groupBox_5)
        self.cb_tuile.setObjectName(_fromUtf8("cb_tuile"))
        self.horizontalLayout_4.addWidget(self.cb_tuile)
        self.gridLayout_4.addWidget(self.groupBox_5, 1, 0, 1, 1)
        self.but_defaut = QtGui.QPushButton(self.Opt)
        self.but_defaut.setObjectName(_fromUtf8("but_defaut"))
        self.gridLayout_4.addWidget(self.but_defaut, 2, 0, 1, 1)
        self.tabWidget.addTab(self.Opt, _fromUtf8(""))
        self.extent = QtGui.QWidget()
        self.extent.setObjectName(_fromUtf8("extent"))
        self.gridLayout_6 = QtGui.QGridLayout(self.extent)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_11 = QtGui.QLabel(self.extent)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_6.addWidget(self.label_11, 2, 2, 1, 1)
        self.label_13 = QtGui.QLabel(self.extent)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_6.addWidget(self.label_13, 2, 5, 1, 1)
        self.label_12 = QtGui.QLabel(self.extent)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_6.addWidget(self.label_12, 4, 3, 1, 1)
        self.Ymax = QtGui.QLineEdit(self.extent)
        self.Ymax.setText(_fromUtf8(""))
        self.Ymax.setObjectName(_fromUtf8("Ymax"))
        self.gridLayout_6.addWidget(self.Ymax, 1, 3, 1, 1)
        self.Xmax = QtGui.QLineEdit(self.extent)
        self.Xmax.setText(_fromUtf8(""))
        self.Xmax.setObjectName(_fromUtf8("Xmax"))
        self.gridLayout_6.addWidget(self.Xmax, 3, 5, 1, 1)
        self.label_14 = QtGui.QLabel(self.extent)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_6.addWidget(self.label_14, 0, 3, 1, 1)
        self.Ymin = QtGui.QLineEdit(self.extent)
        self.Ymin.setText(_fromUtf8(""))
        self.Ymin.setObjectName(_fromUtf8("Ymin"))
        self.gridLayout_6.addWidget(self.Ymin, 5, 3, 1, 1)
        self.Xmin = QtGui.QLineEdit(self.extent)
        self.Xmin.setText(_fromUtf8(""))
        self.Xmin.setObjectName(_fromUtf8("Xmin"))
        self.gridLayout_6.addWidget(self.Xmin, 3, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_6.addItem(spacerItem2, 6, 3, 1, 1)
        self.tabWidget.addTab(self.extent, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.btnGenerate = QtGui.QPushButton(Vizitown)
        self.btnGenerate.setObjectName(_fromUtf8("btnGenerate"))
        self.gridLayout.addWidget(self.btnGenerate, 1, 0, 1, 1)

        self.retranslateUi(Vizitown)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Vizitown)

    def retranslateUi(self, Vizitown):
        Vizitown.setWindowTitle(_translate("Vizitown", "Vizitown", None))
        self.groupBox.setTitle(_translate("Vizitown", "DEM", None))
        self.groupBox_3.setTitle(_translate("Vizitown", "Vector layer", None))
        self.but_Add.setText(_translate("Vizitown", "Add >>", None))
        self.but_Supp.setText(_translate("Vizitown", "Remove <<", None))
        self.groupBox_2.setTitle(_translate("Vizitown", "Ortho", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Layers), _translate("Vizitown", "Layers", None))
        self.groupBox_4.setTitle(_translate("Vizitown", "Server", None))
        self.label_7.setText(_translate("Vizitown", "Port number", None))
        self.Numero_Port.setText(_translate("Vizitown", "1042", None))
        self.groupBox_5.setTitle(_translate("Vizitown", "Scene", None))
        self.label_8.setText(_translate("Vizitown", "Tile size", None))
        self.but_defaut.setText(_translate("Vizitown", "Par defaut", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Opt), _translate("Vizitown", "Preferences", None))
        self.label_11.setText(_translate("Vizitown", "Xmin", None))
        self.label_13.setText(_translate("Vizitown", "Xmax", None))
        self.label_12.setText(_translate("Vizitown", "Ymin", None))
        self.label_14.setText(_translate("Vizitown", "Ymax", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.extent), _translate("Vizitown", "Extent", None))
        self.btnGenerate.setText(_translate("Vizitown", "Generate", None))

