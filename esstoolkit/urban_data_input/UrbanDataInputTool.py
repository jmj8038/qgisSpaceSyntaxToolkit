# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UrbanDataInput
                                 A QGIS plugin
 Urban Data Input Tool for QGIS
                              -------------------
        begin                : 2016-06-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Abhimanyu Acharya/(C) 2016 by Space Syntax Limited’.
        email                : a.acharya@spacesyntax.com
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from urban_data_input_dockwidget import UrbanDataInputDockWidget
from frontages import FrontageTool
from entrances import EntranceTool
from landuse import LanduseTool
 

class UrbanDataInputTool(QObject):
    # initialise class with self and iface
    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        # create the dialog objects
        self.dockwidget = UrbanDataInputDockWidget(self.iface)
        self.frontage_tool = FrontageTool(self.iface, self.dockwidget)
        self.entrance_tool = EntranceTool(self.iface, self.dockwidget)
        self.lu_tool = LanduseTool(self.iface, self.dockwidget)

        # connect to provide cleanup on closing of dockwidget
        self.dockwidget.closingPlugin.connect(self.unload_gui)

        # get current user settings
        self.user_settings = {}
        self.user_settings['crs'] = QSettings().value('/qgis/crs/use_project_crs')
        self.user_settings['attrib_dialog'] = QSettings().value('/qgis/digitizing/disable_enter_attribute_values_dialog')

    def load_gui(self):
        # Overide existing QGIS settings
        if not self.user_settings['attrib_dialog']:
            QSettings().setValue('/qgis/digitizing/disable_enter_attribute_values_dialog', True)
        if not self.user_settings['crs']:
            QSettings().setValue('/qgis/crs/use_project_crs', True)

        # show the dockwidget
        # TODO: fix to allow choice of dock location
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()

        # set up GUI operation signals
        # legend change connections
        self.iface.projectRead.connect(self.updateLayers)
        self.iface.newProjectCreated.connect(self.updateLayers)
        self.iface.legendInterface().itemRemoved.connect(self.updateLayers)
        self.iface.legendInterface().itemAdded.connect(self.updateLayers)
        # Frontages
        self.iface.mapCanvas().selectionChanged.connect(self.dockwidget.addDataFields)
        # Entrances
        self.iface.mapCanvas().selectionChanged.connect(self.dockwidget.addEntranceDataFields)
        # Landuse
        self.iface.mapCanvas().selectionChanged.connect(self.dockwidget.addLUDataFields)
        #Initialisation
        self.updateLayers()

    def unload_gui(self):
        #self.dockwidget.close()
        # disconnect interface signals
        try:
            # restore user settings
            QSettings().setValue('/qgis/digitizing/disable_enter_attribute_values_dialog', self.user_settings['attrib_dialog'])
            QSettings().setValue('/qgis/crs/use_project_crs', self.user_settings['crs'])

            # legend change connections
            self.iface.projectRead.disconnect(self.updateLayers)
            self.iface.newProjectCreated.disconnect(self.updateLayers)
            self.iface.legendInterface().itemRemoved.disconnect(self.updateLayers)
            self.iface.legendInterface().itemAdded.disconnect(self.updateLayers)
            # Frontages
            self.iface.mapCanvas().selectionChanged.disconnect(self.dockwidget.addDataFields)
            self.dockwidget.disconnectFrontageLayer()
            # Entrances
            self.iface.mapCanvas().selectionChanged.disconnect(self.dockwidget.addEntranceDataFields)
            self.dockwidget.disconnectEnranceLayer()
            # Landuse
            self.iface.mapCanvas().selectionChanged.disconnect(self.dockwidget.addLUDataFields)
            self.dockwidget.disconnectLULayer()
        except:
            pass

    def updateLayers(self):
        # frontages
        self.frontage_tool.updateLayers()
        self.frontage_tool.updateFrontageLayer()
        # this is not being used at the moment
        #self.frontage_tool.updateLayersPushID
        # entrances
        self.entrance_tool.updateEntranceLayer()
        # land use
        self.lu_tool.loadLULayer()
        self.lu_tool.updatebuildingLayers()
        self.lu_tool.updateLULayer()