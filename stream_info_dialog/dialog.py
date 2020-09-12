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
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout

from .node import StreamDirection
from .stream_info_group import StreamInfoGroup


class StreamInfoDialog(QDialog):

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin

        self.setWindowTitle('AES67 Audio Streams')
        self.setMinimumSize(800, 600)
        self.setLayout(QGridLayout())

        self._sources = StreamInfoGroup(self._plugin, StreamDirection.SOURCE)
        self.layout().addWidget(self._sources, 0, 0)

        self._sinks = StreamInfoGroup(self._plugin, StreamDirection.SINK)
        self.layout().addWidget(self._sinks, 0, 1)

        self._button_box = QDialogButtonBox(parent=self)
        self._button_box.addButton(QDialogButtonBox.Close)
        self._button_box.rejected.connect(self.reject)
        self.layout().addWidget(self._button_box, 1, 0, 1, 2)

    @property
    def sinks(self):
        return self._sinks

    @property
    def sources(self):
        return self._sources

    def open(self, *args, **kwargs):
        super().open(*args, **kwargs)
        self._plugin.poller.add_callback('streams', self.update_local_streams)
        self._plugin.poller.add_callback('remote_sources', self.update_remote_sources)

    def reject(self, *args, **kwargs):
        super().reject(*args, **kwargs)
        self._plugin.poller.remove_callback('streams', self.update_local_streams)
        self._plugin.poller.remove_callback('remote_sources', self.update_remote_sources)

    def update_local_streams(self, stream_definitions):
        self._sources.update_local_streams(stream_definitions['sources'])
        self._sinks.update_local_streams(stream_definitions['sinks'])

    def update_remote_sources(self, stream_definitions):
        self._sources.update_remote_streams(stream_definitions['remote_sources'])
