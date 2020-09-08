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

# pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

from .node import StreamDirection, StreamInfoNode


class StreamInfoModelTemplate(QAbstractItemModel):
    def __init__(self, direction):
        super().__init__()
        #self.root = ModelsRootNode(model=self)
        self._direction = direction
        self.children = []

    def __len__(self):
        return len(self.children)

    def addEntry(self):
        entry = StreamInfoNode(self, self._direction)

        rownum = self.__len__()
        self.beginInsertRows(QModelIndex(), rownum, rownum)
        self.children.append(entry)
        self.endInsertRows()

        return entry.index()

    def childCount(self, index):
        return 0 if index.isValid() else self.__len__()

    def columnCount(self, index):
        # pylint: disable=no-self-use, unused-argument
        return 1

    def data(self, index, role=Qt.DisplayRole):
        # pylint: disable=no-self-use
        if not index.isValid():
            return None
        return index.internalPointer().data(role)

    def setData(self, index, value, role):
        # pylint: disable=no-self-use
        if not index.isValid():
            return False
        return index.internalPointer().setData(value, role)

    def flags(self, index):
        # pylint: disable=no-self-use
        if not index.isValid():
            return Qt.NoItemFlags
        return index.internalPointer().flags

    def index(self, row_num, col_num, parent_idx):
        if not self.hasIndex(row_num, col_num, parent_idx):
            return QModelIndex()

        child_node = self.children[row_num]

        if child_node:
            return self.createIndex(row_num, col_num, child_node)
        return QModelIndex()

    def parent(self, index):
        # pylint: disable=no-self-use, unused-argument
        # No nodes have parents...
        return QModelIndex()

    def rowCount(self, index):
        return self.childCount(index)
