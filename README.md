# IGC Segment Importer
QGIS Plugin

This repository contains the source code for the plugin.

This plugin base on Simon Gröchenig's work (https://github.com/SGroe/gpx-segment-importer)

## Overview

The IGC file is a tracking file developed by the Fédération Aéronautique Internationale (FAI)

![screenshot](img/screenshot.png)

## Features

* Available as QGIS dialog in toolbar and also as QGIS algorithm for usage in processing
* [dialog, algorithm] Read all attributes available from each track point at the segment start and/or end. This includes the timestamp and the elevation as well as any other attributes added to a track point.
* [dialog] Select one or multiple IGC files with the same data structure at once.
* [dialog] To gain full control over the data, you can edit the attribute table before creating the segment layer. You can exclude attributes, modify the attribute label and change the data type (integer, double, boolean or string) if the automatic type detection failed, e.g. at numeric data that contains “Null” or “None” values. Also, the plugin detects empty attributes and excludes it by default.
* [dialog, algorithm] Optionally calculate motion attributes (track points indices, distance, speed, duration and elevation_diff) between track points.
* [algorithm] Second algorithm 'Create track segments' to apply line segment creator to any point vector dataset that has a timestamp attribute.

## Use of plugin

The plugin is available in the QGIS plugin repository. Just open the plugin repository through the QGIS menu „Plugins” > „Manage and Install Plugins” and search for „IGC Importer“. Select it and press „Install plugin”.

The dialog is available in the toolbar 'IGC Segment Toolbar' or via the menu 'Plugins' - 'IGC Segment Tools'.

The algorithms 'Import IGC segments' and 'Create track segments' are available in the toolbox (group 'IGC Segment Importer').

## Notes
* By default, the attributes of the latter track point are used for the line segment
* Consecutive track points with equal coordinates are skipped in order to avoid creating single vertex linestrings
