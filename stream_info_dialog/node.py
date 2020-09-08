# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2020 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2020 s0600204
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=missing-docstring

import enum

# pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt, QModelIndex, QSize


class StreamDirection(enum.Enum):
    SOURCE = enum.auto()
    SINK = enum.auto()

class StreamDataRole(enum.Enum):
    _userdatarole = Qt.DisplayRole + Qt.UserRole
    TYPE = _userdatarole + 1
    IDEN = _userdatarole + 2
    NAME = _userdatarole + 3
    CH_COUNT = _userdatarole + 4

class StreamInfoNode:
    _size = QSize(128, 48)

    def __init__(self, model, direction):
        self._direction = direction
        self._model = model
        self.flags = Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemNeverHasChildren) # Qt.ItemIsSelectable | 

    def data(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.rownum()
        if role == Qt.SizeHintRole:
            return self._size
        return None

    def index(self):
        return self.model().createIndex(self.rownum(), 0, self)

    def model(self):
        return self._model

    def next_sibling(self):
        if self.rownum() < len(self.parent) - 1:
            return self._model.children[self.rownum() + 1]
        return None

    def parent(self):
        return QModelIndex()

    def prev_sibling(self):
        if self.rownum():
            return self._model.children[self.rownum() - 1]
        return None

    def rownum(self):
        return self._model.children.index(self)

    def setData(self, value, role):
        # pylint: disable=unused-argument, no-self-use
        return False
