# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IGCSegmentImporterDialog
                                 A QGIS plugin
 This plugin imports an GPX file and creates short line segments between track points
                             -------------------
        begin                : 2017-12-01
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Simon Gröchenig @ Salzburg Research
        email                : simon.groechenig@salzburgresearch.at
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

import os

from qgis.PyQt import QtWidgets, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'igc_segment_importer_dialog_base.ui'))


class IGCSegmentImporterDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(IGCSegmentImporterDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
