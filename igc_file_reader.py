# Initialize Qt resources from file resources.py
from xml.etree import ElementTree
from qgis.core import (QgsPoint, QgsCoordinateReferenceSystem)
from .datatype_definition import (DataTypeDefinition, DataTypes)
from .igc_feature_builder import IGCFeatureBuilder
from .geom_tools import GeomTools
import os


class IGCFileReader:
    """ Reads IGC files and assembles vector layers """

    def __init__(self):
        self.attribute_definitions = list()
        self.namespace = None
        self.error_message = ''
        self.track_count = 0
        self.track_segment_count = 0
        self.track_point_count = 0
        self.equal_coordinates = 0

    def parse_b_record(self, b_record):
        """
        https://xp-soaring.github.io/igc_file_format/igc_format_2008.html#link_B
        """

        definitions = []

        # https://xp-soaring.github.io/igc_file_format/igc_format_2008.html#link_FXA
        # only the first 35 bytes are recognized
        if b_record[0] != "B" or len(b_record) < 36: # 35 + \n
            # not a b record
            return None
        time_utc = b_record[1:7]
        latitude_str = b_record[7:15-1] # last is N for north / S for Sud
        latitude_sign = b_record[14]
        latitude = float(latitude_str[0:2]) + (float(latitude_str[2:4]) + float(latitude_str[4:7]) / 1000) / 60
        if latitude_sign == "S":
            latitude *= -1
        longitude_str = b_record[15:24-1] # last is E for East/ W for West
        longitude_sign = b_record[23]
        longitude = float(longitude_str[0:3]) + (float(longitude_str[3:5]) + float(longitude_str[5:8]) / 1000) / 60
        if longitude_sign == "W":
            longitude *= -1
        fix_validity = b_record[24]
        press_alt = int(b_record[25:30])
        gnss_alt = int(b_record[30:35])

        return {"time_utc": time_utc, 
                "lat": latitude, 
                "lon":longitude, 
                "fix_validity":fix_validity, 
                "press_alt":press_alt, 
                "gnss_alt":gnss_alt}



    def get_table_data(self, file_path):
        """ Reads the first B record and create datatype definitions from the available attributes """

        self.attribute_definitions = list()
        self.error_message = ''

        # find first B record
        with open(file_path) as f:
            for line in f:
                if len(line) > 0 and line[0] == "B":
                    # B record
                    b_record = self.parse_b_record(line)
                    if self.attribute_definitions is not None and b_record is not None:
                        self.attribute_definitions.append(DataTypeDefinition("time_utc", DataTypes.Integer, True,b_record["time_utc"]))
                        self.attribute_definitions.append(DataTypeDefinition("lat",DataTypes.Double,True, b_record["lat"]))
                        self.attribute_definitions.append(DataTypeDefinition("lon",DataTypes.Double,True,b_record["lon"]))
                        self.attribute_definitions.append(DataTypeDefinition("fix_validity",DataTypes.String,True,b_record["fix_validity"]))
                        self.attribute_definitions.append(DataTypeDefinition("press_alt",DataTypes.Integer,True, b_record["press_alt"]))
                        self.attribute_definitions.append(DataTypeDefinition("gnss_alt",DataTypes.Integer,True,b_record["gnss_alt"]))
                        return True

        self.error_message = 'No B record found.'
        return False

    def import_igc_file(self, file_path, output_directory, attribute_select="Last", use_wgs84=True,
                        calculate_motion_attributes=False, overwrite=False):
        """ Imports the data from the IGC file and create the vector layer """

        if len(self.attribute_definitions) == 0:
            self.get_table_data(file_path)

        self.error_message = ''

        if calculate_motion_attributes:
            self.attribute_definitions.append(DataTypeDefinition('_a_index', DataTypes.Integer, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_b_index', DataTypes.Integer, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_distance', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_duration', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_speed', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_elevation_diff', DataTypes.Double, True, ''))

        crs = QgsCoordinateReferenceSystem('EPSG:4326') if use_wgs84 else None

        vector_layer_builder = IGCFeatureBuilder(os.path.basename(file_path), self.attribute_definitions,
                                                 attribute_select, crs)

        self.equal_coordinates = 0
        self.track_point_count = 0

        with open(file_path) as f:
            prev_track_point = None
            prev_track_point_index = -1
            for line in f:
                track_point = self.parse_b_record(line)
                if track_point is None:
                    continue

                self.track_count += 1   

                if prev_track_point is not None:
                    elevation_a_element = prev_track_point["gnss_alt"]
                    elevation_b_element = track_point["gnss_alt"]
                    elevation_a = prev_track_point["gnss_alt"]
                    elevation_b = track_point["gnss_alt"]

                    previous_point = QgsPoint(
                        float(prev_track_point["lon"]),
                        float(prev_track_point["lat"]),
                        elevation_a if (elevation_a is not None) else None
                    )
                    new_point = QgsPoint(
                        float(track_point["lon"]),
                        float(track_point["lat"]),
                        elevation_b if (elevation_b is not None) else None
                    )

                    if GeomTools.is_equal_coordinate(previous_point, new_point):
                        self.equal_coordinates += 1
                        continue

                    # add a feature with first/last/both attributes
                    attributes = dict()
                    if attribute_select == 'First':
                        self.add_attributes(attributes, prev_track_point, '')
                    elif attribute_select == 'Last':
                        self.add_attributes(attributes, track_point, '')
                    elif attribute_select == 'Both':
                        self.add_attributes(attributes, prev_track_point, 'a_')
                        self.add_attributes(attributes, track_point, 'b_')

                    if calculate_motion_attributes:
                        attributes['_a_index'] = prev_track_point_index
                        attributes['_b_index'] = self.track_point_count - 1
                        attributes['_distance'] = GeomTools.distance(previous_point, new_point, crs)

                        time_a = DataTypes.create_date(prev_track_point["time_utc"], "%H%M%S")
                        time_b = DataTypes.create_date(track_point["time_utc"], "%H%M%S")

                        if time_a is not None or time_b is not None:
                            attributes['_duration'] = GeomTools.calculate_duration(time_a, time_b)
                            attributes['_speed'] = GeomTools.calculate_speed(time_a, time_b, previous_point,
                                                                                new_point, crs)

                        if elevation_a is not None or elevation_b is not None:
                            attributes['_elevation_diff'] = elevation_b - elevation_a

                    vector_layer_builder.add_feature([previous_point, new_point], attributes)

                prev_track_point = track_point
                prev_track_point_index = self.track_point_count - 1 

        vector_layer = vector_layer_builder.save_layer(output_directory, overwrite)
        if vector_layer_builder.error_message != '':
            self.error_message = vector_layer_builder.error_message
            print(self.error_message)

        return vector_layer

    def add_attributes(self, attributes, element, key_prefix):
        """ Reads and adds attributes to the feature """

        for key in element:
            attribute = self._get_attribute_definition(key)
            if attribute is None:
                continue

            if attribute.datatype is DataTypes.Integer and DataTypes.value_is_int(attribute.example_value) or \
                attribute.datatype is DataTypes.Double and \
                DataTypes.value_is_double(attribute.example_value) or \
                attribute.datatype is DataTypes.String:
                attributes[key_prefix + attribute.attribute_key_modified] = element[key]

    def _get_attribute_definition(self, key):
        for attribute in self.attribute_definitions:
            if key == attribute.attribute_key:
                return attribute
        return None

    @staticmethod
    def normalize(name):
        if name[0] == '{':
            uri, tag = name[1:].split('}')
            return tag
        else:
            return name
