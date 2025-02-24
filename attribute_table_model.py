import operator
from qgis.PyQt.QtCore import Qt, QAbstractTableModel
from .datatype_definition import DataTypes


class AttributeTableModel(QAbstractTableModel):
    """ Data model for the attribute table """

    def __init__(self, data_in, header_data, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        # QAbstractTableModel.__init__(self, parent, *args)
        super(AttributeTableModel, self).__init__()
        self._array_data = data_in
        self._header_data = header_data

    def rowCount(self, parent=None, *args):
        return len(self._array_data)

    def columnCount(self, parent=None, *args):
        return 4

    def headerData(self, column, orientation, role=None):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._header_data[column]
        # return ""
        return QAbstractTableModel.headerData(self, column, orientation, role)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return ""
        elif role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return self._array_data[index.row()].attribute_key_modified
            elif index.column() == 2:
                return self._array_data[index.row()].datatype
            elif index.column() == 3:
                return self._array_data[index.row()].example_value
        elif role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                if self._array_data[index.row()].selected:
                    return Qt.CheckState.Checked
                else:
                    return Qt.CheckState.Unchecked
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return ""
        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                self._array_data[index.row()].attribute_key_modified = value
            elif index.column() == 2:
                self._array_data[index.row()].datatype = DataTypes.parse(value)
        elif role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                if value == Qt.CheckState.Checked:
                    self._array_data[index.row()].selected = True
                else:
                    self._array_data[index.row()].selected = False
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        elif index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable
        elif index.column() == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        elif index.column() == 2:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        return QAbstractTableModel.flags(self, index) | Qt.ItemFlag.NoItemFlags
