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

import re

# pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

from .node import StreamDataRole, StreamDirection, StreamInfoNode


class StreamInfoModelTemplate(QAbstractItemModel):
    def __init__(self, plugin, direction):
        super().__init__()
        self._plugin = plugin
        self._direction = direction
        self._children_ids = []
        self.children = []

    def __iter__(self):
        for child in self.children:
            yield child

    def __len__(self):
        return len(self.children)

    def _add_node(self, stream_id, definition):
        node = StreamInfoNode(self, self._direction)
        self._amend_node(node, definition)

        self._children_ids.append(stream_id)
        self.children.append(node)

        return node

    def _amend_node(self, node, definition):
        node.setData(definition, StreamDataRole.RAW)
        node.setData(definition['name'], StreamDataRole.NAME)

        if 'sdp' in definition:
            # Local sources don't have this key (initially),
            # but they do when seen through the "remote sources" api
            node.setData(definition['sdp'], StreamDataRole.SDP)

        ch_count = 0
        if 'map' in definition:
            # Sinks, and Local Sources
            ch_count = len(definition['map'])
        else:
            # Remote Sources
            ch_count = int(re.search(r'a=rtpmap.*/(.*)\n', definition['sdp']).group(1))
        node.setData(ch_count, StreamDataRole.CH_COUNT)

    def _update_node(self, stream_id, definition):
        if stream_id not in self._children_ids:
            return
        idx = self._children_ids.index(stream_id)
        self._amend_node(self.children[idx], definition)

    def _cull_old_streams(self, old_streams, cull_local):
        for stream_id in old_streams:
            if isinstance(stream_id, int) ^ cull_local:
                # IDs of local streams have an integer ID
                # If we're culling local streams, we don't wish to skip this id
                # It we're culling remote streams, we do wish to skip this id
                continue

            idx = self._children_ids.index(stream_id)
            self.beginRemoveRows(QModelIndex(), idx, idx)
            del self._children_ids[idx]
            del self.children[idx]
            self.endRemoveRows()

    def updateStreamsFromDaemon(self, streams):
        if not streams:
            return

        old_streams = list(self._children_ids)

        rownum = self.__len__()
        self.beginInsertRows(QModelIndex(), rownum, rownum)
        for definition in streams:
            stream_id = definition['id']

            if stream_id in self._children_ids:
                self._update_node(stream_id, definition)
                old_streams.remove(stream_id)
            else:
                self._add_node(stream_id, definition)
        self.endInsertRows()

        if old_streams:
            self._cull_old_streams(old_streams, True)

    def updateRemoteSourcesFromDaemon(self, sources):
        if self._direction != StreamDirection.SOURCE or not sources:
            return
        sources = sources['remote_sources']
        daemon_name = self._plugin.daemon_name
        old_streams = list(self._children_ids)

        rownum = self.__len__()
        self.beginInsertRows(QModelIndex(), rownum, rownum)
        for definition in sources:

            # If this source is, in fact, a local one
            if definition['address'] == self._plugin.ip:
                for source in self.children:
                    candidate_name = f"{daemon_name} {source.data(StreamDataRole.NAME)}"
                    if candidate_name == definition['name']:
                        source.setData(definition['sdp'], StreamDataRole.SDP)
                        break
                continue

            source_id = definition['id']
            if source_id in self._children_ids:
                self._update_node(source_id, definition)
            else:
                node = self._add_node(source_id, definition)
                node.setData(False, StreamDataRole.IS_LOCAL)

        self.endInsertRows()

        if old_streams:
            self._cull_old_streams(old_streams, False)

    def localStreamIds(self):
        if self._direction == StreamDirection.SINK:
            return self._children_ids

        ids = []
        for stream_id in self._children_ids:
            if isinstance(stream_id, int):
                ids.append(stream_id)
        return ids

    def streamId(self, index):
        if not index.isValid():
            return None
        return self._children_ids[self.children.index(index.internalPointer())]

    def streamIds(self):
        return self._children_ids

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
